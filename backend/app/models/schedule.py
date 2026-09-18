"""定时任务与排名结果。"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base, TimestampMixin


class ScheduledJob(Base, TimestampMixin):
    """定时抓取 + 排名任务。cron 表达式调度。"""
    __tablename__ = "scheduled_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    account_ids: Mapped[list] = mapped_column(JSON, default=list)
    cron: Mapped[str] = mapped_column(String(64))  # 5 段 cron: 分 时 日 月 周
    fields: Mapped[list] = mapped_column(JSON, default=list)
    key_id: Mapped[int | None] = mapped_column(ForeignKey("dajiala_keys.id"), nullable=True)
    ranking_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    ranking_metric: Mapped[str] = mapped_column(String(32), default="read_num")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    last_run: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)


class RankingReport(Base, TimestampMixin):
    """一次定时任务产生的排名结果（日报/周报）。"""
    __tablename__ = "ranking_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("scheduled_jobs.id"), index=True)
    metric: Mapped[str] = mapped_column(String(32), default="read_num")
    # 排名条目: [{article_id, account_id, title, read_num, like_num, publish_time, url}, ...]
    items: Mapped[list] = mapped_column(JSON, default=list)
    period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
