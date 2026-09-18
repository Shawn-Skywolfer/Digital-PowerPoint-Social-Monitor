"""文章查询与最新指标的公共助手（文章列表 / 排名 / 导出共用）。"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import Account, Article, ArticleStatus, MetricSnapshot


def latest_metrics_map(db: Session, article_ids: list[int]) -> dict[int, MetricSnapshot]:
    """每篇文章取最新一条指标快照。DB 无关写法（SQLite/Postgres/MySQL 均可）。"""
    if not article_ids:
        return {}
    subq = (db.query(MetricSnapshot.article_id,
                     func.max(MetricSnapshot.fetched_at).label("mx"))
            .filter(MetricSnapshot.article_id.in_(article_ids))
            .group_by(MetricSnapshot.article_id)
            .subquery())
    rows = (db.query(MetricSnapshot)
            .join(subq, (MetricSnapshot.article_id == subq.c.article_id)
                  & (MetricSnapshot.fetched_at == subq.c.mx))
            .all())
    return {r.article_id: r for r in rows}


def query_articles(
    db: Session,
    account_ids: Optional[list[int]] = None,
    keyword: Optional[str] = None,
    time_start=None,
    time_end=None,
    status: Optional[ArticleStatus] = None,
    sort_by: str = "publish_time",
    sort_desc: bool = True,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Article], int]:
    q = db.query(Article)
    if account_ids:
        q = q.filter(Article.account_id.in_(account_ids))
    if keyword:
        q = q.filter(Article.title.like(f"%{keyword}%"))
    if time_start:
        q = q.filter(Article.publish_time >= time_start)
    if time_end:
        q = q.filter(Article.publish_time <= time_end)
    if status:
        q = q.filter(Article.status == status)
    total = q.count()

    # 数值字段排序需 join 最新指标；这里先按文章字段排序，指标排序在内存做
    if sort_by in ("read_num", "like_num", "wow_num", "share_num", "collect_num", "comment_count"):
        items = q.all()
        mmap = latest_metrics_map(db, [a.id for a in items])
        items.sort(key=lambda a: (getattr(mmap.get(a.id), sort_by, None) or 0),
                   reverse=sort_desc)
        items = items[(page - 1) * page_size: page * page_size]
        return items, total

    col = getattr(Article, sort_by, Article.publish_time)
    q = q.order_by(col.desc() if sort_desc else col.asc())
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def account_name_map(db: Session, account_ids: list[int]) -> dict[int, str]:
    if not account_ids:
        return {}
    return {a.id: a.name for a in db.query(Account).filter(Account.id.in_(account_ids)).all()}
