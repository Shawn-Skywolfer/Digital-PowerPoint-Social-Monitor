"""各类外部服务配置：LLM、dajiala Key、MCP server、LightPanda/Tavily。"""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (JSON, Boolean, DateTime, Enum, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base, TimestampMixin


class LLMConfig(Base, TimestampMixin):
    """多大模型配置（OpenAI 兼容协议）。"""
    __tablename__ = "llm_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))  # 显示名，如 "DeepSeek-V3"
    provider: Mapped[str] = mapped_column(String(64), default="openai")  # openai/deepseek/qwen/...
    base_url: Mapped[str] = mapped_column(String(512))
    api_key_enc: Mapped[str] = mapped_column(Text, default="")
    model: Mapped[str] = mapped_column(String(128))
    params: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # temperature/max_tokens 等
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)


class KeyStatus(str, enum.Enum):
    active = "active"
    exhausted = "exhausted"   # 配额用尽
    invalid = "invalid"
    unknown = "unknown"


class DajialaKey(Base, TimestampMixin):
    """dajiala 多 Key 池，按用户绑定、统计用量。"""
    __tablename__ = "dajiala_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    label: Mapped[str] = mapped_column(String(128))
    key_enc: Mapped[str] = mapped_column(Text, default="")
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    quota: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 总额度(积分), 可空=未知
    used: Mapped[int] = mapped_column(Integer, default=0)              # 已用(本系统统计)
    status: Mapped[KeyStatus] = mapped_column(Enum(KeyStatus), default=KeyStatus.unknown)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_check: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)


class MCPTransport(str, enum.Enum):
    stdio = "stdio"
    sse = "sse"
    http = "http"


class MCPServer(Base, TimestampMixin):
    """MCP server 配置（如 FireCrawl）。stdio 用 command/args/env；sse/http 用 url。"""
    __tablename__ = "mcp_servers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    transport: Mapped[MCPTransport] = mapped_column(Enum(MCPTransport), default=MCPTransport.sse)
    command: Mapped[str | None] = mapped_column(String(512), nullable=True)  # stdio
    args: Mapped[list | None] = mapped_column(JSON, nullable=True)           # stdio
    env: Mapped[dict | None] = mapped_column(JSON, nullable=True)            # stdio（含 API key）
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)      # sse/http
    headers: Mapped[dict | None] = mapped_column(JSON, nullable=True)        # sse/http
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)


class ServiceKind(str, enum.Enum):
    lightpanda = "lightpanda"
    tavily = "tavily"


class ServiceConfig(Base, TimestampMixin):
    """LightPanda 云端服务、Tavily 搜索等第三方服务配置。"""
    __tablename__ = "service_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service: Mapped[ServiceKind] = mapped_column(Enum(ServiceKind), index=True)
    name: Mapped[str] = mapped_column(String(128))
    base_url: Mapped[str | None] = mapped_column(String(512), nullable=True)  # lightpanda 云端 ws/http
    api_key_enc: Mapped[str] = mapped_column(Text, default="")                # tavily key / lightpanda token
    extra: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)


class Setting(Base):
    """系统级 KV 配置（导出目录、是否强制改密等）。"""
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
