"""抓取方案（点选字段模板）与抓取任务。"""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base, TimestampMixin


# 可点选的抓取字段（对应 dajiala 分项能力）
FETCHABLE_FIELDS = [
    "title",         # 标题（列表自带）
    "publish_time",  # 发布时间（列表自带）
    "content",       # 正文
    "read_num",      # 阅读量
    "like_num",      # 点赞
    "wow_num",       # 在看
    "share_num",     # 转发
    "collect_num",   # 收藏
    "comment",       # 评论内容
]

# 指标类字段（走 metrics 接口，可分项）
METRIC_FIELDS = ["read_num", "like_num", "wow_num", "share_num", "collect_num"]


class FetchProfile(Base, TimestampMixin):
    __tablename__ = "fetch_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    fields: Mapped[list] = mapped_column(JSON, default=list)  # 选中的字段
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)


class TaskStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"
    cancelled = "cancelled"


class FetchTask(Base, TimestampMixin):
    __tablename__ = "fetch_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    account_ids: Mapped[list] = mapped_column(JSON, default=list)
    group_ids: Mapped[list] = mapped_column(JSON, default=list)  # 发起时选择的分组（仅记录）
    time_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    time_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fields: Mapped[list] = mapped_column(JSON, default=list)
    key_id: Mapped[int | None] = mapped_column(ForeignKey("dajiala_keys.id"), nullable=True)
    # 本次任务实际抓取/更新到的文章 id（供「按任务导入分析」）
    article_ids: Mapped[list] = mapped_column(JSON, default=list)

    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.pending, index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    done_items: Mapped[int] = mapped_column(Integer, default=0)
    new_articles: Mapped[int] = mapped_column(Integer, default=0)
    updated_articles: Mapped[int] = mapped_column(Integer, default=0)
    reviews_created: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    log: Mapped[str | None] = mapped_column(Text, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
