"""关键词搜索（搜一搜）schema。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ArticleSearchIn(BaseModel):
    keyword: str = Field(min_length=1, max_length=100)
    sort_type: int = Field(default=0, ge=0, le=2)            # 0综合/1最新/2最热
    publish_time_type: int = Field(default=0, ge=0, le=3)    # 0不限/1最近1天/2最近7天/3最近半年
    offset: int = Field(default=0, ge=0)                     # 翻页游标（上一页响应带回）
    cookies_buffer: str = ""                                 # 翻页游标（上一页响应带回）
    current_page: int = Field(default=1, ge=1)
    key_id: Optional[int] = None


class SearchedArticleOut(BaseModel):
    url: str
    title: str
    account_name: str = ""
    digest: Optional[str] = None
    publish_time: Optional[datetime] = None
    cover: Optional[str] = None
    in_library: bool = False          # 是否已在文章库
    article_id: Optional[int] = None  # 已入库时的文章 id


class ArticleSearchOut(BaseModel):
    items: list[SearchedArticleOut]
    continue_flag: bool = False       # 是否还有下一页
    offset: int = 0                   # 下一页游标（原样回传）
    cookies_buffer: str = ""          # 下一页游标（原样回传）
    current_page: int = 1
    total: Optional[int] = None       # 命中总数（约数）
    cost: Optional[float] = None      # 本次扣费（元）
    remain: Optional[float] = None    # 余额（元）


class SearchImportItem(BaseModel):
    url: str = Field(min_length=1, max_length=2048)
    title: str = Field(default="(无标题)", max_length=500)
    account_name: str = Field(default="", max_length=255)
    digest: Optional[str] = None
    publish_time: Optional[datetime] = None
    cover: Optional[str] = None


class SearchImportIn(BaseModel):
    """批量入库（仅建档，不抓正文/指标；那些走批量下载）。"""
    items: list[SearchImportItem] = Field(min_length=1, max_length=50)


class SearchImportOut(BaseModel):
    article_ids: list[int]
    new_count: int
    existed_count: int
    new_accounts: int
