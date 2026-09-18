"""OpenAI 兼容协议客户端：一套代码接 OpenAI/DeepSeek/Qwen/文心/Ollama 等。"""
from __future__ import annotations

from typing import Any, Optional

import httpx

from ..core.config import settings
from .base import LLMClient, LLMError, LLMResult


class OpenAICompatClient(LLMClient):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        default_params: Optional[dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.default_params = default_params or {}
        self.timeout = timeout or settings.llm_request_timeout

    def _endpoint(self) -> str:
        # 兼容用户填到 .../v1 或 .../v1/ 或已带 /chat/completions
        if self.base_url.endswith("/chat/completions"):
            return self.base_url
        return self.base_url + "/chat/completions"

    async def chat(self, messages: list[dict[str, str]], **params: Any) -> LLMResult:
        body: dict[str, Any] = {"model": self.model, "messages": messages}
        merged = {**self.default_params, **params}
        body.update({k: v for k, v in merged.items() if v is not None})
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        try:
            async with httpx.AsyncClient(timeout=self.timeout, **settings.httpx_kwargs) as client:
                resp = await client.post(self._endpoint(), json=body, headers=headers)
                if resp.status_code >= 400:
                    raise LLMError(f"LLM HTTP {resp.status_code}: {resp.text[:300]}")
                data = resp.json()
        except httpx.RequestError as e:
            raise LLMError(f"LLM 请求失败: {e}") from e

        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise LLMError(f"LLM 返回结构异常: {str(data)[:300]}") from e
        usage = data.get("usage") or {}
        return LLMResult(
            text=text,
            model=data.get("model", self.model),
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
            raw=data,
        )

    async def test(self) -> tuple[bool, str]:
        try:
            result = await self.chat(
                [{"role": "user", "content": "ping，回复 pong"}],
                max_tokens=8,
            )
            return True, f"连接成功，模型 {result.model or self.model} 响应正常"
        except LLMError as e:
            return False, str(e)
