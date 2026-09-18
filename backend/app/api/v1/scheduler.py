"""定时任务 + 排名报告。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.deps import get_current_user, get_db
from ...models import RankingReport, ScheduledJob, User
from ...schemas.schedule import (RankingReportOut, ScheduledJobIn, ScheduledJobOut)
from ...tasks import scheduler as sched

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.get("/jobs", response_model=list[ScheduledJobOut])
def list_jobs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return [ScheduledJobOut.model_validate(j)
            for j in db.query(ScheduledJob).order_by(ScheduledJob.id.desc()).all()]


@router.post("/jobs", response_model=ScheduledJobOut, status_code=status.HTTP_201_CREATED)
def create_job(req: ScheduledJobIn, db: Session = Depends(get_db),
               user: User = Depends(get_current_user)):
    if not req.account_ids:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "请至少选择一个公众号")
    # 校验 cron
    from apscheduler.triggers.cron import CronTrigger
    try:
        CronTrigger.from_crontab(req.cron)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"cron 表达式非法: {e}")
    job = ScheduledJob(name=req.name, account_ids=req.account_ids, cron=req.cron,
                       fields=req.fields, key_id=req.key_id,
                       ranking_enabled=req.ranking_enabled,
                       ranking_metric=req.ranking_metric, enabled=req.enabled,
                       owner_id=user.id)
    db.add(job)
    db.commit()
    db.refresh(job)
    sched.register_job(job.id)
    return ScheduledJobOut.model_validate(job)


@router.patch("/jobs/{job_id}", response_model=ScheduledJobOut)
def update_job(job_id: int, req: ScheduledJobIn, db: Session = Depends(get_db),
               user: User = Depends(get_current_user)):
    job = db.get(ScheduledJob, job_id)
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "任务不存在")
    (job.name, job.account_ids, job.cron, job.fields, job.key_id,
     job.ranking_enabled, job.ranking_metric, job.enabled) = (
        req.name, req.account_ids, req.cron, req.fields, req.key_id,
        req.ranking_enabled, req.ranking_metric, req.enabled)
    db.commit()
    db.refresh(job)
    if job.enabled:
        sched.register_job(job.id)
    else:
        sched.remove_job(job.id)
    return ScheduledJobOut.model_validate(job)


@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db),
               user: User = Depends(get_current_user)):
    job = db.get(ScheduledJob, job_id)
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "任务不存在")
    sched.remove_job(job_id)
    db.delete(job)
    db.commit()
    return {"ok": True}


@router.post("/jobs/{job_id}/run")
async def run_job_now(job_id: int, db: Session = Depends(get_db),
                      user: User = Depends(get_current_user)):
    if not db.get(ScheduledJob, job_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "任务不存在")
    await sched.run_job_now(job_id)
    return {"ok": True, "message": "已执行一次"}


@router.get("/reports", response_model=list[RankingReportOut])
def list_reports(job_id: int | None = None, limit: int = 20,
                 db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(RankingReport)
    if job_id:
        q = q.filter(RankingReport.job_id == job_id)
    reports = q.order_by(RankingReport.id.desc()).limit(limit).all()
    return [RankingReportOut.model_validate(r) for r in reports]


@router.get("/ranking")
def current_ranking(account_ids: str | None = None, metric: str = "read_num",
                    days: int = 7, limit: int = 50,
                    db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """实时排名（不落库），用于 Dashboard/排名页。"""
    from datetime import timedelta
    from ...db.base import utcnow
    from ...services import ranking_service
    ids = [int(x) for x in account_ids.split(",") if x.strip()] if account_ids else None
    items = ranking_service.build_ranking(
        db, account_ids=ids, metric=metric,
        period_start=utcnow() - timedelta(days=days), period_end=utcnow(), limit=limit)
    return {"metric": metric, "days": days, "items": items}
