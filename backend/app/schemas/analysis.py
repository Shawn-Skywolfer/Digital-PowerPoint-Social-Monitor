"""分析模块 / 维度 / 结果 schema。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from ..models.analysis import AnalysisTarget, ResultStatus


class DimensionIn(BaseModel):
    name: str
    prompt: str = ""
    order: int = 0
    enabled: bool = True


class DimensionOut(DimensionIn):
    id: int
    module_id: int

    model_config = {"from_attributes": True}


class ModuleIn(BaseModel):
    name: str
    target: AnalysisTarget = AnalysisTarget.content
    prompt_template: str = ""
    enabled: bool = True


class ModuleOut(BaseModel):
    id: int
    name: str
    target: AnalysisTarget
    prompt_template: str
    builtin: bool
    enabled: bool
    dimensions: list[DimensionOut] = []

    model_config = {"from_attributes": True}


class DimensionImportExport(BaseModel):
    """维度导入/导出载体（可跨模块或单模块）。"""
    module_name: str
    target: AnalysisTarget = AnalysisTarget.content
    prompt_template: str = ""
    dimensions: list[DimensionIn] = []


class CustomContentItem(BaseModel):
    """直接录入的自定义内容（不落库为公众号文章流程，而是挂在系统账号下）。"""
    title: str = ""
    content: str


class AnalysisRunRequest(BaseModel):
    article_ids: list[int] = []
    module_id: int
    llm_config_id: int
    dimension_ids: Optional[list[int]] = None  # 空=用模块全部启用维度
    fetch_task_id: Optional[int] = None        # 一键导入某抓取任务的全部文章
    custom_items: Optional[list[CustomContentItem]] = None  # 自定义录入内容
    custom_dimensions: Optional[list[DimensionIn]] = None   # 临时维度（Prompt形式，不存模块）


class CollectionReportOut(BaseModel):
    id: int
    module_id: int
    model: Optional[str] = None
    status: ResultStatus
    article_ids: list[int] = []
    article_total: int = 0
    overview: Optional[str] = None
    result_text: Optional[str] = None
    result_json: Optional[dict] = None
    tokens: Optional[int] = None
    error: Optional[str] = None
    batch_id: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @field_validator("article_ids", mode="before")
    @classmethod
    def _none_to_list(cls, v):
        return v if v is not None else []


class AnalysisResultOut(BaseModel):
    id: int
    article_id: int
    module_id: int
    model: Optional[str] = None
    status: ResultStatus
    result_text: Optional[str] = None
    result_json: Optional[dict] = None
    tokens: Optional[int] = None
    error: Optional[str] = None
    batch_id: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
