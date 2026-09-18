"""MCP server 配置管理 + 连通性测试（如 FireCrawl）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.deps import get_current_user, get_db
from ...mcpclient import manager as mcp_manager
from ...models import MCPServer, User
from ...schemas.config import MCPServerIn, MCPServerOut, TestResult

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.get("/available")
def available(user: User = Depends(get_current_user)):
    return {"mcp_sdk": mcp_manager.mcp_available()}


@router.get("/servers", response_model=list[MCPServerOut])
def list_servers(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return [MCPServerOut.model_validate(s)
            for s in db.query(MCPServer).order_by(MCPServer.id.desc()).all()]


@router.post("/servers", response_model=MCPServerOut, status_code=status.HTTP_201_CREATED)
def create_server(req: MCPServerIn, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    s = MCPServer(name=req.name, transport=req.transport, command=req.command,
                  args=req.args, env=req.env, url=req.url, headers=req.headers,
                  enabled=req.enabled, note=req.note, owner_id=user.id)
    db.add(s)
    db.commit()
    db.refresh(s)
    return MCPServerOut.model_validate(s)


@router.patch("/servers/{server_id}", response_model=MCPServerOut)
def update_server(server_id: int, req: MCPServerIn, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    s = db.get(MCPServer, server_id)
    if not s:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "配置不存在")
    s.name, s.transport, s.command, s.args, s.env, s.url, s.headers, s.enabled, s.note = (
        req.name, req.transport, req.command, req.args, req.env, req.url,
        req.headers, req.enabled, req.note)
    db.commit()
    db.refresh(s)
    return MCPServerOut.model_validate(s)


@router.delete("/servers/{server_id}")
def delete_server(server_id: int, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    s = db.get(MCPServer, server_id)
    if not s:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "配置不存在")
    db.delete(s)
    db.commit()
    return {"ok": True}


@router.post("/servers/{server_id}/test", response_model=TestResult)
async def test_server(server_id: int, db: Session = Depends(get_db),
                      user: User = Depends(get_current_user)):
    s = db.get(MCPServer, server_id)
    if not s:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "配置不存在")
    if not mcp_manager.mcp_available():
        return TestResult(ok=False, message="后端未安装 mcp SDK（pip install mcp）")
    ok, msg = await mcp_manager.test_connection(s)
    return TestResult(ok=ok, message=msg)
