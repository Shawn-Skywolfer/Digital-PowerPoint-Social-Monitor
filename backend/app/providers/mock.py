"""Mock Provider：本地/无 Key 时返回确定性造数，用于联调与测试。

通过 settings.provider_mock=True 或无可用 Key 时启用。
"""
from __future__ import annotations

import hashlib
import random
from datetime import datetime, timedelta
from typing import Optional

from .base import (AccountInfo, ArticleInfo, CommentInfo, MetricsInfo,
                   SearchedArticle, SearchPage, SourceProvider)


def _rng(seed: str) -> random.Random:
    return random.Random(int(hashlib.md5(seed.encode()).hexdigest(), 16) % (10**8))


class MockProvider(SourceProvider):
    name = "mock"

    async def search_accounts(self, query: str, key: str) -> list[AccountInfo]:
        r = _rng("search:" + query)
        return [
            AccountInfo(
                biz="MOCKBIZ_" + hashlib.md5(query.encode()).hexdigest()[:10],
                name=query,
                gh_id="gh_" + hashlib.md5(query.encode()).hexdigest()[:8],
                intro=f"这是 {query} 的模拟公众号简介",
                verify="华为数字能源",
            )
        ]

    async def resolve_account(self, ref: str, key: str) -> Optional[AccountInfo]:
        return (await self.search_accounts(ref, key))[0]

    async def fetch_article_list(
        self, account: AccountInfo, key: str,
        time_start: Optional[datetime] = None,
        time_end: Optional[datetime] = None,
        need_content: bool = False,
    ) -> list[ArticleInfo]:
        r = _rng("list:" + account.biz)
        n = r.randint(8, 15)
        end = time_end or datetime.now()
        arts: list[ArticleInfo] = []
        for i in range(n):
            pub = end - timedelta(days=r.randint(0, 30), hours=r.randint(0, 23))
            if time_start and pub < time_start:
                continue
            url = f"https://mp.weixin.qq.com/s/{account.biz[:8]}-{i}"
            art = ArticleInfo(
                url=url, msgid=f"msg{i}", title=f"{account.name} 第{i+1}篇: 数字能源观察",
                author=account.name, publish_time=pub,
                digest="本文是关于数字能源的模拟摘要。",
            )
            if need_content:
                art.content_text = (f"这是《{art.title}》的模拟正文。" * 20)
                art.content_html = f"<p>{art.content_text}</p>"
            arts.append(art)
        return arts

    async def fetch_content(self, article: ArticleInfo, key: str) -> ArticleInfo:
        return ArticleInfo(
            url=article.url, title=article.title, msgid=article.msgid,
            author=article.author, publish_time=article.publish_time,
            digest=article.digest,
            content_text=(f"这是《{article.title}》的模拟正文。" * 20),
            content_html=f"<p>这是《{article.title}》的模拟正文。</p>",
        )

    async def fetch_metrics(self, article: ArticleInfo, key: str, fields: list[str]) -> MetricsInfo:
        r = _rng("metric:" + article.url)
        m = MetricsInfo()
        if "read_num" in fields:
            m.read_num = r.randint(200, 80000)
        if "like_num" in fields:
            m.like_num = r.randint(5, 2000)
        if "wow_num" in fields:
            m.wow_num = r.randint(2, 800)
        if "share_num" in fields:
            m.share_num = r.randint(0, 500)
        if "collect_num" in fields:
            m.collect_num = r.randint(0, 400)
        m.comment_count = r.randint(0, 120)
        return m

    async def fetch_comments(self, article: ArticleInfo, key: str) -> list[CommentInfo]:
        r = _rng("comment:" + article.url)
        n = r.randint(3, 20)
        out: list[CommentInfo] = []
        for i in range(n):
            out.append(CommentInfo(
                comment_id=f"c{i}", nickname=f"读者{i}",
                content=r.choice([
                    "写得很好，受教了！", "请问这个数据口径是？",
                    "数字能源确实是趋势。", "有点夸大了吧？", "收藏了，干货。",
                ]),
                like_num=r.randint(0, 200), is_sub=False,
                comment_time=datetime.now() - timedelta(hours=r.randint(1, 200)),
            ))
        return out

    async def search_articles(
        self, keyword: str, key: str, *,
        sort_type: int = 0, publish_time_type: int = 0,
        offset: int = 0, cookies_buffer: str = "", current_page: int = 1,
    ) -> SearchPage:
        """模拟搜一搜：确定性造 10 条/页，共 3 页，URL 带合法 __biz 便于入库联调。"""
        r = _rng(f"websearch:{keyword}")
        page_size, total = 10, 30
        start = max(offset, 0)
        items: list[SearchedArticle] = []
        for i in range(start, min(start + page_size, total)):
            biz = "MOCKBIZ_" + hashlib.md5(f"{keyword}:{i % 4}".encode()).hexdigest()[:10]
            url = (f"https://mp.weixin.qq.com/s?__biz={biz}&mid=2247{i:04d}"
                   f"&idx=1&sn={hashlib.md5(f'{keyword}:{i}'.encode()).hexdigest()[:16]}")
            items.append(SearchedArticle(
                url=url,
                title=f"{keyword} 相关文章 第{i+1}篇：行业观察与解读",
                account_name=f"{keyword}观察{i % 4}",
                biz=biz,
                digest=f"这是关于「{keyword}」的模拟搜索结果摘要，用于联调与测试。",
                publish_time=datetime.now() - timedelta(days=i, hours=r.randint(0, 23)),
                doc_id=f"mock-{i}",
            ))
        nxt = start + page_size
        return SearchPage(
            items=items,
            continue_flag=nxt < total,
            offset=nxt,
            cookies_buffer=(f"mockbuf-{nxt}" if nxt < total else ""),
            total=total,
            cost=0.0,
            remain=None,
        )
