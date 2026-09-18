"""关键词搜索（搜一搜）：文章检索预览 + 选中批量入库。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.deps import get_current_user, get_db
from ...models import User
from ...providers.base import ProviderError
from ...schemas.search import (ArticleSearchIn, ArticleSearchOut,
                               SearchedArticleOut, SearchImportIn,
                               SearchImportOut)
from ...services import search_service
from ...utils.wxcontent import canonical_url_key

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/articles", response_model=ArticleSearchOut)
async def search_articles(req: ArticleSearchIn, db: Session = Depends(get_db),
                          user: User = Depends(get_current_user)):
    """关键词搜索文章（搜一搜，0.5元/页）。纯预览不落库；翻页把响应里的
    offset/cookies_buffer/current_page+1 原样带回。"""
    try:
        page = await search_service.search_articles(
            db, req.keyword.strip(), owner_id=user.id, key_id=req.key_id,
            sort_type=req.sort_type, publish_time_type=req.publish_time_type,
            offset=req.offset, cookies_buffer=req.cookies_buffer,
            current_page=req.current_page,
        )
    except ProviderError as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"检索失败: {e}")

    in_lib = search_service.mark_in_library(db, page.items)
    items = []
    for it in page.items:
        key = canonical_url_key(it.url)
        items.append(SearchedArticleOut(
            url=it.url, title=it.title, account_name=it.account_name,
            digest=it.digest, publish_time=it.publish_time, cover=it.cover,
            in_library=key in in_lib, article_id=in_lib.get(key),
        ))
    return ArticleSearchOut(
        items=items, continue_flag=page.continue_flag, offset=page.offset,
        cookies_buffer=page.cookies_buffer, current_page=req.current_page,
        total=page.total, cost=page.cost, remain=page.remain,
    )


@router.post("/import", response_model=SearchImportOut)
def import_articles(req: SearchImportIn, db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    """把选中的搜索结果建档入库（不调付费接口）。返回文章 id 列表，
    供前端继续批量下载（建抓取任务）或批量分析（/analysis/run）。"""
    ids, new_count, existed_count, new_accounts = search_service.import_articles(
        db, req.items)
    return SearchImportOut(article_ids=ids, new_count=new_count,
                           existed_count=existed_count, new_accounts=new_accounts)
