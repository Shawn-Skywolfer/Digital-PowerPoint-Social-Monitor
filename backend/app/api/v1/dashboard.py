"""Dashboard 概览统计。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.deps import get_current_user, get_db
from ...models import (Account, AnalysisResult, Article, ArticleStatus,
                       ChangeReview, Comment, DajialaKey, FetchTask,
                       LLMConfig, RankingReport, ReviewStatus, ScheduledJob, User)
from ...services import ranking_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return {
        "accounts": db.query(Account).filter(Account.is_system.is_(False)).count(),
        "accounts_monitoring": db.query(Account).filter(
            Account.is_monitoring.is_(True), Account.is_system.is_(False)).count(),
        "articles": db.query(Article).count(),
        "articles_pending_review": db.query(Article).filter(
            Article.status == ArticleStatus.pending_review).count(),
        "comments": db.query(Comment).count(),
        "analysis_results": db.query(AnalysisResult).count(),
        "dajiala_keys": db.query(DajialaKey).count(),
        "llm_configs": db.query(LLMConfig).count(),
        "scheduled_jobs": db.query(ScheduledJob).count(),
        "pending_reviews": db.query(ChangeReview).filter(
            ChangeReview.status == ReviewStatus.pending).count(),
        "recent_tasks": db.query(FetchTask).count(),
        "ranking_reports": db.query(RankingReport).count(),
    }


@router.get("/top-articles")
def top_articles(metric: str = "read_num", days: int = 7, limit: int = 10,
                 db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from datetime import timedelta
    from ...db.base import utcnow
    items = ranking_service.build_ranking(
        db, metric=metric, period_start=utcnow() - timedelta(days=days),
        period_end=utcnow(), limit=limit)
    return {"metric": metric, "items": items}
