"""关键词搜索工作流：搜一搜预览（不落库）+ 选中文章建档入库。

设计要点：
  * 搜索只预览，不写库、不产生除搜索本身外的费用（0.5元/页）；
  * 入库（import）只做「建档」——文章+公众号落库，正文/指标/评论由用户
    再通过批量下载（复用抓取任务）按需花钱抓取；
  * 公众号按 URL 里的 __biz 归一建档：已存在则复用，不存在则新建
    （is_monitoring=False，出现在公众号管理列表但默认不参与定时抓取）；
    URL 解析不出 biz 的进系统兜底账号「搜索导入」（is_system=True，不出现在列表）。
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.logging import get_logger
from ..models import Account, Article
from ..providers.base import (ArticleInfo, ProviderError, SearchedArticle,
                              SearchPage)
from ..providers.registry import get_provider
from ..schemas.search import SearchImportItem
from ..utils.wxcontent import biz_from_url, canonical_url_key
from . import key_service
from .fetch_service import _upsert_article

logger = get_logger(__name__)

# 解析不出 biz 时的兜底系统账号（所有无法归属的搜索文章都挂这里）
SEARCH_IMPORT_BIZ = "SEARCH_IMPORT"
SEARCH_IMPORT_NAME = "搜索导入"


def _pick_provider(db: Session, owner_id: Optional[int], key_id: Optional[int]):
    """选 Key + Provider（与抓取任务同一套逻辑）。返回 (provider, key_value, key_id)。"""
    key = key_service.pick_key(db, owner_id=owner_id, key_id=key_id)
    key_value = key_service.get_key_value(key)
    provider = get_provider(None if (key_value or not settings.provider_mock) else "mock")
    if settings.provider_mock:
        provider = get_provider("mock")
    return provider, key_value, (key.id if key else None)


async def search_articles(
    db: Session, keyword: str, *, owner_id: Optional[int], key_id: Optional[int],
    sort_type: int = 0, publish_time_type: int = 0,
    offset: int = 0, cookies_buffer: str = "", current_page: int = 1,
) -> SearchPage:
    """按关键词搜索文章（纯预览，不落库）。翻页游标原样透传给 Provider。"""
    provider, key_value, used_key_id = _pick_provider(db, owner_id, key_id)
    if not key_value and not settings.provider_mock:
        raise ProviderError("暂无可用 dajiala Key，请先在「设置-密钥管理」配置")
    page = await provider.search_articles(
        keyword, key_value or "",
        sort_type=sort_type, publish_time_type=publish_time_type,
        offset=offset, cookies_buffer=cookies_buffer, current_page=current_page,
    )
    key_service.record_usage(db, used_key_id, 1)
    return page


def mark_in_library(db: Session, items: list[SearchedArticle]) -> dict[str, int]:
    """按稳定身份键批量匹配文章库，返回 {url_key: article_id}。"""
    keys = {canonical_url_key(it.url) for it in items if it.url}
    keys.discard("")
    if not keys:
        return {}
    rows = db.query(Article.url_key, Article.id).filter(Article.url_key.in_(keys)).all()
    return {r[0]: r[1] for r in rows}


def _ensure_account(db: Session, item: SearchImportItem,
                    cache: dict[str, Account]) -> tuple[Account, bool]:
    """按 URL 的 __biz 找/建公众号。返回 (account, is_new)。"""
    biz = biz_from_url(item.url) or SEARCH_IMPORT_BIZ
    if biz in cache:
        return cache[biz], False
    acc = db.query(Account).filter(Account.biz == biz).first()
    is_new = acc is None
    if is_new:
        if biz == SEARCH_IMPORT_BIZ:
            acc = Account(biz=biz, name=SEARCH_IMPORT_NAME,
                          is_monitoring=False, is_system=True)
        else:
            acc = Account(biz=biz, name=item.account_name or "未知公众号",
                          is_monitoring=False, is_system=False)
        db.add(acc)
        db.flush()
        logger.info("搜索导入新建公众号: %s (%s)", acc.name, biz)
    cache[biz] = acc
    return acc, is_new


def import_articles(db: Session, items: list[SearchImportItem]) -> tuple[list[int], int, int, int]:
    """选中文章建档入库（不调付费接口）。返回 (article_ids, 新增, 已存在, 新建公众号数)。"""
    article_ids: list[int] = []
    new_count = existed_count = new_accounts = 0
    acc_cache: dict[str, Account] = {}
    for it in items:
        acc, acc_new = _ensure_account(db, it, acc_cache)
        new_accounts += 1 if acc_new else 0
        info = ArticleInfo(url=it.url, title=it.title,
                           author=it.account_name or None,
                           publish_time=it.publish_time, cover=it.cover,
                           digest=it.digest)
        art, is_new = _upsert_article(db, acc.id, info)
        article_ids.append(art.id)
        if is_new:
            new_count += 1
        else:
            existed_count += 1
    db.commit()
    logger.info("搜索导入: 入库 %d 篇（新 %d / 已存在 %d），新建公众号 %d 个",
                len(article_ids), new_count, existed_count, new_accounts)
    return article_ids, new_count, existed_count, new_accounts
