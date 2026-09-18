"""LLM 注册：从 LLMConfig 记录构建客户端。"""
from __future__ import annotations

from ..core.security import decrypt_secret
from ..models.config import LLMConfig
from .base import LLMClient
from .openai_compat import OpenAICompatClient


def build_llm_client(cfg: LLMConfig) -> LLMClient:
    """目前所有 provider 都走 OpenAI 兼容协议；如有特殊厂商可在此分支。"""
    return OpenAICompatClient(
        base_url=cfg.base_url,
        api_key=decrypt_secret(cfg.api_key_enc),
        model=cfg.model,
        default_params=cfg.params or {},
    )
