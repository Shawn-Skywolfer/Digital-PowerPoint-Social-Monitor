"""文章 / 评论 / 指标 schema。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from ..models.article import ArticleStatus, CommentStatus


class MetricOut(BaseModel):
    read_num: Optional[int] = None
    like_num: Optional[int] = None
    wow_num: Optional[int] = None
    share_num: Optional[int] = None
    collect_num: Optional[int] = None
    comment_count: Optional[int] = None
    fetched_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ArticleListItem(BaseModel):
    id: int
    account_id: int
    account_name: Optional[str] = None
    title: str
    author: Optional[str] = None
    url: str
    publish_time: Optional[datetime] = None
    status: ArticleStatus
    content_fetched: bool
    # 最新指标（冗余便于列表展示）
    read_num: Optional[int] = None
    like_num: Optional[int] = None
    wow_num: Optional[int] = None
    share_num: Optional[int] = None
    collect_num: Optional[int] = None
    comment_count: Optional[int] = None


class ArticleDetail(BaseModel):
    id: int
    account_id: int
    account_name: Optional[str] = None
    title: str
    author: Optional[str] = None
    url: str
    cover: Optional[str] = None
    digest: Optional[str] = None
    publish_time: Optional[datetime] = None
    status: ArticleStatus
    content_fetched: bool
    content_text: Optional[str] = None
    first_seen_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    latest_metrics: Optional[MetricOut] = None

    model_config = {"from_attributes": True}


class CommentOut(BaseModel):
    id: int
    comment_id: str
    nickname: Optional[str] = None
    content: Optional[str] = None
    like_num: Optional[int] = None
    is_sub: bool
    parent_id: Optional[str] = None
    comment_time: Optional[datetime] = None
    status: CommentStatus

    model_config = {"from_attributes": True}


class Page(BaseModel):
    total: int
    page: int
    page_size: int
