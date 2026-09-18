"""文章、指标快照、评论。指标快照只增不删，支持"自动覆盖更新"与趋势。"""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (JSON, Boolean, DateTime, Enum, ForeignKey, Index,
                        Integer, String, Text, UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, TimestampMixin, utcnow


class ArticleStatus(str, enum.Enum):
    normal = "normal"
    deleted = "deleted"          # 已确认删除（软删，留痕）
    pending_review = "pending_review"  # 检测到疑似删除/异常，待人工确认


class Article(Base, TimestampMixin):
    __tablename__ = "articles"
    __table_args__ = (
        UniqueConstraint("account_id", "url", name="uq_article_account_url"),
        Index("ix_article_publish", "publish_time"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True)
    msgid: Mapped[str | None] = mapped_column(String(128), nullable=True)
    url: Mapped[str] = mapped_column(String(1024))
    # 文章稳定身份键（biz|mid|idx|sn，见 utils.wxcontent.canonical_url_key）：
    # 微信 URL 里 chksm/scene/sessionid 每次抓取都变，跨任务去重必须靠它
    url_key: Mapped[str | None] = mapped_column(String(512), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(1024))
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    publish_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cover: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    digest: Mapped[str | None] = mapped_column(Text, nullable=True)

    content_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_fetched: Mapped[bool] = mapped_column(Boolean, default=False)

    status: Mapped[ArticleStatus] = mapped_column(
        Enum(ArticleStatus), default=ArticleStatus.normal, index=True
    )
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    account = relationship("Account", back_populates="articles")
    metrics = relationship(
        "MetricSnapshot", back_populates="article",
        cascade="all, delete-orphan", order_by="MetricSnapshot.fetched_at",
    )
    comments = relationship(
        "Comment", back_populates="article", cascade="all, delete-orphan"
    )


class MetricSnapshot(Base):
    """一篇文章某次抓取时的互动指标。只增不删：最新一条即当前值。"""
    __tablename__ = "article_metrics_snapshots"
    __table_args__ = (Index("ix_metric_article_time", "article_id", "fetched_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), index=True)
    read_num: Mapped[int | None] = mapped_column(Integer, nullable=True)
    like_num: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wow_num: Mapped[int | None] = mapped_column(Integer, nullable=True)   # 在看
    share_num: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 转发
    collect_num: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 收藏
    comment_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    article = relationship("Article", back_populates="metrics")


class CommentStatus(str, enum.Enum):
    normal = "normal"
    deleted = "deleted"
    hidden = "hidden"


class Comment(Base, TimestampMixin):
    __tablename__ = "comments"
    __table_args__ = (
        UniqueConstraint("article_id", "comment_id", name="uq_comment_article_cid"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), index=True)
    comment_id: Mapped[str] = mapped_column(String(128))  # 平台侧评论 id
    nickname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    like_num: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_sub: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否二级评论
    parent_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    comment_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[CommentStatus] = mapped_column(Enum(CommentStatus), default=CommentStatus.normal)
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    article = relationship("Article", back_populates="comments")
