"""安全工具：密码哈希(bcrypt)、JWT(PyJWT)、密钥对称加密(Fernet)。"""
from __future__ import annotations

import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
import jwt
from cryptography.fernet import Fernet, InvalidToken

from .config import settings


# ---------- 密码 ----------
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


# ---------- JWT ----------
def create_access_token(subject: str, extra: Optional[dict[str, Any]] = None) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None


# ---------- 密钥对称加密（用于落库的第三方 Key）----------
def _fernet() -> Fernet:
    # 由 secret_key 派生 32 字节 urlsafe base64 key
    digest = hashlib.sha256(settings.secret_key.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_secret(plain: str) -> str:
    if plain is None:
        return ""
    return _fernet().encrypt(plain.encode("utf-8")).decode("utf-8")


def decrypt_secret(token: str) -> str:
    if not token:
        return ""
    try:
        return _fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return ""


def mask_secret(plain: str, keep: int = 4) -> str:
    """用于前端回显的脱敏：保留后 keep 位。"""
    if not plain:
        return ""
    if len(plain) <= keep:
        return "*" * len(plain)
    return "*" * (len(plain) - keep) + plain[-keep:]
