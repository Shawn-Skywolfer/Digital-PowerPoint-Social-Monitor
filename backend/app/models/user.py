"""用户与权限。"""
from __future__ import annotations

import enum

from sqlalchemy import Boolean, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base, TimestampMixin


class UserRole(str, enum.Enum):
    admin = "admin"
    member = "member"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.member)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # 首次登录是否需改密（默认管理员播种时置 True）
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False)
