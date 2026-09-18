"""dajiala 多 Key 池管理 + 校验。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.deps import get_current_user, get_db
from ...core.security import decrypt_secret, encrypt_secret, mask_secret
from ...db.base import utcnow
from ...models import DajialaKey, KeyStatus, User
from ...providers.base import ProviderError
from ...providers.registry import get_provider
from ...schemas.config import KeyIn, KeyOut, KeyUpdate, TestResult

router = APIRouter(prefix="/keys", tags=["keys"])


def _out(k: DajialaKey) -> KeyOut:
    o = KeyOut.model_validate(k)
    o.key_masked = mask_secret(decrypt_secret(k.key_enc))
    return o


def _clear_other_defaults(db: Session, keep_id: int) -> None:
    db.query(DajialaKey).filter(DajialaKey.id != keep_id,
                                DajialaKey.is_default.is_(True)
                                ).update({DajialaKey.is_default: False},
                                         synchronize_session=False)


@router.get("", response_model=list[KeyOut])
def list_keys(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # 成员看自己的 + 全局默认；管理员看全部
    q = db.query(DajialaKey)
    if user.role.value != "admin":
        q = q.filter((DajialaKey.owner_id == user.id) | (DajialaKey.is_default.is_(True)))
    return [_out(k) for k in q.order_by(DajialaKey.id.desc()).all()]


@router.post("", response_model=KeyOut, status_code=status.HTTP_201_CREATED)
def create_key(req: KeyIn, db: Session = Depends(get_db),
               user: User = Depends(get_current_user)):
    k = DajialaKey(label=req.label, key_enc=encrypt_secret(req.key),
                   owner_id=user.id, quota=req.quota, is_default=req.is_default,
                   note=req.note, status=KeyStatus.unknown)
    db.add(k)
    db.flush()
    if k.is_default:
        _clear_other_defaults(db, k.id)
    db.commit()
    db.refresh(k)
    return _out(k)


@router.patch("/{key_id}", response_model=KeyOut)
def update_key(key_id: int, req: KeyUpdate, db: Session = Depends(get_db),
               user: User = Depends(get_current_user)):
    k = db.get(DajialaKey, key_id)
    if not k:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Key 不存在")
    if req.label is not None:
        k.label = req.label
    if req.quota is not None:
        k.quota = req.quota
    if req.note is not None:
        k.note = req.note
    if req.enabled is not None:
        k.enabled = req.enabled
    if req.key:
        k.key_enc = encrypt_secret(req.key)
        k.status = KeyStatus.unknown  # 重新校验
    if req.is_default is not None:
        k.is_default = req.is_default
        if k.is_default:
            _clear_other_defaults(db, k.id)
    db.commit()
    db.refresh(k)
    return _out(k)


@router.delete("/{key_id}")
def delete_key(key_id: int, db: Session = Depends(get_db),
               user: User = Depends(get_current_user)):
    k = db.get(DajialaKey, key_id)
    if not k:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Key 不存在")
    db.delete(k)
    db.commit()
    return {"ok": True}


@router.post("/{key_id}/check", response_model=TestResult)
async def check_key(key_id: int, db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    """用一个轻量调用校验 Key 是否有效。"""
    k = db.get(DajialaKey, key_id)
    if not k:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Key 不存在")
    provider = get_provider("dajiala")
    try:
        # 用免费的余额查询校验 Key（避免 search_accounts 按条扣费）
        bal = await provider.get_balance(decrypt_secret(k.key_enc))
        k.status = KeyStatus.active
        k.last_check = utcnow()
        db.commit()
        remain = bal.get("remain_money")
        msg = "Key 有效" + (f"，余额 ¥{remain}" if remain is not None else "")
        return TestResult(ok=True, message=msg)
    except ProviderError as e:
        msg = str(e)
        if "鉴权" in msg or "授权" in msg:
            k.status = KeyStatus.invalid
        elif "配额" in msg or "积分" in msg:
            k.status = KeyStatus.exhausted
        k.last_check = utcnow()
        db.commit()
        return TestResult(ok=False, message=msg)
