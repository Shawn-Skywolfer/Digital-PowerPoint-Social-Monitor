"""关键词搜索（搜一搜）：API + 入库流程测试。

conftest 里 PROVIDER_MOCK=true，搜索走 MockProvider（确定性造数，不花钱）。
"""
import asyncio

from app.db.session import SessionLocal
from app.models import (Account, Article, FetchTask, MetricSnapshot, TaskStatus)
from app.services.fetch_service import run_article_download
from app.services.search_service import SEARCH_IMPORT_BIZ
from app.utils.wxcontent import biz_from_url, canonical_url_key

KW = "数字能源"


def test_search_articles_mock(client, auth_headers):
    resp = client.post("/api/v1/search/articles",
                       json={"keyword": KW, "sort_type": 1, "publish_time_type": 2},
                       headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["items"], "mock 应返回搜索结果"
    assert data["continue_flag"] is True
    assert data["offset"] > 0
    assert data["cookies_buffer"]
    assert data["total"] == 30
    first = data["items"][0]
    assert first["url"].startswith("https://mp.weixin.qq.com/s")
    assert first["account_name"]
    assert "<em" not in first["title"]
    assert first["in_library"] is False


def test_search_pagination_cursor(client, auth_headers):
    """把上一页响应的 offset/cookies_buffer 原样带回，取到下一页不同的文章。"""
    p1 = client.post("/api/v1/search/articles", json={"keyword": KW},
                     headers=auth_headers).json()
    p2 = client.post("/api/v1/search/articles", json={
        "keyword": KW, "offset": p1["offset"],
        "cookies_buffer": p1["cookies_buffer"], "current_page": 2,
    }, headers=auth_headers).json()
    assert p2["items"], "第二页应有数据"
    urls1 = {it["url"] for it in p1["items"]}
    urls2 = {it["url"] for it in p2["items"]}
    assert not (urls1 & urls2), "两页文章不应重复"


def test_import_creates_accounts_and_articles(client, auth_headers):
    """选中结果入库：建档文章 + 按 __biz 自动建档公众号（不监控、非系统）。"""
    items = client.post("/api/v1/search/articles", json={"keyword": KW},
                        headers=auth_headers).json()["items"][:3]
    resp = client.post("/api/v1/search/import", json={"items": items},
                       headers=auth_headers)
    assert resp.status_code == 200, resp.text
    out = resp.json()
    assert len(out["article_ids"]) == 3
    assert out["new_count"] == 3
    assert out["existed_count"] == 0
    assert out["new_accounts"] >= 1

    db = SessionLocal()
    try:
        art = db.get(Article, out["article_ids"][0])
        assert art is not None
        assert art.url_key == canonical_url_key(art.url)
        acc = db.get(Account, art.account_id)
        assert acc.is_monitoring is False
        assert acc.is_system is False
        assert acc.biz == biz_from_url(art.url)
        assert art.content_fetched is False  # 仅建档，不抓正文
    finally:
        db.close()

    # 重复导入 → 归一到已有文章，不重复建行
    again = client.post("/api/v1/search/import", json={"items": items},
                        headers=auth_headers).json()
    assert again["new_count"] == 0
    assert again["existed_count"] == 3
    assert again["article_ids"] == out["article_ids"]

    # 入库后再搜索 → in_library 标记命中
    found = client.post("/api/v1/search/articles", json={"keyword": KW},
                        headers=auth_headers).json()["items"]
    marked = [it for it in found if it["in_library"]]
    assert len(marked) >= 3
    assert all(it["article_id"] for it in marked)


def test_import_fallback_account_for_unparseable_url(client, auth_headers):
    """URL 解析不出 biz 的文章进系统兜底账号「搜索导入」（不出现在公众号管理）。"""
    item = {"url": "https://example.com/weird-article-1",
            "title": "无 biz 的文章", "account_name": "未知来源"}
    resp = client.post("/api/v1/search/import", json={"items": [item]},
                       headers=auth_headers)
    assert resp.status_code == 200, resp.text
    aid = resp.json()["article_ids"][0]
    db = SessionLocal()
    try:
        art = db.get(Article, aid)
        acc = db.get(Account, art.account_id)
        assert acc.biz == SEARCH_IMPORT_BIZ
        assert acc.is_system is True
        assert acc.is_monitoring is False
    finally:
        db.close()


def test_search_requires_keyword(client, auth_headers):
    resp = client.post("/api/v1/search/articles", json={"keyword": ""},
                       headers=auth_headers)
    assert resp.status_code == 422


def test_import_rejects_empty(client, auth_headers):
    resp = client.post("/api/v1/search/import", json={"items": []},
                       headers=auth_headers)
    assert resp.status_code == 422


async def test_article_download_channel(client, auth_headers):
    """批量下载通道：按文章清单补抓正文/指标/评论（mock 数据源，确定性）。"""
    items = client.post("/api/v1/search/articles", json={"keyword": "储能"},
                        headers=auth_headers).json()["items"][:2]
    ids = client.post("/api/v1/search/import", json={"items": items},
                      headers=auth_headers).json()["article_ids"]
    assert len(ids) == 2

    db = SessionLocal()
    try:
        task = FetchTask(owner_id=None, account_ids=[], article_ids=ids,
                         fields=["content", "read_num", "like_num", "comment"],
                         status=TaskStatus.pending)
        db.add(task)
        db.commit()
        db.refresh(task)
        task_id = task.id
    finally:
        db.close()

    await run_article_download(task_id, asyncio.Event())

    db = SessionLocal()
    try:
        task = db.get(FetchTask, task_id)
        assert task.status == TaskStatus.success, task.error or task.log
        assert task.done_items == 2
        arts = db.query(Article).filter(Article.id.in_(ids)).all()
        assert len(arts) == 2
        assert all(a.content_fetched for a in arts), "正文应已补抓"
        snaps = db.query(MetricSnapshot).filter(MetricSnapshot.article_id.in_(ids)).all()
        assert len(snaps) >= 2, "应有指标快照"
        assert all(s.read_num is not None for s in snaps)
    finally:
        db.close()
