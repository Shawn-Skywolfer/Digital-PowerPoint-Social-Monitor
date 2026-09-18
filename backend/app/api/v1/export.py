"""导出：文章/评论/分析结果/聚合报告 → Excel/CSV。浏览器下载 + 写入服务器导出目录。"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ...core.config import settings
from ...core.deps import get_current_user, get_db
from ...models import (AnalysisModule, AnalysisResult, Article, CollectionReport,
                       Comment, ResultStatus, User)
from ...services import article_service
from ...utils.export import (ARTICLE_COLUMNS, COMMENT_COLUMNS, export_rows,
                             to_csv, to_xlsx_multi)

router = APIRouter(prefix="/export", tags=["export"])


def _save_copy(data: bytes, filename: str) -> str:
    """在服务器导出目录保存一份副本，返回路径。"""
    os.makedirs(settings.export_dir, exist_ok=True)
    path = os.path.join(settings.export_dir, filename)
    with open(path, "wb") as f:
        f.write(data)
    return path


def _respond(data: bytes, filename: str, fmt: str) -> Response:
    _save_copy(data, filename)
    media = ("text/csv" if fmt == "csv"
             else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    return Response(
        content=data, media_type=media,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


@router.get("/articles")
def export_articles(
    ids: Optional[str] = Query(None, description="逗号分隔；空=导出全部(按过滤)"),
    account_ids: Optional[str] = None,
    keyword: Optional[str] = None,
    fmt: str = "xlsx",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if ids:
        id_list = [int(x) for x in ids.split(",") if x.strip()]
        articles = db.query(Article).filter(Article.id.in_(id_list)).all()
    else:
        acc_ids = [int(x) for x in account_ids.split(",") if x.strip()] if account_ids else None
        articles, _ = article_service.query_articles(
            db, account_ids=acc_ids, keyword=keyword, page=1, page_size=10000)
    mmap = article_service.latest_metrics_map(db, [a.id for a in articles])
    names = article_service.account_name_map(db, list({a.account_id for a in articles}))
    rows = []
    for a in articles:
        m = mmap.get(a.id)
        rows.append({
            "title": a.title, "account_name": names.get(a.account_id),
            "author": a.author, "publish_time": a.publish_time,
            "read_num": m.read_num if m else None,
            "like_num": m.like_num if m else None,
            "wow_num": m.wow_num if m else None,
            "share_num": m.share_num if m else None,
            "collect_num": m.collect_num if m else None,
            "comment_count": m.comment_count if m else None,
            "status": a.status.value, "url": a.url,
            "content_text": a.content_text or "",
        })
    data, ext = export_rows(rows, ARTICLE_COLUMNS, fmt, sheet_name="文章")
    filename = f"articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return _respond(data, filename, fmt)


@router.get("/comments")
def export_comments(
    article_id: int,
    fmt: str = "xlsx",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    article = db.get(Article, article_id)
    comments = db.query(Comment).filter(Comment.article_id == article_id).all()
    rows = [{
        "article_title": article.title if article else "",
        "nickname": c.nickname, "content": c.content, "like_num": c.like_num,
        "is_sub": c.is_sub, "comment_time": c.comment_time, "status": c.status.value,
    } for c in comments]
    data, ext = export_rows(rows, COMMENT_COLUMNS, fmt, sheet_name="评论")
    filename = f"comments_{article_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return _respond(data, filename, fmt)


@router.get("/analysis")
def export_analysis(
    batch_id: Optional[str] = None,
    article_id: Optional[int] = None,
    fmt: str = "xlsx",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(AnalysisResult)
    if batch_id:
        q = q.filter(AnalysisResult.batch_id == batch_id)
    if article_id:
        q = q.filter(AnalysisResult.article_id == article_id)
    results = q.order_by(AnalysisResult.id.desc()).all()
    cols = [("article_title", "文章标题"), ("account_name", "公众号"),
            ("publish_time", "发布时间"), ("module", "分析模块"), ("model", "模型"),
            ("status", "状态"), ("result_text", "分析结果"), ("error", "错误信息"),
            ("tokens", "Token数"), ("created_at", "时间"), ("url", "链接")]
    rows = []
    for r in results:
        article = db.get(Article, r.article_id)
        account = article.account if article else None
        rows.append({
            "article_title": article.title if article else r.article_id,
            "account_name": account.name if account else "",
            "publish_time": article.publish_time if article else None,
            "module": r.module_id, "model": r.model, "result_text": r.result_text,
            "error": r.error, "tokens": r.tokens, "status": r.status.value,
            "created_at": r.created_at, "url": article.url if article else "",
        })
    data, ext = export_rows(rows, cols, fmt, sheet_name="分析结果")
    scope = f"batch_{batch_id[:8]}_" if batch_id else ""
    filename = f"analysis_{scope}{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return _respond(data, filename, fmt)


@router.get("/collection/{report_id}")
def export_collection(
    report_id: int,
    fmt: str = "xlsx",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """导出单份聚合报告：概览 + 议题排行 + 文章清单（多 Sheet Excel）。"""
    r = db.get(CollectionReport, report_id)
    if not r:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "报告不存在")
    if r.status != ResultStatus.success:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "报告尚未分析完成，暂不能导出")

    rj = r.result_json or {}
    module = db.get(AnalysisModule, r.module_id)

    # Sheet 1：报告概览（键值对）
    overview_rows = [
        {"item": "报告编号", "value": r.id},
        {"item": "分析模块", "value": module.name if module else r.module_id},
        {"item": "模型", "value": r.model or ""},
        {"item": "状态", "value": r.status.value},
        {"item": "覆盖文章数", "value": rj.get("article_total") or len(r.article_ids or [])},
        {"item": "Token 数", "value": r.tokens},
        {"item": "生成时间", "value": r.created_at},
        {"item": "分析维度", "value": "、".join(d.get("name", "") for d in (r.dimensions or []))},
        {"item": "总体概述", "value": r.overview or rj.get("overview") or ""},
    ]
    for k, v in (rj.get("dimension_insights") or {}).items():
        overview_rows.append({"item": f"维度洞察·{k}", "value": v})
    overview_cols = [("item", "项目"), ("value", "内容")]

    # Sheet 2：议题排行
    topic_rows = []
    for i, t in enumerate(rj.get("topics") or [], 1):
        topic_rows.append({
            "rank": i, "name": t.get("name"), "article_count": t.get("article_count"),
            "total_read": t.get("total_read"), "total_like": t.get("total_like"),
            "summary": t.get("summary"),
            "top_articles": "；".join(
                f"{a.get('title')}（阅读{a.get('read_num') or '—'}）"
                for a in (t.get("top_articles") or [])),
        })
    topic_cols = [("rank", "排名"), ("name", "议题"), ("article_count", "篇数"),
                  ("total_read", "总阅读"), ("total_like", "总点赞"),
                  ("summary", "议题要点"), ("top_articles", "代表文章")]

    if fmt == "csv":  # CSV 单表，只导出议题排行
        data = to_csv(topic_rows, topic_cols)
        filename = f"collection_{report_id}_topics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return _respond(data, filename, fmt)

    # Sheet 3：文章清单（分析范围内的全部文章）
    article_ids = list(r.article_ids or [])
    articles = (db.query(Article).filter(Article.id.in_(article_ids)).all()
                if article_ids else [])
    mmap = article_service.latest_metrics_map(db, article_ids)
    names = article_service.account_name_map(db, list({a.account_id for a in articles}))
    article_rows = []
    for a in articles:
        m = mmap.get(a.id)
        article_rows.append({
            "title": a.title, "account_name": names.get(a.account_id),
            "publish_time": a.publish_time,
            "read_num": m.read_num if m else None,
            "like_num": m.like_num if m else None,
            "wow_num": m.wow_num if m else None,
            "share_num": m.share_num if m else None,
            "collect_num": m.collect_num if m else None,
            "comment_count": m.comment_count if m else None,
            "status": a.status.value, "url": a.url,
        })
    article_cols = [c for c in ARTICLE_COLUMNS if c[0] not in ("author", "content_text")]

    data = to_xlsx_multi([
        ("报告概览", overview_rows, overview_cols),
        ("议题排行", topic_rows, topic_cols),
        ("文章清单", article_rows, article_cols),
    ])
    filename = f"collection_{report_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return _respond(data, filename, fmt)
