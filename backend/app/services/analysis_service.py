"""分析工作流：对文章执行指定模块+维度的大模型分析，支持单篇/批量。"""
from __future__ import annotations

import asyncio
import re
import uuid

from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.logging import get_logger
from ..db.session import SessionLocal
from ..models import (Account, AnalysisDimension, AnalysisModule, AnalysisResult,
                      Article, ArticleStatus, CollectionReport, LLMConfig,
                      ResultStatus)
from ..analyzers import engine as analyzer_engine
from ..analyzers.engine import analyze_article
from ..llm.registry import build_llm_client
from ..tasks.queue import CancelEvent
from .article_service import latest_metrics_map

logger = get_logger(__name__)

# 自定义内容载体账号（系统账号，不出现在公众号管理/抓取中）
CUSTOM_ACCOUNT_BIZ = "CUSTOM_CONTENT"


def ensure_custom_account(db: Session) -> Account:
    acc = db.query(Account).filter(Account.biz == CUSTOM_ACCOUNT_BIZ).first()
    if not acc:
        acc = Account(biz=CUSTOM_ACCOUNT_BIZ, name="自定义内容",
                      is_monitoring=False, is_system=True)
        db.add(acc)
        db.flush()
    return acc


def create_custom_article(db: Session, title: str, content: str) -> Article:
    """把用户录入的自定义内容存为系统账号下的文章，复用分析管线。"""
    acc = ensure_custom_account(db)
    art = Article(
        account_id=acc.id, url=f"custom://{uuid.uuid4().hex}",
        title=(title or "自定义内容")[:200], content_text=content,
        content_fetched=True, status=ArticleStatus.normal,
    )
    db.add(art)
    db.flush()
    return art


def create_results(db: Session, article_ids: list[int], module_id: int,
                   llm_config_id: int, dimension_ids: list[int] | None,
                   custom_dimensions: list[dict] | None = None) -> str:
    """为每篇文章创建 pending 结果记录，返回 batch_id。"""
    batch_id = uuid.uuid4().hex[:16]
    module = db.get(AnalysisModule, module_id)
    dims = _select_dimensions(db, module, dimension_ids)
    dim_snapshot = [{"name": d.name, "prompt": d.prompt} for d in dims]
    # 临时自定义维度（不存模块，仅本次运行）
    for d in (custom_dimensions or []):
        if d.get("name"):
            dim_snapshot.append({"name": d["name"], "prompt": d.get("prompt", "")})
    for aid in article_ids:
        db.add(AnalysisResult(
            article_id=aid, module_id=module_id, llm_config_id=llm_config_id,
            dimensions=dim_snapshot, status=ResultStatus.pending, batch_id=batch_id,
        ))
    db.commit()
    return batch_id


def _select_dimensions(db: Session, module: AnalysisModule,
                       dimension_ids: list[int] | None) -> list[AnalysisDimension]:
    q = db.query(AnalysisDimension).filter(AnalysisDimension.module_id == module.id,
                                           AnalysisDimension.enabled.is_(True))
    if dimension_ids:
        q = q.filter(AnalysisDimension.id.in_(dimension_ids))
    return q.order_by(AnalysisDimension.order).all()


async def run_analysis_batch(batch_id: str, cancel: CancelEvent) -> None:
    db = SessionLocal()
    try:
        ids = [r.id for r in db.query(AnalysisResult)
               .filter(AnalysisResult.batch_id == batch_id).all()]
    finally:
        db.close()
    if not ids:
        return
    sem = asyncio.Semaphore(settings.analysis_concurrency)
    # 每条结果用独立 session，避免并发协程共享 session
    await asyncio.gather(*[_run_one(rid, sem) for rid in ids])


async def _run_one(result_id: int, sem: asyncio.Semaphore) -> None:
    async with sem:
        db = SessionLocal()
        try:
            result = db.get(AnalysisResult, result_id)
            if not result or result.status != ResultStatus.pending:
                return
            result.status = ResultStatus.running
            db.commit()
            article = db.get(Article, result.article_id)
            module = db.get(AnalysisModule, result.module_id)
            cfg = db.get(LLMConfig, result.llm_config_id)
            if not (article and module and cfg):
                raise ValueError("文章/模块/模型配置缺失")
            dims = [AnalysisDimension(name=d["name"], prompt=d.get("prompt", ""))
                    for d in (result.dimensions or [])]
            llm = build_llm_client(cfg)
            text, result_json, tokens = await analyze_article(llm, module, article, dims)
            result.result_text = text
            result.result_json = result_json
            result.tokens = tokens
            result.model = cfg.model
            result.status = ResultStatus.success
        except Exception as e:  # noqa: BLE001
            logger.exception("分析结果 %s 失败", result_id)
            try:
                result.status = ResultStatus.failed
                result.error = str(e)
                db.commit()
            except Exception:  # noqa: BLE001
                pass
        else:
            db.commit()
        finally:
            db.close()


# ============================================================
# 聚合分析（collection）：一批文章 → 一份议题报告
# ============================================================
def create_collection_report(db: Session, article_ids: list[int], module_id: int,
                             llm_config_id: int, dimension_ids: list[int] | None,
                             custom_dimensions: list[dict] | None = None) -> str:
    """创建聚合分析报告（pending），返回 batch_id。"""
    batch_id = uuid.uuid4().hex[:16]
    module = db.get(AnalysisModule, module_id)
    dims = _select_dimensions(db, module, dimension_ids)
    dim_snapshot = [{"name": d.name, "prompt": d.prompt} for d in dims]
    for d in (custom_dimensions or []):
        if d.get("name"):
            dim_snapshot.append({"name": d["name"], "prompt": d.get("prompt", "")})
    db.add(CollectionReport(
        module_id=module_id, llm_config_id=llm_config_id, article_ids=article_ids,
        dimensions=dim_snapshot, status=ResultStatus.pending, batch_id=batch_id,
    ))
    db.commit()
    return batch_id


def _parse_idx(v) -> int | None:
    """LLM 返回的文章序号可能是 int / "3" / "#3" / "第3篇" 等，尽力解析为 1-based int。"""
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if isinstance(v, str):
        m = re.search(r"\d+", v)
        return int(m.group()) if m else None
    return None


def _aggregate_topic_stats(result_json: dict, articles: list[Article],
                           metrics: dict) -> dict:
    """把 LLM 返回的 article_indices 映射回文章，并精确汇总阅读/点赞等数字。"""
    topics = result_json.get("topics") or []
    out_topics = []
    for t in topics:
        # 序号清洗：兼容 "#2"/"2"/2.0 等形态，去重且只保留有效范围
        seen: set[int] = set()
        idxs: list[int] = []
        for v in (t.get("article_indices") or []):
            n = _parse_idx(v)
            if n is not None and 1 <= n <= len(articles) and n not in seen:
                seen.add(n)
                idxs.append(n)
        arts = [articles[i - 1] for i in idxs]
        ids = [a.id for a in arts]
        read = sum((metrics.get(a.id).read_num or 0) for a in arts if metrics.get(a.id))
        like = sum((metrics.get(a.id).like_num or 0) for a in arts if metrics.get(a.id))
        top = sorted(
            ({"id": a.id, "title": a.title,
              "read_num": metrics.get(a.id).read_num if metrics.get(a.id) else None}
             for a in arts),
            key=lambda x: (x["read_num"] or 0), reverse=True)[:5]
        out_topics.append({
            "name": t.get("name", "未命名议题"),
            "summary": t.get("summary", ""),
            "article_ids": ids,
            "article_count": len(ids),
            "total_read": read,
            "total_like": like,
            "top_articles": top,
        })
    result_json["topics"] = out_topics
    result_json["article_total"] = len(articles)
    return result_json


async def run_collection_report(batch_id: str, cancel: CancelEvent) -> None:
    db = SessionLocal()
    try:
        report = (db.query(CollectionReport)
                  .filter(CollectionReport.batch_id == batch_id).first())
        if not report or report.status != ResultStatus.pending:
            return
        report.status = ResultStatus.running
        db.commit()
        try:
            module = db.get(AnalysisModule, report.module_id)
            cfg = db.get(LLMConfig, report.llm_config_id)
            if not (module and cfg):
                raise ValueError("模块或模型配置缺失")
            articles = (db.query(Article)
                        .filter(Article.id.in_(report.article_ids)).all()) if report.article_ids else []
            if not articles:
                raise ValueError("分析范围为空：所选内容没有文章")
            metrics = latest_metrics_map(db, [a.id for a in articles])
            # 阅读高的优先，截断到 prompt 上限
            articles.sort(key=lambda a: (metrics.get(a.id).read_num or 0)
                          if metrics.get(a.id) else 0, reverse=True)
            articles = articles[:analyzer_engine.COLLECTION_MAX_ARTICLES]
            items = [{
                "idx": i, "title": a.title,
                "account": a.account.name if a.account else "",
                "read_num": metrics.get(a.id).read_num if metrics.get(a.id) else None,
                "like_num": metrics.get(a.id).like_num if metrics.get(a.id) else None,
                "digest": a.digest or (a.content_text or "")[:80],
            } for i, a in enumerate(articles, 1)]
            dims = [AnalysisDimension(name=d["name"], prompt=d.get("prompt", ""))
                    for d in (report.dimensions or [])]
            llm = build_llm_client(cfg)
            prompt = analyzer_engine.build_collection_prompt(module, items, dims)
            result = await llm.chat([{"role": "user", "content": prompt}])
            result_json = analyzer_engine.parse_result_json(result.text) or {}
            result_json = _aggregate_topic_stats(result_json, articles, metrics)
            report.overview = result_json.get("overview")
            report.result_text = result.text
            report.result_json = result_json
            report.tokens = result.total_tokens
            report.model = cfg.model
            report.status = ResultStatus.success
        except Exception as e:  # noqa: BLE001
            logger.exception("聚合分析 %s 失败", batch_id)
            report.status = ResultStatus.failed
            report.error = str(e)
        db.commit()
    finally:
        db.close()


def repair_collection_topic_counts(db: Session) -> int:
    """修复历史聚合报告：LLM 把序号输出成 "#2" 字符串导致议题篇数全 0。

    用 result_text 里的原始 JSON 重新映射汇总（文章顺序按当前指标重建，
    与运行时相同）；幂等，启动时调用，返回修复份数。
    """
    repaired = 0
    reports = (db.query(CollectionReport)
               .filter(CollectionReport.status == ResultStatus.success).all())
    for r in reports:
        topics = (r.result_json or {}).get("topics") or []
        if topics and any((t.get("article_count") or 0) > 0 for t in topics):
            continue  # 正常报告，跳过
        raw = analyzer_engine.parse_result_json(r.result_text or "")
        if not raw or not raw.get("topics"):
            continue
        articles = (db.query(Article)
                    .filter(Article.id.in_(r.article_ids)).all()) if r.article_ids else []
        if not articles:
            continue
        metrics = latest_metrics_map(db, [a.id for a in articles])
        articles.sort(key=lambda a: (metrics.get(a.id).read_num or 0)
                      if metrics.get(a.id) else 0, reverse=True)
        articles = articles[:analyzer_engine.COLLECTION_MAX_ARTICLES]
        new_rj = _aggregate_topic_stats(raw, articles, metrics)
        if not any(t["article_count"] for t in new_rj.get("topics", [])):
            continue  # 重算仍为 0（原始输出本身无有效序号），放弃
        if new_rj.get("overview"):
            r.overview = new_rj["overview"]
        r.result_json = new_rj
        repaired += 1
        logger.info("聚合报告 #%s 议题篇数已修复（%d 个议题）",
                    r.id, len(new_rj.get("topics", [])))
    if repaired:
        db.commit()
    return repaired
