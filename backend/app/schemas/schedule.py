"""定时任务 / 排名 / 待确认 schema。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ..models.review import ChangeType, ReviewStatus


class ScheduledJobIn(BaseModel):
    name: str
    account_ids: list[int]
    cron: str = Field(description="5段cron: 分 时 日 月 周，如 '0 8 * * *' 每天8点")
    fields: list[str] = Field(default_factory=lambda: ["title", "publish_time", "read_num"])
    key_id: Optional[int] = None
    ranking_enabled: bool = True
    ranking_metric: str = "read_num"
    enabled: bool = True


class ScheduledJobOut(BaseModel):
    id: int
    name: str
    account_ids: list[int]
    cron: str
    fields: list[str]
    ranking_enabled: bool
    ranking_metric: str
    enabled: bool
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    last_error: Optional[str] = None

    model_config = {"from_attributes": True}


class RankingItem(BaseModel):
    article_id: int
    account_id: Optional[int] = None
    account_name: Optional[str] = None
    title: str
    url: Optional[str] = None
    publish_time: Optional[datetime] = None
    read_num: Optional[int] = None
    like_num: Optional[int] = None
    wow_num: Optional[int] = None


class RankingReportOut(BaseModel):
    id: int
    job_id: int
    metric: str
    items: list[dict] = []
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------- 待确认 ----------
class ReviewOut(BaseModel):
    id: int
    article_id: int
    article_title: Optional[str] = None
    change_type: ChangeType
    old_data: Optional[dict] = None
    new_data: Optional[dict] = None
    status: ReviewStatus
    note: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ReviewResolveRequest(BaseModel):
    action: str = Field(description="keep=保留原始 / delete=确认删除")
    note: Optional[str] = None
