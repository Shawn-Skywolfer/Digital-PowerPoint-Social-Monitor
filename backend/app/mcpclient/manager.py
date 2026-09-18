"""MCP client 管理：连接 MCP server（FireCrawl 等）、列工具、连通性测试。

`mcp` SDK 为可选依赖；未安装时仅配置可保存，连接测试会提示需要安装。
"""
from __future__ import annotations

from typing import Any, Optional

from ..core.logging import get_logger
from ..models.config import MCPServer, MCPTransport

logger = get_logger(__name__)

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.sse import sse_client
    from mcp.client.stdio import stdio_client
    try:
        from mcp.client.streamable_http import streamablehttp_client
        _HAS_HTTP = True
    except Exception:  # noqa: BLE001
        _HAS_HTTP = False
    _HAS_MCP = True
except Exception:  # noqa: BLE001
    _HAS_MCP = False
    _HAS_HTTP = False


def mcp_available() -> bool:
    return _HAS_MCP


async def list_tools(server: MCPServer) -> list[dict[str, Any]]:
    """连接并列出 MCP server 的工具。"""
    if not _HAS_MCP:
        raise RuntimeError("未安装 mcp SDK（pip install mcp）")

    if server.transport == MCPTransport.stdio:
        params = StdioServerParameters(
            command=server.command or "", args=server.args or [],
            env=server.env or None,
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                res = await session.list_tools()
                return [{"name": t.name, "description": t.description or ""} for t in res.tools]

    if server.transport == MCPTransport.sse:
        async with sse_client(server.url, headers=server.headers or None) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                res = await session.list_tools()
                return [{"name": t.name, "description": t.description or ""} for t in res.tools]

    if server.transport == MCPTransport.http:
        if not _HAS_HTTP:
            raise RuntimeError("当前 mcp SDK 不支持 streamable http 传输")
        async with streamablehttp_client(server.url, headers=server.headers or None) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                res = await session.list_tools()
                return [{"name": t.name, "description": t.description or ""} for t in res.tools]

    raise RuntimeError(f"未知传输方式: {server.transport}")


async def test_connection(server: MCPServer) -> tuple[bool, str]:
    """连通性测试：尝试 initialize + list_tools。"""
    try:
        tools = await list_tools(server)
        names = ", ".join(t["name"] for t in tools[:10])
        return True, f"连接成功，发现 {len(tools)} 个工具: {names}"
    except Exception as e:  # noqa: BLE001
        logger.warning("MCP 连接测试失败 %s: %s", server.name, e)
        return False, f"连接失败: {e}"
