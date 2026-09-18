"""文章查询：列表(过滤/排序/分页)、详情、评论、指标趋势。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...core.deps import get_current_user, get_db
from ...models import (Article, ArticleStatus, Comment, MetricSnapshot, User)
from ...schemas.article import (ArticleDetail, ArticleListItem, CommentOut, MetricOut)
from ...services import article_service

router = APIRouter(prefix="/articles", tags=["articles"])


def _to_list_item(a: Article, m, names: dict[int, str]) -> ArticleListItem:
    return ArticleListItem(
        id=a.id, account_id=a.account_id, account_name=names.get(a.account_id),
        title=a.title, author=a.author, url=a.url, publish_time=a.publish_time,
        status=a.status, content_fetched=a.content_fetched,
        read_num=m.read_num if m else None, like_num=m.like_num if m else None,
        wow_num=m.wow_num if m else None, share_num=m.share_num if m else None,
        collect_num=m.collect_num if m else None,
        comment_count=m.comment_count if m else None,
    )


@router.get("")
def list_articles(
    account_ids: Optional[str] = Query(None, description="逗号分隔"),
    ids: Optional[str] = Query(None, description="按文章id批量过滤，逗号分隔"),
    keyword: Optional[str] = None,
    time_start: Optional[datetime] = None,
    time_end: Optional[datetime] = None,
    status: Optional[ArticleStatus] = None,
    sort_by: str = "publish_time",
    sort_desc: bool = True,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if ids:
        id_list = [int(x) for x in ids.split(",") if x.strip()]
        items = (db.query(Article).filter(Article.id.in_(id_list))
                 .order_by(Article.publish_time.desc()).all())
        mmap = article_service.latest_metrics_map(db, [a.id for a in items])
        names = article_service.account_name_map(db, list({a.account_id for a in items}))
        return {"total": len(items), "page": 1, "page_size": len(items) or 1,
                "items": [_to_list_item(a, mmap.get(a.id), names) for a in items]}
    acct_ids = [int(x) for x in account_ids.split(",") if x.strip()] if account_ids else None
    items, total = article_service.query_articles(
        db, account_ids=acct_ids, keyword=keyword, time_start=time_start, time_end=time_end,
        status=status, sort_by=sort_by, sort_desc=sort_desc, page=page, page_size=page_size,
    )
    mmap = article_service.latest_metrics_map(db, [a.id for a in items])
    names = article_service.account_name_map(db, list({a.account_id for a in items}))
    return {
        "total": total, "page": page, "page_size": page_size,
        "items": [_to_list_item(a, mmap.get(a.id), names) for a in items],
    }


@router.get("/{article_id}", response_model=ArticleDetail)
def article_detail(article_id: int, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    a = db.get(Article, article_id)
    if not a:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "文章不存在")
    mmap = article_service.latest_metrics_map(db, [a.id])
    m = mmap.get(a.id)
    return ArticleDetail(
        id=a.id, account_id=a.account_id,
        account_name=a.account.name if a.account else None,
        title=a.title, author=a.author, url=a.url, cover=a.cover, digest=a.digest,
        publish_time=a.publish_time, status=a.status, content_fetched=a.content_fetched,
        content_text=a.content_text, first_seen_at=a.first_seen_at,
        last_seen_at=a.last_seen_at,
        latest_metrics=MetricOut.model_validate(m) if m else None,
    )


@router.get("/{article_id}/comments", response_model=list[CommentOut])
def article_comments(article_id: int, db: Session = Depends(get_db),
                     user: User = Depends(get_current_user)):
    if not db.get(Article, article_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "文章不存在")
    comments = (db.query(Comment).filter(Comment.article_id == article_id)
                .order_by(Comment.like_num.desc().nullslast(), Comment.id).all())
    return [CommentOut.model_validate(c) for c in comments]


@router.get("/{article_id}/metrics", response_model=list[MetricOut])
def article_metrics_trend(article_id: int, db: Session = Depends(get_db),
                          user: User = Depends(get_current_user)):
    if not db.get(Article, article_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "文章不存在")
    snaps = (db.query(MetricSnapshot).filter(MetricSnapshot.article_id == article_id)
             .order_by(MetricSnapshot.fetched_at.asc()).all())
    return [MetricOut.model_validate(s) for s in snaps]
