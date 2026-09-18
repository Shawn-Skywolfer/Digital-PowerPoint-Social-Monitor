"""排名：按指标对最新快照排序，生成日报/周报。"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from ..models import Article, ArticleStatus, RankingReport
from .article_service import account_name_map, latest_metrics_map


def build_ranking(
    db: Session,
    account_ids: Optional[list[int]] = None,
    metric: str = "read_num",
    period_start: Optional[datetime] = None,
    period_end: Optional[datetime] = None,
    limit: int = 50,
) -> list[dict]:
    q = db.query(Article).filter(Article.status != ArticleStatus.deleted)
    if account_ids:
        q = q.filter(Article.account_id.in_(account_ids))
    if period_start:
        q = q.filter(Article.publish_time >= period_start)
    if period_end:
        q = q.filter(Article.publish_time <= period_end)
    articles = q.all()
    mmap = latest_metrics_map(db, [a.id for a in articles])
    names = account_name_map(db, list({a.account_id for a in articles}))

    items = []
    for a in articles:
        m = mmap.get(a.id)
        items.append({
            "article_id": a.id,
            "account_id": a.account_id,
            "account_name": names.get(a.account_id),
            "title": a.title,
            "url": a.url,
            "publish_time": a.publish_time.isoformat() if a.publish_time else None,
            "read_num": m.read_num if m else None,
            "like_num": m.like_num if m else None,
            "wow_num": m.wow_num if m else None,
            "share_num": m.share_num if m else None,
            "comment_count": m.comment_count if m else None,
        })
    items.sort(key=lambda x: (x.get(metric) or 0), reverse=True)
    return items[:limit]


def create_report(db: Session, job_id: int, metric: str,
                  account_ids: Optional[list[int]],
                  period_start: Optional[datetime], period_end: Optional[datetime],
                  limit: int = 50) -> RankingReport:
    items = build_ranking(db, account_ids, metric, period_start, period_end, limit)
    report = RankingReport(job_id=job_id, metric=metric, items=items,
                           period_start=period_start, period_end=period_end)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
