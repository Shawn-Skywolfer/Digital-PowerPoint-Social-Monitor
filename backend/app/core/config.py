"""应用全局配置（pydantic-settings，支持 .env 与环境变量覆盖）。"""
from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _base_dir() -> Path:
    """项目/应用根目录。

    PyInstaller 打包（frozen）时以 exe 所在目录为根：
    数据库、导出文件都落在 exe 旁边的 data/ 下，.env 也可放旁边覆盖配置。
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    # backend/app/core/config.py 向上 3 级 = backend/，再上一级 = 项目根
    return Path(__file__).resolve().parents[3]


def _frontend_dist() -> Optional[Path]:
    """前端构建产物目录（存在 index.html 才认为可用）。"""
    candidates = []
    if getattr(sys, "frozen", False):
        # PyInstaller 打包时前端 dist 打进 _MEIPASS/web
        candidates.append(Path(getattr(sys, "_MEIPASS", "")) / "web")
    else:
        candidates.append(_base_dir() / "frontend" / "dist")
    for c in candidates:
        if (c / "index.html").is_file():
            return c
    return None


BASE_DIR = _base_dir()
FRONTEND_DIST = _frontend_dist()
DEFAULT_SQLITE = f"sqlite:///{BASE_DIR / 'data' / 'monitor.db'}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 基本
    app_name: str = "社媒监测洞察系统"
    app_env: str = "dev"
    api_prefix: str = "/api/v1"

    # 安全
    secret_key: str = "CHANGE-ME-in-.env"  # 用于 JWT 与 Fernet 派生
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 12  # 12 小时

    # 数据库（默认 SQLite，可切 PostgreSQL/MySQL）
    # 例：postgresql+psycopg://user:pass@host:5432/db  或  mysql+pymysql://user:pass@host/db
    database_url: str = DEFAULT_SQLITE

    @field_validator("database_url", mode="before")
    @classmethod
    def _default_db(cls, v):
        # .env 里留空时回退到默认 SQLite
        if v is None or (isinstance(v, str) and not v.strip()):
            return DEFAULT_SQLITE
        return v

    # 目录
    data_dir: str = str(BASE_DIR / "data")
    export_dir: str = str(BASE_DIR / "data" / "exports")

    # 默认管理员（首次启动播种）
    default_admin_username: str = "Admin"
    default_admin_password: str = "Seek22626301"
    force_change_default_password: bool = True

    # CORS（前端 dev 端口）
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # dajiala
    dajiala_base_url: str = "https://www.dajiala.com"
    # 无可用 Key 或本地调试时，使用 Mock Provider 返回造数
    provider_mock: bool = False

    # 出站 HTTP（本机/内网走代理 + 关 SSL 校验；云服务器直连则留空 proxy、verify 保持 true）
    http_proxy: str = ""           # 例 http://proxyjp.huawei.com:8080
    http_verify_ssl: bool = True   # 代理做 SSL MITM（如华为）时需置 false

    # 抓取默认
    fetch_default_page_size: int = 20
    fetch_max_pages_per_account: int = 50
    fetch_request_timeout: int = 30
    fetch_concurrency: int = 3  # 单任务内账号抓取并发

    # 分析默认
    analysis_concurrency: int = 3
    llm_request_timeout: int = 120

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def httpx_kwargs(self) -> dict:
        """出站 httpx 客户端通用参数（代理 + SSL 校验开关）。"""
        kw: dict = {"verify": self.http_verify_ssl}
        if self.http_proxy:
            kw["proxy"] = self.http_proxy
        return kw

    def ensure_dirs(self) -> None:
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.export_dir, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    s.ensure_dirs()
    return s


settings = get_settings()
