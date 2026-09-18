"""被监测的公众号 + 公众号分组。"""
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base, TimestampMixin


class AccountGroup(Base, TimestampMixin):
    """公众号分组（一个公众号至多属于一个分组）。"""
    __tablename__ = "account_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    accounts = relationship("Account", back_populates="group")


class Account(Base, TimestampMixin):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # dajiala/微信侧的稳定标识：biz 唯一
    biz: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    gh_id: Mapped[str | None] = mapped_column(String(128), nullable=True)  # 微信号
    avatar: Mapped[str | None] = mapped_column(String(512), nullable=True)
    intro: Mapped[str | None] = mapped_column(Text, nullable=True)
    verify: Mapped[str | None] = mapped_column(String(255), nullable=True)  # 认证信息
    profile_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    group_id: Mapped[int | None] = mapped_column(ForeignKey("account_groups.id"), nullable=True)
    tags: Mapped[str | None] = mapped_column(String(512), nullable=True)  # 逗号分隔
    is_monitoring: Mapped[bool] = mapped_column(Boolean, default=True)
    # 系统内置账号（如"自定义内容"载体），不出现在公众号管理列表
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)

    group = relationship("AccountGroup", back_populates="accounts")
    articles = relationship("Article", back_populates="account", cascade="all, delete-orphan")
