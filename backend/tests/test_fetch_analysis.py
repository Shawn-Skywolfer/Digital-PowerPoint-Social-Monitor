"""抓取工作流 + 分析工作流测试（使用 mock 数据源与 mock LLM）。"""
import asyncio

import pytest

from app.db.session import SessionLocal
from app.models import (Account, AnalysisModule, AnalysisResult, Article,
                        Comment, FetchTask, LLMConfig, MetricSnapshot,
                        ResultStatus, TaskStatus)
from app.services.fetch_service import run_fetch_task


def _make_task(fields):
    db = SessionLocal()
    try:
        acc = db.query(Account).first()
        assert acc is not None
        task = FetchTask(owner_id=None, account_ids=[acc.id], fields=fields,
                         status=TaskStatus.pending)
        db.add(task)
        db.commit()
        db.refresh(task)
        return task.id
    finally:
        db.close()


async def test_fetch_full(client, auth_headers):
    # 确保有公众号
    client.post("/api/v1/accounts/import", headers=auth_headers,
                json={"lines": ["测试公众号"]})
    task_id = _make_task(["title", "publish_time", "content",
                          "read_num", "like_num", "comment"])
    await run_fetch_task(task_id, asyncio.Event())

    db = SessionLocal()
    try:
        task = db.get(FetchTask, task_id)
        assert task.status == TaskStatus.success, task.error or task.log
        assert task.new_articles > 0

        articles = db.query(Article).all()
        assert len(articles) > 0
        # 有正文
        assert any(a.content_fetched for a in articles)
        # 有指标快照
        snaps = db.query(MetricSnapshot).all()
        assert len(snaps) > 0
        assert any(s.read_num is not None for s in snaps)
        # 有评论
        assert db.query(Comment).count() > 0
    finally:
        db.close()


def test_articles_list_and_export(client, auth_headers):
    resp = client.get("/api/v1/articles", headers=auth_headers, params={"page_size": 50})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0
    first = data["items"][0]
    assert "read_num" in first

    # 导出 Excel
    exp = client.get("/api/v1/export/articles", headers=auth_headers,
                     params={"fmt": "xlsx"})
    assert exp.status_code == 200
    assert len(exp.content) > 1000  # xlsx 非空


async def test_analysis_flow(client, auth_headers, monkeypatch):
    # 造一个 LLM 配置
    resp = client.post("/api/v1/llm/configs", headers=auth_headers, json={
        "name": "测试模型", "provider": "openai",
        "base_url": "https://example.com/v1", "api_key": "sk-test", "model": "test-model",
    })
    assert resp.status_code == 201, resp.text
    llm_id = resp.json()["id"]

    # mock LLM client
    from app.llm.base import LLMResult
    from app.services import analysis_service

    class FakeLLM:
        async def chat(self, messages, **params):
            return LLMResult(text='{"核心观点": "测试观点", "情绪倾向": "正面"}',
                             model="test-model", total_tokens=123)

    monkeypatch.setattr(analysis_service, "build_llm_client", lambda cfg: FakeLLM())

    db = SessionLocal()
    try:
        article = db.query(Article).filter(Article.content_fetched.is_(True)).first()
        assert article is not None
        module = db.query(AnalysisModule).first()
        assert module is not None
        aid, mid = article.id, module.id
    finally:
        db.close()

    from app.services.analysis_service import create_results, run_analysis_batch
    db = SessionLocal()
    try:
        batch_id = create_results(db, [aid], mid, llm_id, None)
    finally:
        db.close()
    await run_analysis_batch(batch_id, asyncio.Event())

    db = SessionLocal()
    try:
        r = db.query(AnalysisResult).filter(AnalysisResult.batch_id == batch_id).first()
        assert r.status == ResultStatus.success, r.error
        assert r.result_json is not None
        assert "核心观点" in (r.result_text or "")
    finally:
        db.close()


def test_dashboard_and_ranking(client, auth_headers):
    s = client.get("/api/v1/dashboard/stats", headers=auth_headers)
    assert s.status_code == 200
    assert s.json()["articles"] > 0

    rk = client.get("/api/v1/scheduler/ranking", headers=auth_headers,
                    params={"metric": "read_num", "days": 60})
    assert rk.status_code == 200
    assert len(rk.json()["items"]) > 0
