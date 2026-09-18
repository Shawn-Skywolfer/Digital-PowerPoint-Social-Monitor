"""FastAPI 应用入口。"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.logging import get_logger, setup_logging
from .db.init_db import init_db

logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("启动 %s (env=%s)", settings.app_name, settings.app_env)
    init_db()
    # 启动定时任务调度器
    from .tasks.scheduler import start_scheduler
    start_scheduler()
    logger.info("初始化完成")
    yield
    from .tasks.scheduler import shutdown_scheduler
    shutdown_scheduler()
    logger.info("已停止")


app = FastAPI(
    title=settings.app_name,
    version="0.4.1",
    lifespan=lifespan,
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health() -> dict:
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}


# 业务路由
from .api.v1 import api_router  # noqa: E402

app.include_router(api_router, prefix=settings.api_prefix)


# ============ 前端静态托管（生产/桌面打包模式：前后端同端口） ============
# 开发模式（vite dev）下 frontend/dist 可能不存在，则跳过；
# 打包模式下前端 dist 内嵌，catch-all 路由必须在所有 API 路由之后注册。
from .core.config import FRONTEND_DIST  # noqa: E402

if FRONTEND_DIST:
    from fastapi.responses import FileResponse  # noqa: E402
    from fastapi.staticfiles import StaticFiles  # noqa: E402

    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str):
        # 未知 API 路径返回 404 而不是 index.html
        if full_path.startswith(("api/", "docs", "openapi.json")):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="接口不存在")
        # 真实静态文件（favicon、图片等）直接返回，其余一律回退 index.html（SPA 路由）
        if full_path:
            file = FRONTEND_DIST / full_path
            if file.is_file():
                return FileResponse(file)
        return FileResponse(FRONTEND_DIST / "index.html")
