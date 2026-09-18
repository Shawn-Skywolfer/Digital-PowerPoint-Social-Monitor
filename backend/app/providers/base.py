"""数据源 Provider 抽象层。

所有数据源（公众号 dajiala、视频号、FireCrawl、Tavily、LightPanda…）都实现
`SourceProvider` 接口，以统一的规范化数据结构返回，主流程与具体平台解耦。
新增平台时只需新增一个 provider 并注册到 registry。
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


# ---------- 规范化数据结构 ----------
@dataclass
class AccountInfo:
    biz: str
    name: str
    gh_id: Optional[str] = None
    avatar: Optional[str] = None
    intro: Optional[str] = None
    verify: Optional[str] = None
    profile_url: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class ArticleInfo:
    url: str
    title: str
    msgid: Optional[str] = None
    author: Optional[str] = None
    publish_time: Optional[datetime] = None
    cover: Optional[str] = None
    digest: Optional[str] = None
    content_html: Optional[str] = None
    content_text: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricsInfo:
    read_num: Optional[int] = None
    like_num: Optional[int] = None
    wow_num: Optional[int] = None
    share_num: Optional[int] = None
    collect_num: Optional[int] = None
    comment_count: Optional[int] = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class CommentInfo:
    comment_id: str
    nickname: Optional[str] = None
    content: Optional[str] = None
    like_num: Optional[int] = None
    is_sub: bool = False
    parent_id: Optional[str] = None
    comment_time: Optional[datetime] = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchedArticle:
    """关键词搜索命中的文章（搜一搜结果，尚未入库）。"""
    url: str
    title: str
    account_name: str = ""                 # 公众号名（搜一搜 item.source.title）
    biz: Optional[str] = None              # 从 doc_url 的 __biz 参数解析
    digest: Optional[str] = None
    publish_time: Optional[datetime] = None
    cover: Optional[str] = None
    doc_id: Optional[str] = None           # 搜一搜侧文档 id（排查用）
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchPage:
    """一页搜索结果 + 翻页游标（搜一搜翻页靠 offset + cookies_buffer）。"""
    items: list[SearchedArticle]
    continue_flag: bool = False            # 是否还有下一页
    offset: int = 0                        # 下一页 offset
    cookies_buffer: str = ""               # 下一页 cookies_buffer
    total: Optional[int] = None            # 命中总数（搜一搜 totalCount，约为约数）
    cost: Optional[float] = None           # 本次调用扣费（元）
    remain: Optional[float] = None         # 调用后余额（元）


# ---------- 异常 ----------
class ProviderError(Exception):
    """数据源调用失败（网络/限频/鉴权/解析）。"""


class ProviderAuthError(ProviderError):
    """Key 无效或鉴权失败。"""


class ProviderQuotaError(ProviderError):
    """配额/积分不足。"""


class ArticleDeletedError(ProviderError):
    """目标文章已被删除/不可见（重抓时用于触发待确认）。"""


# ---------- Provider 接口 ----------
class SourceProvider(abc.ABC):
    """数据源抽象。所有方法都是 async，key 为解密后的平台凭证。"""
    name: str = "base"

    @abc.abstractmethod
    async def search_accounts(self, query: str, key: str) -> list[AccountInfo]:
        """按关键字搜索公众号。"""

    @abc.abstractmethod
    async def resolve_account(self, ref: str, key: str) -> Optional[AccountInfo]:
        """按名称/微信号/链接解析出唯一公众号（用于导入校验）。"""

    @abc.abstractmethod
    async def fetch_article_list(
        self,
        account: AccountInfo,
        key: str,
        time_start: Optional[datetime] = None,
        time_end: Optional[datetime] = None,
        need_content: bool = False,
    ) -> list[ArticleInfo]:
        """抓取某公众号在 [time_start, time_end] 内的发文列表（可选含正文）。"""

    @abc.abstractmethod
    async def fetch_metrics(
        self, article: ArticleInfo, key: str, fields: list[str]
    ) -> MetricsInfo:
        """抓取单篇文章的互动指标（read/like/wow/share/collect/comment_count）。"""

    @abc.abstractmethod
    async def fetch_content(self, article: ArticleInfo, key: str) -> ArticleInfo:
        """抓取单篇文章的正文（返回填充了 content_text/content_html 的 ArticleInfo）。"""

    @abc.abstractmethod
    async def fetch_comments(self, article: ArticleInfo, key: str) -> list[CommentInfo]:
        """抓取单篇文章的评论（含二级）。"""

    async def search_articles(
        self, keyword: str, key: str, *,
        sort_type: int = 0, publish_time_type: int = 0,
        offset: int = 0, cookies_buffer: str = "", current_page: int = 1,
    ) -> "SearchPage":
        """按关键词搜索文章（搜一搜）。非所有平台都支持，默认抛错。"""
        raise NotImplementedError(f"{self.name} 不支持文章关键词搜索")
