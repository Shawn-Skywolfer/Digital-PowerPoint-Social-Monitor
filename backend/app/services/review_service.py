"""待确认队列处理：保留原始 or 确认删除。"""
from __future__ import annotations

from sqlalchemy.orm import Session

from ..db.base import utcnow
from ..models import (Article, ArticleStatus, ChangeReview, ChangeType,
                      Comment, CommentStatus, ReviewStatus)


def resolve_review(db: Session, review: ChangeReview, action: str,
                   reviewer_id: int | None, note: str | None) -> ChangeReview:
    article = db.get(Article, review.article_id)
    if action == "keep":
        # 保留原始数据：文章恢复正常，评论保持不动
        review.status = ReviewStatus.keep
        if article and article.status == ArticleStatus.pending_review:
            article.status = ArticleStatus.normal
    elif action == "delete":
        # 确认删除：软删文章/评论，留痕
        review.status = ReviewStatus.deleted
        if article:
            if review.change_type == ChangeType.article_deleted:
                article.status = ArticleStatus.deleted
            elif review.change_type in (ChangeType.comment_drop, ChangeType.comment_deleted):
                article.status = ArticleStatus.normal
                # 把 new_data 中标记缺失的评论置为 deleted
                missing = (review.old_data or {}).get("missing") or []
                if missing:
                    db.query(Comment).filter(
                        Comment.article_id == article.id,
                        Comment.comment_id.in_(missing),
                    ).update({Comment.status: CommentStatus.deleted}, synchronize_session=False)
    else:
        raise ValueError("action 必须是 keep 或 delete")

    review.reviewer_id = reviewer_id
    if note:
        review.note = (review.note or "") + (" | " if review.note else "") + note
    review.resolved_at = utcnow()
    db.commit()
    db.refresh(review)
    return review
