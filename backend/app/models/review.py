"""变更待确认队列 + 审计日志。"""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base, TimestampMixin, utcnow


class ChangeType(str, enum.Enum):
    article_deleted = "article_deleted"      # 文章发布后被删除
    comment_drop = "comment_drop"            # 评论数异常下降（可能被删除/隐藏）
    comment_deleted = "comment_deleted"      # 具体评论消失


class ReviewStatus(str, enum.Enum):
    pending = "pending"
    keep = "keep"        # 保留原始数据
    deleted = "deleted"  # 确认删除（软删，留痕）


class ChangeReview(Base, TimestampMixin):
    """重抓时发现的数据变更，需人工确认是否覆盖/保留。"""
    __tablename__ = "change_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), index=True)
    change_type: Mapped[ChangeType] = mapped_column(Enum(ChangeType))
    old_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 变更前快照
    new_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 变更后观测
    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus), default=ReviewStatus.pending, index=True
    )
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(128))
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
