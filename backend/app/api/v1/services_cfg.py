"""LightPanda / Tavily 服务配置管理 + 连通性测试。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.deps import get_current_user, get_db
from ...core.security import decrypt_secret, encrypt_secret, mask_secret
from ...models import ServiceConfig, User
from ...schemas.config import (ServiceConfigIn, ServiceConfigOut, TestResult)
from ...services import service_tester

router = APIRouter(prefix="/services", tags=["services"])


def _out(c: ServiceConfig) -> ServiceConfigOut:
    o = ServiceConfigOut.model_validate(c)
    o.api_key_masked = mask_secret(decrypt_secret(c.api_key_enc))
    return o


@router.get("", response_model=list[ServiceConfigOut])
def list_services(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return [_out(c) for c in db.query(ServiceConfig).order_by(ServiceConfig.id.desc()).all()]


@router.post("", response_model=ServiceConfigOut, status_code=status.HTTP_201_CREATED)
def create_service(req: ServiceConfigIn, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    c = ServiceConfig(service=req.service, name=req.name, base_url=req.base_url,
                      api_key_enc=encrypt_secret(req.api_key), extra=req.extra,
                      enabled=req.enabled, owner_id=user.id)
    db.add(c)
    db.commit()
    db.refresh(c)
    return _out(c)


@router.patch("/{cfg_id}", response_model=ServiceConfigOut)
def update_service(cfg_id: int, req: ServiceConfigIn, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    c = db.get(ServiceConfig, cfg_id)
    if not c:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "配置不存在")
    c.service, c.name, c.base_url, c.extra, c.enabled = (
        req.service, req.name, req.base_url, req.extra, req.enabled)
    if req.api_key:
        c.api_key_enc = encrypt_secret(req.api_key)
    db.commit()
    db.refresh(c)
    return _out(c)


@router.delete("/{cfg_id}")
def delete_service(cfg_id: int, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    c = db.get(ServiceConfig, cfg_id)
    if not c:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "配置不存在")
    db.delete(c)
    db.commit()
    return {"ok": True}


@router.post("/{cfg_id}/test", response_model=TestResult)
async def test_service(cfg_id: int, db: Session = Depends(get_db),
                       user: User = Depends(get_current_user)):
    c = db.get(ServiceConfig, cfg_id)
    if not c:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "配置不存在")
    ok, msg = await service_tester.test_service(c)
    return TestResult(ok=ok, message=msg)
