"""多大模型配置管理 + 连通性测试。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.deps import get_current_user, get_db
from ...core.security import decrypt_secret, encrypt_secret, mask_secret
from ...llm.registry import build_llm_client
from ...models import LLMConfig, User
from ...schemas.config import (LLMConfigIn, LLMConfigOut, LLMConfigUpdate, TestResult)

router = APIRouter(prefix="/llm", tags=["llm"])


def _out(cfg: LLMConfig) -> LLMConfigOut:
    o = LLMConfigOut.model_validate(cfg)
    o.api_key_masked = mask_secret(decrypt_secret(cfg.api_key_enc))
    return o


@router.get("/configs", response_model=list[LLMConfigOut])
def list_configs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return [_out(c) for c in db.query(LLMConfig).order_by(LLMConfig.id).all()]


@router.post("/configs", response_model=LLMConfigOut, status_code=status.HTTP_201_CREATED)
def create_config(req: LLMConfigIn, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    cfg = LLMConfig(name=req.name, provider=req.provider, base_url=req.base_url,
                    api_key_enc=encrypt_secret(req.api_key), model=req.model,
                    params=req.params, enabled=req.enabled, owner_id=user.id)
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return _out(cfg)


@router.patch("/configs/{cfg_id}", response_model=LLMConfigOut)
def update_config(cfg_id: int, req: LLMConfigUpdate, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    cfg = db.get(LLMConfig, cfg_id)
    if not cfg:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "配置不存在")
    for f in ("name", "provider", "base_url", "model", "params", "enabled"):
        v = getattr(req, f)
        if v is not None:
            setattr(cfg, f, v)
    if req.api_key:  # 仅传了新 key 才更新
        cfg.api_key_enc = encrypt_secret(req.api_key)
    db.commit()
    db.refresh(cfg)
    return _out(cfg)


@router.delete("/configs/{cfg_id}")
def delete_config(cfg_id: int, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    cfg = db.get(LLMConfig, cfg_id)
    if not cfg:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "配置不存在")
    db.delete(cfg)
    db.commit()
    return {"ok": True}


@router.post("/configs/{cfg_id}/test", response_model=TestResult)
async def test_config(cfg_id: int, db: Session = Depends(get_db),
                      user: User = Depends(get_current_user)):
    cfg = db.get(LLMConfig, cfg_id)
    if not cfg:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "配置不存在")
    ok, msg = await build_llm_client(cfg).test()
    return TestResult(ok=ok, message=msg)
