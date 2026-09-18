"""dajiala Key 池：选择可用 Key、记录用量。"""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from ..core.security import decrypt_secret
from ..models.config import DajialaKey, KeyStatus


def pick_key(
    db: Session,
    owner_id: Optional[int] = None,
    key_id: Optional[int] = None,
) -> Optional[DajialaKey]:
    """按优先级选一个可用 Key：显式指定 > 用户默认 > 用户任一 > 全局默认 > 全局任一。"""
    def usable(q):
        return q.filter(DajialaKey.enabled.is_(True),
                        DajialaKey.status != KeyStatus.exhausted,
                        DajialaKey.status != KeyStatus.invalid)

    if key_id is not None:
        k = usable(db.query(DajialaKey)).filter(DajialaKey.id == key_id).first()
        if k:
            return k
    base = usable(db.query(DajialaKey))
    if owner_id is not None:
        mine = base.filter(DajialaKey.owner_id == owner_id)
        k = mine.filter(DajialaKey.is_default.is_(True)).first() or mine.first()
        if k:
            return k
    return (base.filter(DajialaKey.is_default.is_(True)).first()
            or base.order_by(DajialaKey.used.asc()).first())


def get_key_value(key: Optional[DajialaKey]) -> Optional[str]:
    return decrypt_secret(key.key_enc) if key else None


def record_usage(db: Session, key_id: Optional[int], amount: int = 1) -> None:
    if key_id is None:
        return
    k = db.query(DajialaKey).filter(DajialaKey.id == key_id).first()
    if not k:
        return
    k.used = (k.used or 0) + amount
    if k.quota is not None and k.used >= k.quota:
        k.status = KeyStatus.exhausted
    db.commit()


def mark_status(db: Session, key_id: Optional[int], status: KeyStatus) -> None:
    if key_id is None:
        return
    k = db.query(DajialaKey).filter(DajialaKey.id == key_id).first()
    if k:
        k.status = status
        db.commit()
