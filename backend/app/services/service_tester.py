"""LightPanda / Tavily 服务连通性测试。"""
from __future__ import annotations

from typing import Optional

import httpx

from ..core.config import settings
from ..models.config import ServiceConfig, ServiceKind


async def test_service(cfg: ServiceConfig) -> tuple[bool, str]:
    if cfg.service == ServiceKind.tavily:
        return await _test_tavily(cfg)
    if cfg.service == ServiceKind.lightpanda:
        return await _test_lightpanda(cfg)
    return False, "未知服务类型"


async def _test_tavily(cfg: ServiceConfig) -> tuple[bool, str]:
    from ..core.security import decrypt_secret
    key = decrypt_secret(cfg.api_key_enc)
    if not key:
        return False, "未配置 Tavily API Key"
    url = (cfg.base_url or "https://api.tavily.com").rstrip("/") + "/search"
    try:
        async with httpx.AsyncClient(timeout=settings.fetch_request_timeout, **settings.httpx_kwargs) as client:
            resp = await client.post(url, json={
                "query": "test", "max_results": 1, "api_key": key,
            })
            if resp.status_code == 200:
                return True, "Tavily 连接成功"
            return False, f"Tavily HTTP {resp.status_code}: {resp.text[:200]}"
    except httpx.RequestError as e:
        return False, f"Tavily 请求失败: {e}"


async def _test_lightpanda(cfg: ServiceConfig) -> tuple[bool, str]:
    if not cfg.base_url:
        return False, "未配置 LightPanda base_url"
    # 云端 LightPanda 通常暴露 CDP 的 /json/version 元信息
    base = cfg.base_url.rstrip("/")
    url = base if base.endswith("/json/version") else base + "/json/version"
    headers = {}
    from ..core.security import decrypt_secret
    token = decrypt_secret(cfg.api_key_enc)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        async with httpx.AsyncClient(timeout=settings.fetch_request_timeout, **settings.httpx_kwargs) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                return True, "LightPanda 连接成功"
            # 有些部署根路径即可达
            resp2 = await client.get(base, headers=headers)
            if resp2.status_code < 500:
                return True, f"LightPanda 可达(HTTP {resp2.status_code})"
            return False, f"LightPanda HTTP {resp.status_code}"
    except httpx.RequestError as e:
        return False, f"LightPanda 请求失败: {e}"
