"""外部服务配置 schema：LLM / dajiala Key / MCP / LightPanda / Tavily。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from ..models.config import KeyStatus, MCPTransport, ServiceKind


# ---------- LLM ----------
class LLMConfigIn(BaseModel):
    name: str
    provider: str = "openai"
    base_url: str
    api_key: str = ""
    model: str
    params: Optional[dict] = None
    enabled: bool = True


class LLMConfigUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None  # 不传则不修改
    model: Optional[str] = None
    params: Optional[dict] = None
    enabled: Optional[bool] = None


class LLMConfigOut(BaseModel):
    id: int
    name: str
    provider: str
    base_url: str
    model: str
    params: Optional[dict] = None
    enabled: bool
    api_key_masked: str = ""

    model_config = {"from_attributes": True}


# ---------- dajiala Key ----------
class KeyIn(BaseModel):
    label: str
    key: str
    quota: Optional[int] = None
    is_default: bool = False
    note: Optional[str] = None


class KeyUpdate(BaseModel):
    label: Optional[str] = None
    key: Optional[str] = None
    quota: Optional[int] = None
    is_default: Optional[bool] = None
    enabled: Optional[bool] = None
    note: Optional[str] = None


class KeyOut(BaseModel):
    id: int
    label: str
    key_masked: str = ""
    owner_id: Optional[int] = None
    quota: Optional[int] = None
    used: int
    status: KeyStatus
    is_default: bool
    enabled: bool
    last_check: Optional[datetime] = None
    note: Optional[str] = None

    model_config = {"from_attributes": True}


# ---------- MCP ----------
class MCPServerIn(BaseModel):
    name: str
    transport: MCPTransport = MCPTransport.sse
    command: Optional[str] = None
    args: Optional[list[str]] = None
    env: Optional[dict] = None
    url: Optional[str] = None
    headers: Optional[dict] = None
    enabled: bool = True
    note: Optional[str] = None


class MCPServerOut(BaseModel):
    id: int
    name: str
    transport: MCPTransport
    command: Optional[str] = None
    args: Optional[list] = None
    url: Optional[str] = None
    enabled: bool
    note: Optional[str] = None

    model_config = {"from_attributes": True}


# ---------- LightPanda / Tavily ----------
class ServiceConfigIn(BaseModel):
    service: ServiceKind
    name: str
    base_url: Optional[str] = None
    api_key: str = ""
    extra: Optional[dict] = None
    enabled: bool = True


class ServiceConfigOut(BaseModel):
    id: int
    service: ServiceKind
    name: str
    base_url: Optional[str] = None
    api_key_masked: str = ""
    extra: Optional[dict] = None
    enabled: bool

    model_config = {"from_attributes": True}


class TestResult(BaseModel):
    ok: bool
    message: str = ""
