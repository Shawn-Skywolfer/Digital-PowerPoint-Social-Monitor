"""定时任务调度：APScheduler(AsyncIO) 驱动定时抓取 + 阅读量排名。"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ..core.logging import get_logger
from ..db.base import utcnow
from ..db.session import SessionLocal
from ..models import FetchTask, ScheduledJob, TaskStatus
from ..services import ranking_service
from ..services.fetch_service import run_fetch_task

logger = get_logger(__name__)

scheduler: Optional[AsyncIOScheduler] = None

_JOB_PREFIX = "cronjob:"


def start_scheduler() -> None:
    global scheduler
    if scheduler and scheduler.running:
        return
    scheduler = AsyncIOScheduler()
    scheduler.start()
    sync_all_jobs()
    logger.info("APScheduler 已启动，载入 %d 个任务", len(scheduler.get_jobs()))


def shutdown_scheduler() -> None:
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler 已停止")


def _job_key(job_id: int) -> str:
    return f"{_JOB_PREFIX}{job_id}"


def sync_all_jobs() -> None:
    """从 DB 读取所有启用的任务并注册。"""
    if not scheduler:
        return
    db = SessionLocal()
    try:
        jobs = db.query(ScheduledJob).filter(ScheduledJob.enabled.is_(True)).all()
        for job in jobs:
            _register(job)
    finally:
        db.close()


def register_job(job_id: int) -> None:
    if not scheduler:
        return
    db = SessionLocal()
    try:
        job = db.get(ScheduledJob, job_id)
        if job:
            _register(job)
    finally:
        db.close()


def remove_job(job_id: int) -> None:
    if not scheduler:
        return
    key = _job_key(job_id)
    if scheduler.get_job(key):
        scheduler.remove_job(key)


def _register(job: ScheduledJob) -> None:
    key = _job_key(job.id)
    try:
        trigger = CronTrigger.from_crontab(job.cron)
    except Exception as e:  # noqa: BLE001
        logger.error("任务 %s cron 非法(%s): %s", job.id, job.cron, e)
        return
    if scheduler.get_job(key):
        scheduler.remove_job(key)
    scheduler.add_job(
        _execute_job, trigger=trigger, id=key, args=[job.id],
        replace_existing=True, misfire_grace_time=3600,
    )
    # 更新 next_run
    db = SessionLocal()
    try:
        j = db.get(ScheduledJob, job.id)
        aj = scheduler.get_job(key)
        if j and aj and aj.next_run_time:
            j.next_run = aj.next_run_time
            db.commit()
    finally:
        db.close()


async def _execute_job(job_id: int) -> None:
    logger.info("定时任务 %s 触发", job_id)
    db = SessionLocal()
    try:
        job = db.get(ScheduledJob, job_id)
        if not job or not job.enabled:
            return
        # 建一个抓取任务（默认抓最近文章；若指定字段含指标则取指标）
        task = FetchTask(
            owner_id=job.owner_id, account_ids=job.account_ids, fields=job.fields,
            key_id=job.key_id, status=TaskStatus.pending,
            log=f"[{utcnow().isoformat()}] 由定时任务[{job.name}]创建\n",
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        task_id = task.id
        job.last_run = utcnow()
        db.commit()
    finally:
        db.close()

    # 执行抓取（等待完成）
    await run_fetch_task(task_id, asyncio.Event())

    # 排名
    db = SessionLocal()
    try:
        job = db.get(ScheduledJob, job_id)
        if job and job.ranking_enabled:
            period_end = utcnow()
            period_start = period_end - timedelta(days=7)  # 默认近7天
            ranking_service.create_report(
                db, job_id=job.id, metric=job.ranking_metric,
                account_ids=job.account_ids,
                period_start=period_start, period_end=period_end,
            )
            logger.info("定时任务 %s 生成排名报告", job_id)
        if job:
            aj = scheduler.get_job(_job_key(job_id)) if scheduler else None
            if aj and aj.next_run_time:
                job.next_run = aj.next_run_time
            db.commit()
    except Exception as e:  # noqa: BLE001
        logger.exception("定时任务 %s 排名失败", job_id)
        job = db.get(ScheduledJob, job_id)
        if job:
            job.last_error = str(e)
            db.commit()
    finally:
        db.close()


async def run_job_now(job_id: int) -> None:
    """手动立即触发一次。"""
    await _execute_job(job_id)
