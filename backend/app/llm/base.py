"""大模型抽象层：统一聊天接口与结果。"""
from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class LLMResult:
    text: str
    model: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    raw: dict[str, Any] | None = None


class LLMError(Exception):
    pass


class LLMClient(abc.ABC):
    """统一的大模型聊天客户端。"""

    @abc.abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        **params: Any,
    ) -> LLMResult:
        """messages 形如 [{"role":"system","content":"..."}]。"""

    @abc.abstractmethod
    async def test(self) -> tuple[bool, str]:
        """连通性测试。"""
