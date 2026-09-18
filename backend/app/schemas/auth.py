"""认证与用户相关 schema。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ..models.user import UserRole


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    must_change_password: bool = False
    user: "UserOut"


class UserOut(BaseModel):
    id: int
    username: str
    role: UserRole
    is_active: bool
    must_change_password: bool = False
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    role: UserRole = UserRole.member


class UserUpdate(BaseModel):
    password: Optional[str] = Field(default=None, min_length=6, max_length=128)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6, max_length=128)


TokenResponse.model_rebuild()
