"""文章归一（url_key 跨任务去重）、全文抓取修复、删除后不再刷新 的回归测试。"""
import asyncio

import pytest

from app.db.session import SessionLocal
from app.models import (Account, Article, ArticleStatus, FetchTask,
                        MetricSnapshot, TaskStatus)
from app.providers.base import AccountInfo, ArticleInfo, MetricsInfo
from app.services import fetch_service
from app.services.fetch_service import run_fetch_task
from app.utils.wxcontent import canonical_url_key, html_to_text, looks_like_html

# ---------------- canonical_url_key ----------------

def test_canonical_key_ignores_volatile_params():
    u1 = ("http://mp.weixin.qq.com/s?__biz=MzA3&mid=100&idx=1&sn=abc123"
          "&chksm=111&scene=126&sessionid=999#rd")
    u2 = ("https://mp.weixin.qq.com/s?__biz=MzA3&mid=100&idx=1&sn=abc123"
          "&chksm=222&scene=27&sessionid=888#rd")
    assert canonical_url_key(u1) == canonical_url_key(u2) == "wx:MzA3|100|1|abc123"


def test_canonical_key_distinguishes_articles():
    u1 = "http://mp.weixin.qq.com/s?__biz=MzA3&mid=100&idx=1&sn=aaa"
    u2 = "http://mp.weixin.qq.com/s?__biz=MzA3&mid=101&idx=1&sn=aaa"
    u3 = "http://mp.weixin.qq.com/s?__biz=MzA3&mid=100&idx=2&sn=aaa"
    assert canonical_url_key(u1) != canonical_url_key(u2)
    assert canonical_url_key(u1) != canonical_url_key(u3)


def test_canonical_key_fallback_for_nonstandard_urls():
    assert canonical_url_key("https://mp.weixin.qq.com/s/ShortToken123") == \
        "url:https://mp.weixin.qq.com/s/ShortToken123"
    assert canonical_url_key("custom://abcdef").startswith("url:custom://")
    assert canonical_url_key("") == ""


# ---------------- html_to_text ----------------

def test_html_to_text_full_page():
    src = ('<!DOCTYPE html><html><head><title>t</title>'
           '<style>.x{color:red}</style></head>'
           '<body><section><p>第一段&nbsp;文字</p><p>第二段<img src="x.jpg"/></p>'
           '<script>var a=1;</script></section></body></html>')
    text = html_to_text(src)
    assert "第一段 文字" in text
    assert "第二段[图片]" in text.replace(" ", "") or "[图片]" in text
    assert "var a=1" not in text
    assert "color:red" not in text
    assert "<" not in text


def test_looks_like_html():
    assert looks_like_html("<!DOCTYPE html><html>...")
    assert looks_like_html("<section><p>x</p></section>")
    assert not looks_like_html("这是一段纯文本，没有标签")
    assert not looks_like_html("")


# ---------------- dajiala fetch_content 顶层字段形态 ----------------

async def test_dajiala_fetch_content_toplevel_shape(monkeypatch):
    """article_detail 实测返回顶层字段且 content 可能是整页 HTML。"""
    from app.providers.dajiala import DajialaProvider

    payload = {
        "code": 0, "title": "测试标题", "author": "测试作者",
        "content": ("<!DOCTYPE html><html><head></head><body>"
                    "<section><p>正文第一段。</p><p>正文第二段。</p>"
                    "</section></body></html>"),
        "content_multi_text": "<section><p>正文第一段。</p><p>正文第二段。</p></section>",
        "post_time_str": "2026-08-10 18:07:38",
    }
    p = DajialaProvider(base_url="https://example.com")

    async def fake_request(endpoint, params, key):
        assert endpoint == "post_detail_text"
        return payload

    monkeypatch.setattr(p, "_request", fake_request)
    art = await p.fetch_content(ArticleInfo(url="http://mp.weixin.qq.com/s?__biz=X&mid=1&idx=1&sn=y",
                                            title="t"), "k")
    assert art.content_text == "正文第一段。\n正文第二段。"
    assert art.content_html and "<section>" in art.content_html
    assert art.author == "测试作者"


async def test_dajiala_fetch_content_plain_text_shape():
    """文档示例形态：content 直接是纯文本。"""
    from app.providers.dajiala import DajialaProvider

    p = DajialaProvider(base_url="https://example.com")

    async def fake_request(endpoint, params, key):
        return {"code": 0, "content": "纯文本正文内容", "content_multi_text": ""}

    p._request = fake_request  # type: ignore
    art = await p.fetch_content(ArticleInfo(url="u", title="t"), "k")
    assert art.content_text == "纯文本正文内容"


# ---------------- 跨任务归一 + 刷新语义 ----------------

class _ChksmProvider:
    """同一篇文章每次返回不同 chksm 的 URL，复现真实 post_history 行为。"""
    name = "chksm"

    def __init__(self, session_no: int):
        self.session_no = session_no

    async def fetch_article_list(self, account, key, time_start=None, time_end=None,
                                 need_content=False):
        url = (f"http://mp.weixin.qq.com/s?__biz=BIZ1&mid=500&idx=1&sn=sn001"
               f"&chksm=vary{self.session_no}&scene=126&sessionid={self.session_no}#rd")
        return [ArticleInfo(url=url, msgid="sn001", title="归一测试文章")]

    async def fetch_content(self, article, key):
        return ArticleInfo(url=article.url, title=article.title,
                           content_text="正文内容" * 10)

    async def fetch_metrics(self, article, key, fields):
        return MetricsInfo(read_num=100 + self.session_no, like_num=5)

    async def fetch_comments(self, article, key):
        return []


def _make_task(fields, account_id):
    db = SessionLocal()
    try:
        task = FetchTask(owner_id=None, account_ids=[account_id], fields=fields,
                         status=TaskStatus.pending)
        db.add(task)
        db.commit()
        db.refresh(task)
        return task.id
    finally:
        db.close()


def _get_account(name: str) -> int:
    db = SessionLocal()
    try:
        acc = db.query(Account).filter(Account.name == name).first()
        assert acc is not None
        return acc.id
    finally:
        db.close()


async def test_same_article_across_tasks_merges(client, auth_headers, monkeypatch):
    client.post("/api/v1/accounts/import", headers=auth_headers,
                json={"lines": ["归一测试号"]})
    acc_id = _get_account("归一测试号")

    providers = [_ChksmProvider(1), _ChksmProvider(2)]
    calls = {"n": 0}

    def next_provider(_name=None):
        p = providers[min(calls["n"], 1)]
        calls["n"] += 1
        return p

    monkeypatch.setattr(fetch_service, "get_provider", next_provider)

    # 任务1：只要标题；任务2：带指标——同一篇文章应归一到同一行并刷新数据
    t1 = _make_task(["title", "publish_time"], acc_id)
    await run_fetch_task(t1, asyncio.Event())
    t2 = _make_task(["title", "read_num", "like_num"], acc_id)
    await run_fetch_task(t2, asyncio.Event())

    db = SessionLocal()
    try:
        arts = db.query(Article).filter(Article.account_id == acc_id).all()
        assert len(arts) == 1, f"应归一为 1 行，实际 {len(arts)} 行"
        snaps = db.query(MetricSnapshot).filter(
            MetricSnapshot.article_id == arts[0].id).all()
        assert len(snaps) == 1  # 只有任务2抓了指标
        assert snaps[0].read_num == 102
    finally:
        db.close()


async def test_pending_review_article_not_refreshed(client, auth_headers, monkeypatch):
    """疑似删除（待确认）的文章：即使又出现在列表里，也不花钱刷新，等待人工裁决。"""
    acc_id = _get_account("归一测试号")
    db = SessionLocal()
    art = db.query(Article).filter(Article.account_id == acc_id).first()
    art.status = ArticleStatus.pending_review
    db.commit()
    art_id = art.id
    n_snaps = db.query(MetricSnapshot).filter(MetricSnapshot.article_id == art_id).count()
    db.close()

    provider = _ChksmProvider(3)
    monkeypatch.setattr(fetch_service, "get_provider", lambda _name=None: provider)
    t = _make_task(["title", "read_num"], acc_id)
    await run_fetch_task(t, asyncio.Event())

    db = SessionLocal()
    try:
        art = db.get(Article, art_id)
        assert art.status == ArticleStatus.pending_review  # 不自动恢复
        assert db.query(MetricSnapshot).filter(
            MetricSnapshot.article_id == art_id).count() == n_snaps  # 没有新快照
    finally:
        db.close()


async def test_deleted_article_recovers_when_relisted(client, auth_headers, monkeypatch):
    """已确认删除的文章重新出现在发文列表 → 自动恢复正常并恢复刷新。"""
    acc_id = _get_account("归一测试号")
    db = SessionLocal()
    art = db.query(Article).filter(Article.account_id == acc_id).first()
    art.status = ArticleStatus.deleted
    db.commit()
    art_id = art.id
    n_snaps = db.query(MetricSnapshot).filter(MetricSnapshot.article_id == art_id).count()
    db.close()

    provider = _ChksmProvider(4)
    monkeypatch.setattr(fetch_service, "get_provider", lambda _name=None: provider)
    t = _make_task(["title", "read_num"], acc_id)
    await run_fetch_task(t, asyncio.Event())

    db = SessionLocal()
    try:
        art = db.get(Article, art_id)
        assert art.status == ArticleStatus.normal
        assert db.query(MetricSnapshot).filter(
            MetricSnapshot.article_id == art_id).count() == n_snaps + 1
    finally:
        db.close()


async def test_export_includes_content_text(client, auth_headers):
    resp = client.get("/api/v1/export/articles", headers=auth_headers,
                      params={"fmt": "csv"})
    assert resp.status_code == 200
    header = resp.content.decode("utf-8-sig").splitlines()[0]
    assert "正文" in header
