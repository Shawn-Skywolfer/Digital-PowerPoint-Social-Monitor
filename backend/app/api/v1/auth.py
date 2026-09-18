"""认证：登录 / 当前用户 / 改密。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.deps import get_current_user, get_db
from ...core.security import (create_access_token, hash_password,
                              verify_password)
from ...models import AuditLog, User
from ...schemas.auth import (ChangePasswordRequest, LoginRequest, TokenResponse,
                             UserOut)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "账号已停用")
    token = create_access_token(subject=user.username, extra={"role": user.role.value})
    db.add(AuditLog(user_id=user.id, action="login", detail=f"{user.username} 登录"))
    db.commit()
    return TokenResponse(
        access_token=token,
        must_change_password=user.must_change_password,
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)


@router.post("/change-password")
def change_password(req: ChangePasswordRequest,
                    user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if not verify_password(req.old_password, user.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "原密码错误")
    user.password_hash = hash_password(req.new_password)
    user.must_change_password = False
    db.add(AuditLog(user_id=user.id, action="change_password", detail="修改密码"))
    db.commit()
    return {"ok": True, "message": "密码已更新"}
