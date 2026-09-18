"""数据库引擎与会话。"""
from __future__ import annotations

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from ..core.config import settings

connect_args = {}
if settings.database_url.startswith("sqlite"):
    # SQLite 多线程 + WAL
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    future=True,
)

if settings.database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _sqlite_connect_pragma(dbapi_conn, _record):
        # 每条池化连接都设置：写锁等待 10s（后台抓取与前台并发写不再立即报 locked）
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA busy_timeout=10000;")
        cur.close()

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


def enable_sqlite_wal() -> None:
    if settings.database_url.startswith("sqlite"):
        with engine.connect() as conn:
            conn.exec_driver_sql("PRAGMA journal_mode=WAL;")
            conn.exec_driver_sql("PRAGMA foreign_keys=ON;")
            # 后台抓取与前台写入并发时，写锁最多等待 10s 而不是立即报 database is locked
            conn.exec_driver_sql("PRAGMA busy_timeout=10000;")
