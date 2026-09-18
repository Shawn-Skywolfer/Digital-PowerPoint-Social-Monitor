"""待确认队列：已删文章 / 评论异常，人工确认保留或删除。"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.deps import get_current_user, get_db
from ...models import Article, ChangeReview, ReviewStatus, User
from ...schemas.schedule import ReviewOut, ReviewResolveRequest
from ...services import review_service

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("", response_model=list[ReviewOut])
def list_reviews(status_filter: Optional[str] = None,
                 db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(ChangeReview)
    if status_filter:
        q = q.filter(ChangeReview.status == ReviewStatus(status_filter))
    reviews = q.order_by(ChangeReview.id.desc()).limit(200).all()
    out = []
    for r in reviews:
        o = ReviewOut.model_validate(r)
        art = db.get(Article, r.article_id)
        o.article_title = art.title if art else None
        out.append(o)
    return out


@router.get("/pending-count")
def pending_count(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    n = db.query(ChangeReview).filter(ChangeReview.status == ReviewStatus.pending).count()
    return {"pending": n}


@router.post("/{review_id}/resolve", response_model=ReviewOut)
def resolve_review(review_id: int, req: ReviewResolveRequest,
                   db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    r = db.get(ChangeReview, review_id)
    if not r:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "记录不存在")
    if r.status != ReviewStatus.pending:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "该记录已处理")
    if req.action not in ("keep", "delete"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "action 必须是 keep 或 delete")
    r = review_service.resolve_review(db, r, req.action, user.id, req.note)
    o = ReviewOut.model_validate(r)
    art = db.get(Article, r.article_id)
    o.article_title = art.title if art else None
    return o
