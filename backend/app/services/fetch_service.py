"""抓取工作流：文章列表 upsert、指标快照、评论抓取、变更检测（待确认）。"""
from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.logging import get_logger
from ..db.base import utcnow
from ..db.session import SessionLocal
from ..models import (Account, Article, ArticleStatus, ChangeReview, ChangeType,
                      Comment, FetchTask, MetricSnapshot, ReviewStatus, TaskStatus)
from ..models.article import CommentStatus
from ..models.config import KeyStatus
from ..providers.base import (AccountInfo, ArticleDeletedError, ArticleInfo,
                              ProviderAuthError, ProviderError, ProviderQuotaError)
from ..providers.registry import get_provider
from ..tasks.queue import CancelEvent
from ..utils.wxcontent import canonical_url_key
from . import key_service

logger = get_logger(__name__)

# 评论数下降超过该比例则触发待确认
COMMENT_DROP_RATIO = 0.2


def _to_account_info(acc: Account) -> AccountInfo:
    return AccountInfo(biz=acc.biz, name=acc.name, gh_id=acc.gh_id, avatar=acc.avatar,
                       intro=acc.intro, verify=acc.verify, profile_url=acc.profile_url)


def _latest_snapshot(db: Session, article_id: int) -> Optional[MetricSnapshot]:
    return (db.query(MetricSnapshot)
            .filter(MetricSnapshot.article_id == article_id)
            .order_by(MetricSnapshot.fetched_at.desc())
            .first())


def _has_pending_review(db: Session, article_id: int, change_type: ChangeType) -> bool:
    return db.query(ChangeReview).filter(
        ChangeReview.article_id == article_id,
        ChangeReview.change_type == change_type,
        ChangeReview.status == ReviewStatus.pending,
    ).first() is not None


def _create_review(db: Session, article_id: int, change_type: ChangeType,
                   old: dict, new: dict, note: str = "") -> None:
    if _has_pending_review(db, article_id, change_type):
        return
    db.add(ChangeReview(article_id=article_id, change_type=change_type,
                        old_data=old, new_data=new, note=note,
                        status=ReviewStatus.pending))


def _find_article(db: Session, account_id: int, url: str) -> Optional[Article]:
    """跨任务归一：优先按稳定身份键 url_key 匹配，兜底按完整 URL。

    微信文章 URL 的一次性参数（chksm 等）每次抓取都变，只靠 URL 唯一约束
    会把同一篇文章存成多行（不同任务参数不同 → 有的有指标有的没有）。
    """
    key = canonical_url_key(url)
    if key:
        art = (db.query(Article)
               .filter(Article.account_id == account_id, Article.url_key == key)
               .first())
        if art:
            return art
    return (db.query(Article)
            .filter(Article.account_id == account_id, Article.url == url)
            .first())


def _upsert_article(db: Session, account_id: int, info: ArticleInfo) -> tuple[Article, bool]:
    """返回 (article, is_new)。同一篇文章无论被哪个任务抓到都归一到同一行。"""
    art = _find_article(db, account_id, info.url)
    is_new = art is None
    if is_new:
        art = Article(account_id=account_id, url=info.url)
        db.add(art)
    # 更新可变字段；URL 每次带最新的一次性参数（调指标/详情接口用新链接更稳）
    art.url = info.url or art.url
    art.url_key = canonical_url_key(info.url) or art.url_key
    art.title = info.title or art.title
    art.author = info.author or art.author
    art.msgid = info.msgid or art.msgid
    art.cover = info.cover or art.cover
    art.digest = info.digest or art.digest
    if info.publish_time:
        art.publish_time = info.publish_time
    art.last_seen_at = utcnow()
    # 若此前被标删除但又重新出现在发文列表里，说明文章恢复了，回到正常
    # （pending_review 不自动恢复：疑似删除需人工在「变更确认」里裁决）
    if art.status == ArticleStatus.deleted:
        art.status = ArticleStatus.normal
    db.flush()
    return art, is_new


async def run_fetch_task(task_id: int, cancel: CancelEvent) -> None:
    db = SessionLocal()
    task = db.get(FetchTask, task_id)
    if not task:
        db.close()
        return
    task.status = TaskStatus.running
    task.log = (task.log or "") + f"[{utcnow().isoformat()}] 任务开始\n"
    db.commit()

    key = key_service.pick_key(db, owner_id=task.owner_id, key_id=task.key_id)
    key_value = key_service.get_key_value(key)
    provider = get_provider(None if (key_value or not settings.provider_mock) else "mock")
    if settings.provider_mock:
        provider = get_provider("mock")
    task.key_id = key.id if key else None
    db.commit()

    fields = set(task.fields or [])
    want_content = "content" in fields
    metric_fields = [f for f in fields if f in
                     ("read_num", "like_num", "wow_num", "share_num", "collect_num")]
    want_comment = "comment" in fields

    accounts = db.query(Account).filter(Account.id.in_(task.account_ids)).all()
    # 预估工作量用于进度
    task.total_items = max(len(accounts), 1)
    db.commit()
    done_accounts = 0
    touched_ids: set[int] = set()  # 本次任务实际抓到的文章

    try:
        for acc in accounts:
            if cancel.is_set():
                task.status = TaskStatus.cancelled
                break
            try:
                await _fetch_one_account(
                    db, provider, key_value, acc, task,
                    time_start=task.time_start, time_end=task.time_end,
                    want_content=want_content, metric_fields=metric_fields,
                    want_comment=want_comment, cancel=cancel, touched=touched_ids,
                )
            except (ProviderAuthError, ProviderQuotaError) as e:
                key_service.mark_status(
                    db, task.key_id,
                    KeyStatus.invalid if isinstance(e, ProviderAuthError) else KeyStatus.exhausted)
                task.log = (task.log or "") + f"[{utcnow().isoformat()}] 账号{acc.name} Key异常: {e}\n"
                db.commit()
                break  # Key 出问题，终止任务换 Key
            except ProviderError as e:
                task.log = (task.log or "") + f"[{utcnow().isoformat()}] 账号{acc.name} 抓取失败: {e}\n"
                db.commit()
            done_accounts += 1
            task.done_items = done_accounts
            task.progress = int(done_accounts / task.total_items * 100)
            db.commit()

        task.article_ids = sorted(touched_ids)  # 快照：供「按任务导入分析」
        if task.status == TaskStatus.running:
            task.status = TaskStatus.success
    except Exception as e:  # noqa: BLE001
        logger.exception("抓取任务 %s 异常", task_id)
        task.status = TaskStatus.failed
        task.error = str(e)
    finally:
        task.finished_at = utcnow()
        task.progress = 100 if task.status in (TaskStatus.success,) else task.progress
        task.log = (task.log or "") + f"[{utcnow().isoformat()}] 任务结束: {task.status.value}\n"
        db.commit()
        db.close()


async def run_article_download(task_id: int, cancel: CancelEvent) -> None:
    """按文章清单补抓（正文/指标/评论）——关键词搜索结果「批量下载」的执行通道。

    与 run_fetch_task 的区别：不扫公众号发文列表，直接对已建档的文章逐篇
    调接口，花多少钱补多少篇，精确可控。任务仍出现在「内容抓取」列表里。
    """
    db = SessionLocal()
    task = db.get(FetchTask, task_id)
    if not task:
        db.close()
        return
    task.status = TaskStatus.running
    task.log = (task.log or "") + f"[{utcnow().isoformat()}] 文章补抓开始\n"
    db.commit()

    key = key_service.pick_key(db, owner_id=task.owner_id, key_id=task.key_id)
    key_value = key_service.get_key_value(key)
    provider = get_provider(None if (key_value or not settings.provider_mock) else "mock")
    if settings.provider_mock:
        provider = get_provider("mock")
    task.key_id = key.id if key else None
    db.commit()

    fields = set(task.fields or [])
    want_content = "content" in fields
    metric_fields = [f for f in fields if f in
                     ("read_num", "like_num", "wow_num", "share_num", "collect_num")]
    want_comment = "comment" in fields

    articles = (db.query(Article).filter(Article.id.in_(task.article_ids or [])).all()
                if task.article_ids else [])
    task.total_items = max(len(articles), 1)
    db.commit()

    done = 0
    try:
        for art in articles:
            if cancel.is_set():
                task.status = TaskStatus.cancelled
                break
            info = ArticleInfo(url=art.url, title=art.title, msgid=art.msgid,
                               author=art.author, publish_time=art.publish_time,
                               cover=art.cover, digest=art.digest)
            # 已删除/疑似删除的文章不再花钱补抓
            if art.status in (ArticleStatus.deleted, ArticleStatus.pending_review):
                task.log = (task.log or "") + f"  跳过[{art.title[:20]}]（{art.status.value}）\n"
            else:
                if want_content and not art.content_fetched:
                    await _fill_content(db, provider, key_value, art, info, task)
                if metric_fields:
                    await _refresh_metrics(db, provider, key_value, art, info,
                                           metric_fields, task)
                if want_comment:
                    await _refresh_comments(db, provider, key_value, art, info, task)
                task.updated_articles += 1
            done += 1
            task.done_items = done
            task.progress = int(done / task.total_items * 100)
            db.commit()
            await asyncio.sleep(0)  # 让出事件循环
        if task.status == TaskStatus.running:
            task.status = TaskStatus.success
    except Exception as e:  # noqa: BLE001
        logger.exception("文章补抓任务 %s 异常", task_id)
        task.status = TaskStatus.failed
        task.error = str(e)
    finally:
        task.finished_at = utcnow()
        task.progress = 100 if task.status == TaskStatus.success else task.progress
        task.log = (task.log or "") + f"[{utcnow().isoformat()}] 任务结束: {task.status.value}\n"
        db.commit()
        db.close()


async def _fetch_one_account(
    db: Session, provider, key_value: Optional[str], acc: Account, task: FetchTask,
    time_start, time_end, want_content: bool, metric_fields: list[str],
    want_comment: bool, cancel: CancelEvent, touched: set[int],
) -> None:
    acc_info = _to_account_info(acc)
    infos = await provider.fetch_article_list(
        acc_info, key_value or "", time_start=time_start, time_end=time_end,
        need_content=False,  # 正文在 upsert 后按需逐篇补抓（见下方 _fill_content）
    )
    key_service.record_usage(db, task.key_id, 1)
    task.log = (task.log or "") + f"[{utcnow().isoformat()}] 账号{acc.name} 取到 {len(infos)} 篇\n"
    db.commit()

    for info in infos:
        if cancel.is_set():
            return
        art, is_new = _upsert_article(db, acc.id, info)
        touched.add(art.id)
        if is_new:
            task.new_articles += 1
        else:
            task.updated_articles += 1

        # 已删除/疑似删除的文章不再花钱刷新任何数据（除非它重新出现在列表里被恢复正常）
        if art.status in (ArticleStatus.deleted, ArticleStatus.pending_review):
            db.commit()
            continue
        # 正文：仅当还没有抓到过时补抓（正文基本不变，重复抓浪费额度）
        if want_content and not art.content_fetched:
            await _fill_content(db, provider, key_value, art, info, task)
        # 指标
        if metric_fields:
            await _refresh_metrics(db, provider, key_value, art, info, metric_fields, task)
        # 评论
        if want_comment:
            await _refresh_comments(db, provider, key_value, art, info, task)
        db.commit()
        await asyncio.sleep(0)  # 让出事件循环


async def _fill_content(db, provider, key_value, art: Article, info: ArticleInfo,
                        task: FetchTask) -> None:
    try:
        filled = await provider.fetch_content(info, key_value or "")
        key_service.record_usage(db, task.key_id, 1)
    except ArticleDeletedError as e:
        art.status = ArticleStatus.pending_review
        _create_review(db, art.id, ChangeType.article_deleted,
                       old={"title": art.title}, new={"error": str(e)},
                       note="抓取正文时返回已删除")
        task.reviews_created += 1
        return
    except ProviderError as e:
        task.log = (task.log or "") + f"  正文抓取失败[{art.title[:20]}]: {e}\n"
        return
    if filled.content_text:
        art.content_text = filled.content_text
        art.content_html = filled.content_html
        art.content_fetched = True
        # 详情接口字段更全，顺带补齐
        art.author = art.author or filled.author
        art.cover = art.cover or filled.cover
        art.digest = art.digest or filled.digest
        if not art.publish_time and filled.publish_time:
            art.publish_time = filled.publish_time
    else:
        task.log = (task.log or "") + f"  正文为空[{art.title[:20]}]\n"


async def _refresh_metrics(db, provider, key_value, art: Article, info: ArticleInfo,
                           metric_fields: list[str], task: FetchTask) -> None:
    prev = _latest_snapshot(db, art.id)
    try:
        m = await provider.fetch_metrics(info, key_value or "", metric_fields)
        key_service.record_usage(db, task.key_id, 1)
    except ArticleDeletedError as e:
        if art.status == ArticleStatus.normal:
            art.status = ArticleStatus.pending_review
            _create_review(db, art.id, ChangeType.article_deleted,
                           old={"title": art.title,
                                "read_num": prev.read_num if prev else None},
                           new={"error": str(e)}, note="抓取指标时返回已删除")
            task.reviews_created += 1
        return
    except ProviderError as e:
        task.log = (task.log or "") + f"  指标抓取失败[{art.title[:20]}]: {e}\n"
        return

    snap = MetricSnapshot(
        article_id=art.id, read_num=m.read_num, like_num=m.like_num, wow_num=m.wow_num,
        share_num=m.share_num, collect_num=m.collect_num, comment_count=m.comment_count,
    )
    db.add(snap)
    db.flush()

    # 评论数异常下降检测
    if (prev and prev.comment_count and m.comment_count is not None
            and m.comment_count < prev.comment_count
            and (prev.comment_count - m.comment_count) / max(prev.comment_count, 1) >= COMMENT_DROP_RATIO):
        _create_review(db, art.id, ChangeType.comment_drop,
                       old={"comment_count": prev.comment_count},
                       new={"comment_count": m.comment_count},
                       note="评论数明显下降，可能有评论被删除/隐藏")
        task.reviews_created += 1


async def _refresh_comments(db, provider, key_value, art: Article, info: ArticleInfo,
                            task: FetchTask) -> None:
    try:
        items = await provider.fetch_comments(info, key_value or "")
        key_service.record_usage(db, task.key_id, 1)
    except ArticleDeletedError as e:
        task.log = (task.log or "") + f"  评论不可抓[{art.title[:20]}]: {e}\n"
        return  # 指标阶段已处理删除
    except ProviderError as e:
        task.log = (task.log or "") + f"  评论抓取失败[{art.title[:20]}]: {e}\n"
        return

    if not items:
        task.log = (task.log or "") + f"  评论为 0 条[{art.title[:20]}]（可能未开通评论）\n"

    seen_ids = set()
    for c in items:
        seen_ids.add(str(c.comment_id))
        existing = (db.query(Comment)
                    .filter(Comment.article_id == art.id, Comment.comment_id == str(c.comment_id))
                    .first())
        if existing:
            existing.like_num = c.like_num if c.like_num is not None else existing.like_num
            existing.content = c.content or existing.content
        else:
            db.add(Comment(
                article_id=art.id, comment_id=str(c.comment_id), nickname=c.nickname,
                content=c.content, like_num=c.like_num, is_sub=c.is_sub,
                parent_id=c.parent_id, comment_time=c.comment_time,
            ))
    # 之前有、这次没了的评论 → 标记 deleted（不物理删，留痕）
    if items:
        disappeared = (db.query(Comment)
                       .filter(Comment.article_id == art.id,
                               Comment.status == CommentStatus.normal)
                       .all())
        missing = [c for c in disappeared if c.comment_id not in seen_ids]
        if missing and len(missing) / max(len(disappeared), 1) >= COMMENT_DROP_RATIO:
            _create_review(db, art.id, ChangeType.comment_drop,
                           old={"missing": [c.comment_id for c in missing][:20]},
                           new={"fetched": len(items)},
                           note=f"{len(missing)} 条评论疑似被删除/隐藏")
            task.reviews_created += 1
