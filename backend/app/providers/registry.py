"""Provider 注册表：按名称获取数据源实现。

预留扩展：后续视频号 / FireCrawl / Tavily / LightPanda 检索，
实现 SourceProvider 后在 `_REGISTRY` 注册即可，主流程无需改动。
"""
from __future__ import annotations

from ..core.config import settings
from .base import SourceProvider
from .dajiala import DajialaProvider
from .mock import MockProvider

_REGISTRY: dict[str, type[SourceProvider]] = {
    "dajiala": DajialaProvider,
    "mock": MockProvider,
    # "shipinhao": ShipinHaoProvider,     # M3 预留
    # "firecrawl": FirecrawlProvider,     # M3 预留
    # "tavily": TavilyProvider,           # M3 预留
    # "lightpanda": LightpandaProvider,   # M3 预留
}


def get_provider(name: str | None = None) -> SourceProvider:
    """返回 Provider 实例。name 为空时按配置返回 dajiala 或 mock。"""
    if name is None:
        name = "mock" if settings.provider_mock else "dajiala"
    cls = _REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"未知数据源: {name}")
    return cls()


def list_providers() -> list[str]:
    return list(_REGISTRY.keys())
