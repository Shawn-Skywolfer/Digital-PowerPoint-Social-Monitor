"""公众号 schema。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AccountOut(BaseModel):
    id: int
    biz: str
    name: str
    gh_id: Optional[str] = None
    avatar: Optional[str] = None
    intro: Optional[str] = None
    verify: Optional[str] = None
    tags: Optional[str] = None
    is_monitoring: bool
    group_id: Optional[int] = None
    group_name: Optional[str] = None
    article_count: int = 0
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------- 分组 ----------
class GroupIn(BaseModel):
    name: str


class GroupOut(BaseModel):
    id: int
    name: str
    account_count: int = 0

    model_config = {"from_attributes": True}


class BatchGroupRequest(BaseModel):
    """把一批公众号加入某分组（group_id=None 表示移出分组）。"""
    account_ids: list[int]
    group_id: Optional[int] = None


class AccountImportRequest(BaseModel):
    """批量导入：每行一个 名称/微信号/链接。"""
    lines: list[str]
    key_id: Optional[int] = None  # 指定用哪个 dajiala Key 解析
    tags: Optional[str] = None


class AccountImportItem(BaseModel):
    input: str
    ok: bool
    biz: Optional[str] = None
    name: Optional[str] = None
    message: Optional[str] = None


class AccountImportResponse(BaseModel):
    total: int
    success: int
    failed: int
    items: list[AccountImportItem]


class AccountSearchRequest(BaseModel):
    query: str
    key_id: Optional[int] = None


class AccountUpdate(BaseModel):
    tags: Optional[str] = None
    is_monitoring: Optional[bool] = None
    group_id: Optional[int] = None  # 传 0 表示移出分组
