"""分析模块、分析维度、分析结果。"""
from __future__ import annotations

import enum

from sqlalchemy import (JSON, Boolean, Enum, ForeignKey, Integer, String, Text)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, TimestampMixin


class AnalysisTarget(str, enum.Enum):
    content = "content"    # 针对正文
    comment = "comment"    # 针对评论
    both = "both"
    collection = "collection"  # 聚合分析：把一批文章作为整体出一份报告


class AnalysisModule(Base, TimestampMixin):
    """分析模块，如"正文分析""评论分析"。含可复用的 prompt 模板。"""
    __tablename__ = "analysis_modules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    target: Mapped[AnalysisTarget] = mapped_column(Enum(AnalysisTarget), default=AnalysisTarget.content)
    # prompt 模板，支持 {title} {content} {comments} {dimensions} 占位
    prompt_template: Mapped[str] = mapped_column(Text, default="")
    builtin: Mapped[bool] = mapped_column(Boolean, default=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    dimensions = relationship(
        "AnalysisDimension", back_populates="module",
        cascade="all, delete-orphan", order_by="AnalysisDimension.order",
    )


class AnalysisDimension(Base, TimestampMixin):
    """自定义分析维度，如"情绪倾向""核心观点""传播风险"。可导入/导出。"""
    __tablename__ = "analysis_dimensions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("analysis_modules.id"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    prompt: Mapped[str] = mapped_column(Text, default="")  # 该维度的具体指令
    order: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    module = relationship("AnalysisModule", back_populates="dimensions")


class ResultStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"


class AnalysisResult(Base, TimestampMixin):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), index=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("analysis_modules.id"))
    llm_config_id: Mapped[int | None] = mapped_column(ForeignKey("llm_configs.id"), nullable=True)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    dimensions: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 快照
    result_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[ResultStatus] = mapped_column(Enum(ResultStatus), default=ResultStatus.pending, index=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 批量任务分组 id
    batch_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)


class CollectionReport(Base, TimestampMixin):
    """聚合分析报告：一批文章整体出一份（议题提炼 + 按议题汇总阅读/点赞）。"""
    __tablename__ = "collection_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("analysis_modules.id"))
    llm_config_id: Mapped[int | None] = mapped_column(ForeignKey("llm_configs.id"), nullable=True)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    article_ids: Mapped[list] = mapped_column(JSON, default=list)     # 分析范围快照
    dimensions: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 维度快照
    overview: Mapped[str | None] = mapped_column(Text, nullable=True)  # 总体概述
    result_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # topics+统计
    tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[ResultStatus] = mapped_column(Enum(ResultStatus), default=ResultStatus.pending, index=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    batch_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
