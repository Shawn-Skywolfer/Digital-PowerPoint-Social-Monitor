"""抓取方案与抓取任务 schema。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from ..models.fetch import TaskStatus


class FetchProfileIn(BaseModel):
    name: str
    fields: list[str]


class FetchProfileOut(BaseModel):
    id: int
    name: str
    fields: list[str]

    model_config = {"from_attributes": True}


class FetchTaskCreate(BaseModel):
    account_ids: list[int] = []
    group_ids: list[int] = []  # 按分组抓取：与 account_ids 取并集
    article_ids: list[int] = []  # 按文章清单补抓（搜索结果批量下载）；非空则忽略账号维度
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None
    fields: list[str] = Field(default_factory=lambda: ["title", "publish_time", "read_num"])
    key_id: Optional[int] = None


class FetchTaskOut(BaseModel):
    id: int
    status: TaskStatus
    progress: int
    total_items: int
    done_items: int
    new_articles: int
    updated_articles: int
    reviews_created: int
    account_ids: list[int]
    group_ids: list[int] = []
    article_ids: list[int] = []
    fields: list[str]
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None
    error: Optional[str] = None
    log: Optional[str] = None
    created_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @field_validator("group_ids", "article_ids", "account_ids", "fields", mode="before")
    @classmethod
    def _none_to_list(cls, v):
        return v if v is not None else []
