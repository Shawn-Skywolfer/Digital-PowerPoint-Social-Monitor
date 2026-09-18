"""公众号管理：批量导入、在线检索、列表、更新、删除。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.deps import get_current_user, get_db
from ...models import Account, AccountGroup, Article, User
from ...providers.base import ProviderError
from ...providers.registry import get_provider
from ...schemas.account import (AccountImportRequest, AccountImportResponse,
                                AccountImportItem, AccountOut, AccountSearchRequest,
                                AccountUpdate, BatchGroupRequest, GroupIn, GroupOut)
from ...services import key_service

router = APIRouter(prefix="/accounts", tags=["accounts"])


def _with_count(db: Session, acc: Account) -> AccountOut:
    out = AccountOut.model_validate(acc)
    out.article_count = db.query(Article).filter(Article.account_id == acc.id).count()
    out.group_name = acc.group.name if acc.group else None
    return out


@router.get("", response_model=list[AccountOut])
def list_accounts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    accounts = (db.query(Account).filter(Account.is_system.is_(False))
                .order_by(Account.id.desc()).all())
    return [_with_count(db, a) for a in accounts]


# ---------- 分组管理 ----------
@router.get("/groups", response_model=list[GroupOut])
def list_groups(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    groups = db.query(AccountGroup).order_by(AccountGroup.id).all()
    out = []
    for g in groups:
        o = GroupOut.model_validate(g)
        o.account_count = db.query(Account).filter(Account.group_id == g.id,
                                                   Account.is_system.is_(False)).count()
        out.append(o)
    return out


@router.post("/groups", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
def create_group(req: GroupIn, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    name = req.name.strip()
    if not name:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "分组名不能为空")
    if db.query(AccountGroup).filter(AccountGroup.name == name).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "分组已存在")
    g = AccountGroup(name=name, owner_id=user.id)
    db.add(g)
    db.commit()
    db.refresh(g)
    return GroupOut.model_validate(g)


@router.patch("/groups/{group_id}", response_model=GroupOut)
def rename_group(group_id: int, req: GroupIn, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    g = db.get(AccountGroup, group_id)
    if not g:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "分组不存在")
    name = req.name.strip()
    if not name:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "分组名不能为空")
    dup = db.query(AccountGroup).filter(AccountGroup.name == name,
                                        AccountGroup.id != group_id).first()
    if dup:
        raise HTTPException(status.HTTP_409_CONFLICT, "分组名已被占用")
    g.name = name
    db.commit()
    db.refresh(g)
    return GroupOut.model_validate(g)


@router.delete("/groups/{group_id}")
def delete_group(group_id: int, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    g = db.get(AccountGroup, group_id)
    if not g:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "分组不存在")
    # 组内公众号移出分组（不删除公众号）
    db.query(Account).filter(Account.group_id == group_id).update({"group_id": None})
    db.delete(g)
    db.commit()
    return {"ok": True}


@router.post("/groups/assign")
def assign_group(req: BatchGroupRequest, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    """批量把公众号加入/移出分组（group_id 为空=移出）。"""
    if req.group_id is not None and not db.get(AccountGroup, req.group_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "分组不存在")
    n = (db.query(Account).filter(Account.id.in_(req.account_ids))
         .update({"group_id": req.group_id}, synchronize_session=False))
    db.commit()
    return {"ok": True, "updated": n}


@router.post("/search")
async def search_accounts(req: AccountSearchRequest, db: Session = Depends(get_db),
                          user: User = Depends(get_current_user)):
    key = key_service.pick_key(db, owner_id=user.id, key_id=req.key_id)
    key_value = key_service.get_key_value(key)
    provider = get_provider(None if key_value else "mock")
    try:
        results = await provider.search_accounts(req.query, key_value or "")
        key_service.record_usage(db, key.id if key else None, 1)
    except ProviderError as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"检索失败: {e}")
    return [{"biz": r.biz, "name": r.name, "gh_id": r.gh_id, "avatar": r.avatar,
             "intro": r.intro, "verify": r.verify} for r in results]


@router.post("/import", response_model=AccountImportResponse)
async def import_accounts(req: AccountImportRequest, db: Session = Depends(get_db),
                          user: User = Depends(get_current_user)):
    key = key_service.pick_key(db, owner_id=user.id, key_id=req.key_id)
    key_value = key_service.get_key_value(key)
    provider = get_provider(None if key_value else "mock")

    items: list[AccountImportItem] = []
    success = 0
    for raw_line in req.lines:
        line = raw_line.strip()
        if not line:
            continue
        try:
            info = await provider.resolve_account(line, key_value or "")
            key_service.record_usage(db, key.id if key else None, 1)
        except ProviderError as e:
            items.append(AccountImportItem(input=line, ok=False, message=str(e)))
            continue
        if not info or not info.biz:
            items.append(AccountImportItem(input=line, ok=False, message="未能解析到公众号"))
            continue
        # 去重：已存在则更新标签
        existing = db.query(Account).filter(Account.biz == info.biz).first()
        if existing:
            if req.tags:
                existing.tags = req.tags
                db.commit()
            items.append(AccountImportItem(input=line, ok=True, biz=info.biz,
                                           name=existing.name, message="已存在，已更新"))
            success += 1
            continue
        acc = Account(biz=info.biz, name=info.name or line, gh_id=info.gh_id,
                      avatar=info.avatar, intro=info.intro, verify=info.verify,
                      profile_url=info.profile_url, owner_id=user.id, tags=req.tags)
        db.add(acc)
        db.commit()
        items.append(AccountImportItem(input=line, ok=True, biz=info.biz,
                                       name=acc.name, message="导入成功"))
        success += 1

    return AccountImportResponse(total=len(req.lines), success=success,
                                 failed=len(items) - success, items=items)


@router.post("/add")
async def add_account(req: AccountSearchRequest, db: Session = Depends(get_db),
                      user: User = Depends(get_current_user)):
    """按名称/微信号/链接精确添加单个公众号。"""
    key = key_service.pick_key(db, owner_id=user.id, key_id=req.key_id)
    key_value = key_service.get_key_value(key)
    provider = get_provider(None if key_value else "mock")
    try:
        info = await provider.resolve_account(req.query, key_value or "")
    except ProviderError as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"解析失败: {e}")
    if not info or not info.biz:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "未能解析到该公众号")
    if db.query(Account).filter(Account.biz == info.biz).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "该公众号已存在")
    acc = Account(biz=info.biz, name=info.name or req.query, gh_id=info.gh_id,
                  avatar=info.avatar, intro=info.intro, verify=info.verify,
                  profile_url=info.profile_url, owner_id=user.id)
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return _with_count(db, acc)


@router.patch("/{account_id}", response_model=AccountOut)
def update_account(account_id: int, req: AccountUpdate, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    acc = db.get(Account, account_id)
    if not acc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "公众号不存在")
    if req.tags is not None:
        acc.tags = req.tags
    if req.is_monitoring is not None:
        acc.is_monitoring = req.is_monitoring
    if req.group_id is not None:
        if req.group_id == 0:
            acc.group_id = None
        else:
            if not db.get(AccountGroup, req.group_id):
                raise HTTPException(status.HTTP_404_NOT_FOUND, "分组不存在")
            acc.group_id = req.group_id
    db.commit()
    db.refresh(acc)
    return _with_count(db, acc)


@router.delete("/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    acc = db.get(Account, account_id)
    if not acc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "公众号不存在")
    db.delete(acc)
    db.commit()
    return {"ok": True}
