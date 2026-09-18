"""分析：模块/维度 CRUD + 导入导出 + 运行 + 结果查询。"""
from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ...core.deps import get_current_user, get_db
from ...models import (AnalysisDimension, AnalysisModule, AnalysisResult,
                       AnalysisTarget, Article, CollectionReport, FetchTask,
                       LLMConfig, User)
from ...schemas.analysis import (AnalysisResultOut, AnalysisRunRequest,
                                 CollectionReportOut, DimensionIn,
                                 DimensionImportExport, DimensionOut,
                                 ModuleIn, ModuleOut)
from ...services import analysis_service
from ...tasks.queue import manager

router = APIRouter(prefix="/analysis", tags=["analysis"])


# ---------- 模块 ----------
@router.get("/modules", response_model=list[ModuleOut])
def list_modules(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    modules = db.query(AnalysisModule).order_by(AnalysisModule.id).all()
    return [ModuleOut.model_validate(m) for m in modules]


@router.post("/modules", response_model=ModuleOut, status_code=status.HTTP_201_CREATED)
def create_module(req: ModuleIn, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    m = AnalysisModule(name=req.name, target=req.target,
                       prompt_template=req.prompt_template, enabled=req.enabled,
                       builtin=False, owner_id=user.id)
    db.add(m)
    db.commit()
    db.refresh(m)
    return ModuleOut.model_validate(m)


@router.patch("/modules/{module_id}", response_model=ModuleOut)
def update_module(module_id: int, req: ModuleIn, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    m = db.get(AnalysisModule, module_id)
    if not m:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "模块不存在")
    m.name, m.target, m.prompt_template, m.enabled = (
        req.name, req.target, req.prompt_template, req.enabled)
    db.commit()
    db.refresh(m)
    return ModuleOut.model_validate(m)


@router.delete("/modules/{module_id}")
def delete_module(module_id: int, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    m = db.get(AnalysisModule, module_id)
    if not m:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "模块不存在")
    if m.builtin:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "内置模块不可删除")
    db.delete(m)
    db.commit()
    return {"ok": True}


# ---------- 维度 ----------
@router.post("/modules/{module_id}/dimensions", response_model=DimensionOut,
             status_code=status.HTTP_201_CREATED)
def add_dimension(module_id: int, req: DimensionIn, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    if not db.get(AnalysisModule, module_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "模块不存在")
    d = AnalysisDimension(module_id=module_id, name=req.name, prompt=req.prompt,
                          order=req.order, enabled=req.enabled)
    db.add(d)
    db.commit()
    db.refresh(d)
    return DimensionOut.model_validate(d)


@router.patch("/dimensions/{dim_id}", response_model=DimensionOut)
def update_dimension(dim_id: int, req: DimensionIn, db: Session = Depends(get_db),
                     user: User = Depends(get_current_user)):
    d = db.get(AnalysisDimension, dim_id)
    if not d:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "维度不存在")
    d.name, d.prompt, d.order, d.enabled = req.name, req.prompt, req.order, req.enabled
    db.commit()
    db.refresh(d)
    return DimensionOut.model_validate(d)


@router.delete("/dimensions/{dim_id}")
def delete_dimension(dim_id: int, db: Session = Depends(get_db),
                     user: User = Depends(get_current_user)):
    d = db.get(AnalysisDimension, dim_id)
    if not d:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "维度不存在")
    db.delete(d)
    db.commit()
    return {"ok": True}


# ---------- 维度导入/导出 ----------
@router.get("/modules/{module_id}/export")
def export_module(module_id: int, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    m = db.get(AnalysisModule, module_id)
    if not m:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "模块不存在")
    payload = DimensionImportExport(
        module_name=m.name, target=m.target, prompt_template=m.prompt_template,
        dimensions=[DimensionIn(name=d.name, prompt=d.prompt, order=d.order, enabled=d.enabled)
                    for d in m.dimensions],
    )
    data = json.dumps(payload.model_dump(), ensure_ascii=False, indent=2).encode("utf-8")
    return Response(
        content=data, media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''module_{module_id}.json"},
    )


@router.post("/modules/import", response_model=ModuleOut)
def import_module(payload: DimensionImportExport, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    m = AnalysisModule(name=payload.module_name, target=payload.target,
                       prompt_template=payload.prompt_template, builtin=False,
                       enabled=True, owner_id=user.id)
    db.add(m)
    db.flush()
    for d in payload.dimensions:
        db.add(AnalysisDimension(module_id=m.id, name=d.name, prompt=d.prompt,
                                 order=d.order, enabled=d.enabled))
    db.commit()
    db.refresh(m)
    return ModuleOut.model_validate(m)


# ---------- 运行 ----------
@router.post("/run")
async def run_analysis(req: AnalysisRunRequest, db: Session = Depends(get_db),
                       user: User = Depends(get_current_user)):
    module = db.get(AnalysisModule, req.module_id)
    if not module:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "模块不存在")
    if not db.get(LLMConfig, req.llm_config_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "模型配置不存在")

    article_ids: set[int] = set(req.article_ids or [])

    # ① 从抓取任务导入其全部文章
    if req.fetch_task_id:
        task = db.get(FetchTask, req.fetch_task_id)
        if not task:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "抓取任务不存在")
        ids = list(task.article_ids or [])
        if not ids and task.account_ids:  # 老任务回退：账号+时间范围
            q = db.query(Article.id).filter(Article.account_id.in_(task.account_ids))
            if task.time_start:
                q = q.filter(Article.publish_time >= task.time_start)
            if task.time_end:
                q = q.filter(Article.publish_time <= task.time_end)
            ids = [r[0] for r in q.all()]
        article_ids.update(ids)

    # ② 自定义录入内容 → 存为系统账号下的文章
    if req.custom_items:
        for item in req.custom_items:
            if not (item.content or "").strip():
                continue
            art = analysis_service.create_custom_article(db, item.title, item.content)
            article_ids.add(art.id)
        db.commit()

    if not article_ids:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "请选择文章、导入抓取任务或录入自定义内容")
    count = db.query(Article).filter(Article.id.in_(article_ids)).count()
    if count != len(article_ids):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "部分文章不存在")

    custom_dims = ([d.model_dump() for d in req.custom_dimensions]
                   if req.custom_dimensions else None)

    # 聚合分析：一批文章整体出一份报告
    if module.target == AnalysisTarget.collection:
        batch_id = analysis_service.create_collection_report(
            db, sorted(article_ids), req.module_id, req.llm_config_id,
            req.dimension_ids, custom_dims)
        manager.start(f"analysis:col:{batch_id}",
                      lambda cancel: analysis_service.run_collection_report(batch_id, cancel))
        return {"ok": True, "batch_id": batch_id, "count": len(article_ids),
                "mode": "collection"}

    batch_id = analysis_service.create_results(
        db, sorted(article_ids), req.module_id, req.llm_config_id,
        req.dimension_ids, custom_dims)
    manager.start(f"analysis:{batch_id}",
                  lambda cancel: analysis_service.run_analysis_batch(batch_id, cancel))
    return {"ok": True, "batch_id": batch_id, "count": len(article_ids),
            "mode": "per_article"}


# ---------- 聚合分析报告 ----------
@router.get("/collections", response_model=list[CollectionReportOut])
def list_collections(limit: int = Query(50, le=200), db: Session = Depends(get_db),
                     user: User = Depends(get_current_user)):
    rows = db.query(CollectionReport).order_by(CollectionReport.id.desc()).limit(limit).all()
    return [_collection_out(r) for r in rows]


@router.get("/collections/{report_id}", response_model=CollectionReportOut)
def get_collection(report_id: int, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    r = db.get(CollectionReport, report_id)
    if not r:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "报告不存在")
    return _collection_out(r)


@router.delete("/collections/{report_id}")
def delete_collection(report_id: int, db: Session = Depends(get_db),
                      user: User = Depends(get_current_user)):
    r = db.get(CollectionReport, report_id)
    if not r:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "报告不存在")
    db.delete(r)
    db.commit()
    return {"ok": True}


def _collection_out(r: CollectionReport) -> CollectionReportOut:
    out = CollectionReportOut.model_validate(r)
    out.article_total = (r.result_json or {}).get("article_total") or len(r.article_ids or [])
    return out


# ---------- 结果 ----------
@router.get("/results", response_model=list[AnalysisResultOut])
def list_results(
    article_id: Optional[int] = None,
    batch_id: Optional[str] = None,
    module_id: Optional[int] = None,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(AnalysisResult)
    if article_id:
        q = q.filter(AnalysisResult.article_id == article_id)
    if batch_id:
        q = q.filter(AnalysisResult.batch_id == batch_id)
    if module_id:
        q = q.filter(AnalysisResult.module_id == module_id)
    results = q.order_by(AnalysisResult.id.desc()).limit(limit).all()
    return [AnalysisResultOut.model_validate(r) for r in results]


@router.get("/results/{result_id}", response_model=AnalysisResultOut)
def get_result(result_id: int, db: Session = Depends(get_db),
               user: User = Depends(get_current_user)):
    r = db.get(AnalysisResult, result_id)
    if not r:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "结果不存在")
    return AnalysisResultOut.model_validate(r)
