"""建表 + 播种：默认管理员、内置分析模块与维度。

SQLite 轻量迁移：create_all 只建新表，不会给已有表加列；
这里用 PRAGMA 检测并 ALTER TABLE 补列（本项目无 Alembic，够用且幂等）。
"""
from __future__ import annotations

from sqlalchemy import text

from ..core.config import settings
from ..core.logging import get_logger
from ..core.security import hash_password
from ..models import (AnalysisDimension, AnalysisModule, AnalysisTarget, Base,
                      User, UserRole)
from ..utils.wxcontent import canonical_url_key
from .session import SessionLocal, enable_sqlite_wal, engine

logger = get_logger(__name__)

# 需要后补的列：(表, 列, DDL)
_MIGRATIONS = [
    ("accounts", "group_id", "INTEGER"),
    ("accounts", "is_system", "BOOLEAN DEFAULT 0"),
    ("fetch_tasks", "group_ids", "JSON"),
    ("fetch_tasks", "article_ids", "JSON"),
    ("articles", "url_key", "VARCHAR(512)"),
]


def _migrate_sqlite() -> None:
    if engine.url.get_backend_name() != "sqlite":
        return
    with engine.begin() as conn:
        for table, column, ddl in _MIGRATIONS:
            cols = {r[1] for r in conn.execute(text(f"PRAGMA table_info({table})"))}
            if cols and column not in cols:  # 表存在但缺列 → 补列
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))
                logger.info("迁移: %s 新增列 %s", table, column)
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_articles_url_key ON articles (url_key)"))


def _dedup_articles() -> None:
    """文章归一：回填 url_key，并把同一身份键的重复行合并为一行。

    历史问题：微信 URL 的一次性参数（chksm 等）每次抓取都变，同一篇文章被
    不同任务存成多行，指标/正文分散在各自行上。合并时把指标快照、评论、
    分析结果、待确认记录全部指向保留行，任务快照里的文章 id 一并改写。
    幂等：没有重复行时不做任何写操作。
    """
    from ..models import (AnalysisResult, Article, ChangeReview, Comment,
                          FetchTask, MetricSnapshot)

    db = SessionLocal()
    try:
        arts = db.query(Article).all()
        for a in arts:
            if not a.url_key:
                a.url_key = canonical_url_key(a.url)
        db.commit()

        groups: dict[tuple[int, str], list[Article]] = {}
        for a in arts:
            if a.url_key:
                groups.setdefault((a.account_id, a.url_key), []).append(a)

        for (acc_id, key), rows in groups.items():
            if len(rows) < 2:
                continue
            # 保留行：已有正文的优先，其次 id 最小（最早建档）
            rows.sort(key=lambda a: (not a.content_fetched, a.id))
            keep, dupes = rows[0], rows[1:]
            keep_id = keep.id
            for d in dupes:
                # 字段补缺（保留行没有的，从重复行补）
                for f in ("title", "author", "msgid", "cover", "digest",
                          "content_text", "content_html", "publish_time"):
                    if not getattr(keep, f) and getattr(d, f):
                        setattr(keep, f, getattr(d, f))
                keep.content_fetched = keep.content_fetched or d.content_fetched
                if d.first_seen_at and d.first_seen_at < keep.first_seen_at:
                    keep.first_seen_at = d.first_seen_at
                if d.last_seen_at and d.last_seen_at > keep.last_seen_at:
                    keep.last_seen_at = d.last_seen_at
                # 状态取“更严重”的：删除 > 待确认 > 正常
                sev = {"normal": 0, "pending_review": 1, "deleted": 2}
                if sev.get(d.status.value, 0) > sev.get(keep.status.value, 0):
                    keep.status = d.status
                # 关联数据改指保留行
                db.query(MetricSnapshot).filter(
                    MetricSnapshot.article_id == d.id).update(
                    {"article_id": keep_id}, synchronize_session=False)
                db.query(AnalysisResult).filter(
                    AnalysisResult.article_id == d.id).update(
                    {"article_id": keep_id}, synchronize_session=False)
                db.query(ChangeReview).filter(
                    ChangeReview.article_id == d.id).update(
                    {"article_id": keep_id}, synchronize_session=False)
                keep_cids = {c.comment_id for c in
                             db.query(Comment).filter(Comment.article_id == keep_id)}
                for c in db.query(Comment).filter(Comment.article_id == d.id):
                    if c.comment_id in keep_cids:
                        db.delete(c)
                    else:
                        c.article_id = keep_id
                db.delete(d)
                logger.info("文章归一: 合并重复行 %s → %s (account=%s)", d.id, keep_id, acc_id)
            db.flush()
            # 任务快照里的文章 id 改写为保留行
            dup_ids = {d.id for d in dupes}
            for t in db.query(FetchTask).all():
                ids = t.article_ids or []
                if dup_ids & set(ids):
                    t.article_ids = sorted({keep_id if i in dup_ids else i for i in ids})
        db.commit()
    finally:
        db.close()


BUILTIN_MODULES = [
    {
        "name": "正文分析",
        "target": AnalysisTarget.content,
        "prompt_template": (
            "你是一名资深的新能源/数字能源行业社媒内容分析师。请阅读下面这篇公众号文章，"
            "并按要求输出结构化分析。\n\n"
            "【标题】{title}\n【正文】\n{content}\n\n"
            "请针对以下每个分析维度逐一给出结论，输出为 JSON（键为维度名）：\n{dimensions}"
        ),
        "dimensions": [
            ("核心观点", "用 3~5 条要点概括文章的核心观点与结论"),
            ("情绪倾向", "判断整体情绪：正面/中性/负面，并说明依据"),
            ("主题标签", "给出 3~6 个主题/关键词标签"),
            ("传播亮点", "指出标题或内容中有助于传播的亮点与钩子"),
            ("风险与合规", "是否存在夸大、敏感或合规风险表述，若有请指出"),
        ],
    },
    {
        "name": "评论分析",
        "target": AnalysisTarget.comment,
        "prompt_template": (
            "你是一名社媒舆情分析师。下面是公众号文章《{title}》下的读者评论。"
            "请分析这些评论。\n\n【评论列表】\n{comments}\n\n"
            "请针对以下每个维度给出结论，输出为 JSON（键为维度名）：\n{dimensions}"
        ),
        "dimensions": [
            ("整体情绪", "评论整体情绪占比：正面/中性/负面"),
            ("热点诉求", "读者最关心的问题或诉求 Top3"),
            ("典型评论", "摘录 3 条最有代表性的评论并说明"),
            ("舆情风险", "是否存在负面/争议/需回复引导的评论"),
        ],
    },
    {
        "name": "议题聚合分析",
        "target": AnalysisTarget.collection,
        "prompt_template": "",  # 空=用引擎内置聚合模板
        "dimensions": [
            ("关注焦点", "大家近期最关心、讨论最多的话题是什么"),
            ("传播热点", "哪些内容获得了明显更高的阅读/互动，为什么"),
            ("行业趋势", "从这批内容能看出哪些行业趋势或政策动向"),
            ("值得跟进", "哪些议题值得我们（华为数字能源）跟进发声或回应"),
        ],
    },
]


def create_tables() -> None:
    enable_sqlite_wal()
    Base.metadata.create_all(bind=engine)
    _migrate_sqlite()


def seed_admin() -> None:
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == settings.default_admin_username).first()
        if not admin:
            admin = User(
                username=settings.default_admin_username,
                password_hash=hash_password(settings.default_admin_password),
                role=UserRole.admin,
                is_active=True,
                must_change_password=settings.force_change_default_password,
            )
            db.add(admin)
            db.commit()
            logger.info("已播种默认管理员: %s", settings.default_admin_username)
    finally:
        db.close()


def seed_builtin_modules() -> None:
    db = SessionLocal()
    try:
        for spec in BUILTIN_MODULES:
            exists = db.query(AnalysisModule).filter(
                AnalysisModule.name == spec["name"], AnalysisModule.builtin.is_(True)
            ).first()
            if exists:
                continue
            module = AnalysisModule(
                name=spec["name"],
                target=spec["target"],
                prompt_template=spec["prompt_template"],
                builtin=True,
                enabled=True,
            )
            db.add(module)
            db.flush()
            for i, (dname, dprompt) in enumerate(spec["dimensions"]):
                db.add(AnalysisDimension(
                    module_id=module.id, name=dname, prompt=dprompt, order=i, enabled=True
                ))
            db.commit()
            logger.info("已播种内置分析模块: %s", spec["name"])
    finally:
        db.close()


def repair_collection_reports() -> None:
    """修复议题篇数为 0 的历史聚合报告（LLM 序号格式问题，幂等）。"""
    from ..services.analysis_service import repair_collection_topic_counts
    db = SessionLocal()
    try:
        repair_collection_topic_counts(db)
    except Exception:  # noqa: BLE001 修复失败不影响启动
        logger.exception("聚合报告修复失败（忽略，不影响启动）")
    finally:
        db.close()


def init_db() -> None:
    create_tables()
    _dedup_articles()
    repair_collection_reports()
    seed_admin()
    seed_builtin_modules()
