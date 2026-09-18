"""抓取：字段方案模板 + 抓取任务。"""
from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.deps import get_current_user, get_db
from ...models import (FETCHABLE_FIELDS, Account, Article, FetchProfile,
                       FetchTask, TaskStatus, User)
from ...schemas.fetch import (FetchProfileIn, FetchProfileOut, FetchTaskCreate,
                              FetchTaskOut)
from ...services.fetch_service import run_article_download, run_fetch_task
from ...tasks.queue import manager

router = APIRouter(prefix="/fetch", tags=["fetch"])

FIELD_LABELS = {
    "title": "标题", "publish_time": "发布时间", "content": "正文",
    "read_num": "阅读量", "like_num": "点赞", "wow_num": "在看",
    "share_num": "转发", "collect_num": "收藏", "comment": "评论",
}


@router.get("/fields")
def fetchable_fields(user: User = Depends(get_current_user)):
    return [{"value": f, "label": FIELD_LABELS.get(f, f)} for f in FETCHABLE_FIELDS]


# ---------- 抓取方案模板 ----------
@router.get("/profiles", response_model=list[FetchProfileOut])
def list_profiles(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return [FetchProfileOut.model_validate(p)
            for p in db.query(FetchProfile).order_by(FetchProfile.id.desc()).all()]


@router.post("/profiles", response_model=FetchProfileOut, status_code=status.HTTP_201_CREATED)
def create_profile(req: FetchProfileIn, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    p = FetchProfile(name=req.name, fields=req.fields, owner_id=user.id)
    db.add(p)
    db.commit()
    db.refresh(p)
    return FetchProfileOut.model_validate(p)


@router.delete("/profiles/{profile_id}")
def delete_profile(profile_id: int, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    p = db.get(FetchProfile, profile_id)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "方案不存在")
    db.delete(p)
    db.commit()
    return {"ok": True}


# ---------- 抓取任务 ----------
@router.post("/tasks", response_model=FetchTaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(req: FetchTaskCreate, db: Session = Depends(get_db),
                      user: User = Depends(get_current_user)):
    # 分组 → 账号 展开（与手选账号取并集），快照到任务
    account_ids = set(req.account_ids or [])
    if req.group_ids:
        rows = db.query(Account.id).filter(Account.group_id.in_(req.group_ids),
                                           Account.is_system.is_(False)).all()
        account_ids.update(r[0] for r in rows)
    article_ids = sorted({i for i in (req.article_ids or [])})
    if not account_ids and not article_ids:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "请至少选择一个公众号、分组或文章")
    if not req.fields:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "请至少选择一个抓取字段")
    if article_ids:
        # 按文章补抓：确认文章存在
        exist = {r[0] for r in db.query(Article.id).filter(Article.id.in_(article_ids)).all()}
        article_ids = [i for i in article_ids if i in exist]
        if not article_ids:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "所选文章不存在")
    task = FetchTask(owner_id=user.id, account_ids=sorted(account_ids),
                     group_ids=req.group_ids or [],
                     article_ids=article_ids,
                     time_start=req.time_start, time_end=req.time_end,
                     fields=req.fields, key_id=req.key_id, status=TaskStatus.pending)
    db.add(task)
    db.commit()
    db.refresh(task)
    # 后台执行：给了文章清单走逐篇补抓，否则走公众号扫描
    runner = run_article_download if article_ids else run_fetch_task
    manager.start(f"fetch:{task.id}", lambda cancel: runner(task.id, cancel))
    return FetchTaskOut.model_validate(task)


@router.get("/tasks", response_model=list[FetchTaskOut])
def list_tasks(limit: int = 50, db: Session = Depends(get_db),
               user: User = Depends(get_current_user)):
    tasks = db.query(FetchTask).order_by(FetchTask.id.desc()).limit(limit).all()
    return [FetchTaskOut.model_validate(t) for t in tasks]


@router.get("/tasks/{task_id}", response_model=FetchTaskOut)
def get_task(task_id: int, db: Session = Depends(get_db),
             user: User = Depends(get_current_user)):
    task = db.get(FetchTask, task_id)
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "任务不存在")
    return FetchTaskOut.model_validate(task)


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: int, db: Session = Depends(get_db),
                      user: User = Depends(get_current_user)):
    task = db.get(FetchTask, task_id)
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "任务不存在")
    if task.status not in (TaskStatus.pending, TaskStatus.running):
        return {"ok": False, "message": "任务已结束"}
    manager.cancel(f"fetch:{task_id}")
    task.status = TaskStatus.cancelled
    db.commit()
    return {"ok": True, "message": "已请求取消"}


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db),
                      user: User = Depends(get_current_user)):
    """删除抓取任务记录（不影响已抓取的文章数据）。进行中任务会先取消。"""
    task = db.get(FetchTask, task_id)
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "任务不存在")
    if task.status in (TaskStatus.pending, TaskStatus.running):
        manager.cancel(f"fetch:{task_id}")
        task.status = TaskStatus.cancelled
        db.commit()
        await asyncio.sleep(0.5)  # 给后台协程一个退出窗口
    db.delete(task)
    db.commit()
    return {"ok": True}


@router.get("/tasks/{task_id}/articles")
def task_articles(task_id: int, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    """该任务抓到的文章 id 列表（供「按任务导入分析」）。

    优先用任务运行时记录的快照；老任务无快照则按 账号+时间范围 回退匹配。
    """
    task = db.get(FetchTask, task_id)
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "任务不存在")
    ids = list(task.article_ids or [])
    if not ids and task.account_ids:
        q = db.query(Article.id).filter(Article.account_id.in_(task.account_ids))
        if task.time_start:
            q = q.filter(Article.publish_time >= task.time_start)
        if task.time_end:
            q = q.filter(Article.publish_time <= task.time_end)
        ids = [r[0] for r in q.all()]
    return {"task_id": task_id, "article_ids": ids, "total": len(ids)}
