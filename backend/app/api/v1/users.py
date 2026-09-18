"""用户管理（仅管理员）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.deps import get_db, require_admin
from ...core.security import hash_password
from ...models import AuditLog, User
from ...schemas.auth import UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return [UserOut.model_validate(u) for u in db.query(User).order_by(User.id).all()]


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(req: UserCreate, db: Session = Depends(get_db),
                admin: User = Depends(require_admin)):
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "用户名已存在")
    user = User(username=req.username, password_hash=hash_password(req.password),
                role=req.role, is_active=True)
    db.add(user)
    db.add(AuditLog(user_id=admin.id, action="create_user", detail=f"创建用户 {req.username}"))
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, req: UserUpdate, db: Session = Depends(get_db),
                admin: User = Depends(require_admin)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "用户不存在")
    if req.password:
        user.password_hash = hash_password(req.password)
    if req.role is not None:
        user.role = req.role
    if req.is_active is not None:
        user.is_active = req.is_active
    db.add(AuditLog(user_id=admin.id, action="update_user", detail=f"更新用户 {user.username}"))
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db),
                admin: User = Depends(require_admin)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "用户不存在")
    if user.id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "不能删除当前登录账户")
    db.delete(user)
    db.add(AuditLog(user_id=admin.id, action="delete_user", detail=f"删除用户 {user.username}"))
    db.commit()
    return {"ok": True}
