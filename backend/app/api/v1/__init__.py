"""聚合 v1 下所有业务路由。"""
from __future__ import annotations

from fastapi import APIRouter

from . import (accounts, analysis, articles, auth, dashboard, export, fetch,
               keys, llm, mcp, reviews, scheduler, search, services_cfg, users)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(accounts.router)
api_router.include_router(fetch.router)
api_router.include_router(articles.router)
api_router.include_router(export.router)
api_router.include_router(analysis.router)
api_router.include_router(llm.router)
api_router.include_router(keys.router)
api_router.include_router(mcp.router)
api_router.include_router(services_cfg.router)
api_router.include_router(scheduler.router)
api_router.include_router(reviews.router)
api_router.include_router(dashboard.router)
api_router.include_router(search.router)
