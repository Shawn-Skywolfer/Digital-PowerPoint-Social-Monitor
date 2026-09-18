"""dajiala（极致了数据）公众号数据源适配器。

✅ 字段级对齐说明（2026-08，依据官方 Apifox 文档，见 docs/dajiala_api/）：
    下列 `ENDPOINTS` 与 `*_FIELD_MAP`、`_parse_envelope` 的错误码判断均已按
    官方 OpenAPI 文档逐项核对。若官方后续调整，只需改本文件的常量与映射，
    主流程代码无需改动。

要点（与早期占位实现的差异）：
  * 所有接口均为 **POST + JSON body**（不是 GET query）。
  * 翻页机制不统一：历史发文用 offset/is_end；评论用 buffer/continue_flag；
    只有「搜索公众号」用 page/size。
  * post_history 不接受 biz，需用 ghid（原始id，亦兼容 wxid/alias）/ url / nickname 其一。
  * 信封多为 {code,msg,data,cost_money,remain_money}；article_html 用 msk 作消息字段；
    删除/错误时 data 常为 ''（空串）；comment_count=-1 表示该文未开通评论。
  * 同一错误码在不同接口含义不同（如 105/106/107），故「删除」判定以 msg 关键词为主、
    code 为辅。
"""
from __future__ import annotations

import asyncio
import hashlib
import html
import json
import re
from datetime import datetime
from typing import Any, Optional

import httpx

from ..core.config import settings
from ..core.logging import get_logger
from ..utils.wxcontent import biz_from_url, html_to_text, looks_like_html
from .base import (AccountInfo, ArticleDeletedError, ArticleInfo, CommentInfo,
                   MetricsInfo, ProviderAuthError, ProviderError,
                   ProviderQuotaError, SearchedArticle, SearchPage,
                   SourceProvider)

logger = get_logger(__name__)

# ============================================================
# 端点（已对文档核对）  base = https://www.dajiala.com
# ============================================================
ENDPOINTS = {
    # 根据关键字查询公众号（库数据，0.2元/条）
    "search_mp": "/fbmain/monitor/v3/wx_account/search",
    # 公众号头像/类型/简介等基础信息（实时，name=名称|原始id|wxid，0.5元/次）
    "mp_info": "/fbmain/monitor/v3/avatar_type",
    # 公众号主体信息（实时，url=任意文章链接）
    "mp_subject": "/fbmain/monitor/v3/principal_info",
    # 历史发文列表（实时，offset 翻页；ghid/url/nickname 其一，0.14~0.16元/次）
    "post_history": "/fbmain/monitor/v3/post_history",
    # 历史发文列表 Pro（实时，history_by_ghid）
    "post_history_pro": "/fbmain/monitor/v3/history_by_ghid",
    # 文章正文 HTML（article_html，返回 data.html，0.04元/次）
    "post_detail_html": "/fbmain/monitor/v3/article_html",
    # 文章详情（纯文本 content + 富文本 content_multi_text）
    "post_detail_text": "/fbmain/monitor/v3/article_detail",
    # 阅读/点赞/在看/转发/收藏/评论 Pro（read_zan_pro，0.06元/次）
    "post_metrics": "/fbmain/monitor/v3/read_zan_pro",
    # 阅读/点赞/在看 基础版（read_zan，0.04元/次）
    "post_metrics_basic": "/fbmain/monitor/v3/read_zan",
    # 单篇文章综合信息（标题/作者/阅读/点赞/在看，article_info）
    "article_info": "/fbmain/monitor/v3/article_info",
    # 文章一级评论 Pro（article_comment2，buffer 翻页，0.06元/次）
    "post_comments": "/fbmain/monitor/v3/article_comment2",
    # 文章二级评论（article_sub_comment，需一级评论 content_id）
    "post_sub_comments": "/fbmain/monitor/v3/article_sub_comment",
    # 查询 API 余额（get_remain_money，免费）
    "balance": "/fbmain/monitor/v3/get_remain_money",
    # 搜一搜·文章关键词搜索（web_search，0.5元/次，offset+cookies_buffer 翻页）
    "web_search": "/fbmain/monitor/v3/web_search",
}

# ---------- 错误码（综合各接口；删除判定以 msg 关键词为主）----------
# 文章被删除/违规/被屏蔽/已迁移（101=多数接口文章删除；102=评论接口文章删除/异常）
DELETED_CODES = {101, 102}
# 文章删除/不可见时 msg 里的常见关键词（触发待确认）
DELETED_KEYWORDS = ["已被发布者删除", "已删除", "该内容已被删除", "内容不存在",
                    "已被删除", "已被屏蔽", "已迁移", "违规", "封号", "无法查看",
                    "被删除", "状态异常"]
# 鉴权失败（key/附加码错误）
AUTH_CODES = {10002, 113}
# 余额/配额不足
QUOTA_CODES = {20001}
# 可重试（限频/解析失败/系统错误）：-1 QPS、103/104 频率、105/106/107 解析失败、
# 110 翻页空、111/112 请求频繁/失败、2003/2005 系统错误、50000 服务器错误
RETRY_CODES = {-1, 103, 104, 105, 106, 107, 110, 111, 112, 2003, 2005, 50000}

# ============================================================
# 字段映射（目标字段 -> 源字段候选列表，按序取值）
# ============================================================
# 账号：来源 = wx_account/search 项、avatar_type 的 data、article_info 项
ACCOUNT_FIELD_MAP = {
    "biz": ["biz"],
    "name": ["name", "wx_name", "nickname", "nick_name"],
    "gh_id": ["ghid", "gh_id", "wxid"],                 # 原始id 优先（post_history 用）
    "avatar": ["avatar", "head_img", "wx_head_img", "mp_head_img"],
    "intro": ["desc", "signature", "intro"],
    "verify": ["customer_type", "type", "verify"],
    "profile_url": ["profile_url", "url"],
}

# 文章：来源 = post_history 项（sn 为唯一字段、无 author）、article_info 项（有 author/hashid）
ARTICLE_FIELD_MAP = {
    "url": ["url", "article_url", "link"],
    "msgid": ["sn", "hashid", "msgid", "appmsgid", "msg_id"],
    "title": ["title", "msg_title"],
    "author": ["author", "msg_author"],
    "publish_time": ["post_time", "post_time_str", "public_time", "publish_time", "create_time"],
    "cover": ["cover_url", "cover", "cdn_url"],
    "digest": ["digest", "summary", "desc"],
}

# 指标：来源 = read_zan_pro 的 data
METRIC_FIELD_MAP = {
    "read_num": ["read", "read_num"],
    "like_num": ["zan", "praise", "like_num"],
    "wow_num": ["looking", "look", "wow_num"],
    "share_num": ["share_num", "share"],
    "collect_num": ["collect_num", "collect"],
    "comment_count": ["comment_count", "comment_num"],
}

# 评论：来源 = article_comment2 项（content_id 为稳定 id；二级评论走单独接口）
COMMENT_FIELD_MAP = {
    "comment_id": ["content_id", "comment_id", "id"],
    "nickname": ["nick_name", "nickname", "user_name"],
    "content": ["content", "comment", "text"],
    "like_num": ["like_num", "reply_like_num", "praise_num"],
    "comment_time": ["create_time_stamp", "create_time", "comment_time", "time"],
}
# ============================================================


def _pick(raw: dict[str, Any], keys: list[str]) -> Any:
    for k in keys:
        if k in raw and raw[k] is not None:
            return raw[k]
    return None


def _to_int(v: Any) -> Optional[int]:
    if v is None or v == "":
        return None
    try:
        if isinstance(v, str):
            v = v.replace(",", "").replace("w", "0000").replace("万", "0000")
            v = v.rstrip("+")  # "10w+" / "100000+" 之类
        return int(float(v))
    except (ValueError, TypeError):
        return None


def _to_time(v: Any) -> Optional[datetime]:
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        try:
            return datetime.fromtimestamp(int(v))
        except (ValueError, OSError):
            return None
    if isinstance(v, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y/%m/%d %H:%M:%S"):
            try:
                return datetime.strptime(v.strip(), fmt)
            except ValueError:
                continue
    return None


def _to_float(v: Any) -> Optional[float]:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


_EM_RE = re.compile(r"</?em[^>]*>")


def _strip_em(v: Any) -> Optional[str]:
    """搜一搜结果的标题/摘要带 <em class="highlight"> 高亮标签，剥掉并反转义实体。"""
    if v is None:
        return None
    text = html.unescape(_EM_RE.sub("", str(v))).strip()
    return text or None


class DajialaProvider(SourceProvider):
    name = "dajiala"
    max_retries = 2          # 限频/解析失败/网络错误的重试次数
    retry_backoff = 2.0      # 重试基础间隔（秒），QPS 上限 5/s

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None):
        self.base_url = (base_url or settings.dajiala_base_url).rstrip("/")
        self.timeout = timeout or settings.fetch_request_timeout

    # ---------- 底层请求 ----------
    async def _request(self, endpoint_key: str, params: dict[str, Any], key: str) -> dict[str, Any]:
        """统一 POST(JSON) 请求 + 信封解析 + 错误分类 + 限频重试。

        返回**完整 payload**（含顶层 offset/is_end/buffer/remain_money 等），
        调用方自行取 payload["data"]。出错抛对应 Provider* 异常。
        """
        path = ENDPOINTS[endpoint_key]
        url = self.base_url + path
        body = {k: v for k, v in params.items() if v is not None and v != ""}
        body["key"] = key
        body.setdefault("verifycode", "")  # 附加码：设置了才必填，默认空

        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout, **settings.httpx_kwargs) as client:
                    resp = await client.post(url, json=body)
                    resp.raise_for_status()
                    payload = resp.json()
            except (httpx.HTTPStatusError, httpx.RequestError, ValueError) as e:
                last_err = ProviderError(f"dajiala 请求失败: {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_backoff * (attempt + 1))
                    continue
                raise last_err

            if not isinstance(payload, dict):  # 异常返回
                raise ProviderError(f"dajiala 返回非对象: {str(payload)[:120]}")

            code = payload.get("code", payload.get("errcode"))
            msg = (payload.get("msg") or payload.get("msk")
                   or payload.get("errmsg") or payload.get("message") or "")
            if code is None and payload.get("message"):  # HTTP 层 Internal Server Error
                code = 50000

            if code in (0, "0", 200, "200", "success"):
                return payload

            text = str(msg)
            # 0) 临时链接失效不是删除（code 也是 101）：换新链接重抓即可，按可重试错误处理
            if "临时链接" in text:
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_backoff * (attempt + 1))
                    continue
                raise ProviderError(f"临时链接已失效(code={code}): {msg}")
            # 1) 删除/不可见（msg 关键词优先，code 为辅）
            if code in DELETED_CODES or any(kw in text for kw in DELETED_KEYWORDS):
                raise ArticleDeletedError(f"内容已删除/不可见(code={code}): {msg}")
            # 2) 鉴权
            if (code in AUTH_CODES or "附加码" in text or "鉴权" in text
                    or ("key" in text.lower() and ("不正确" in text or "有误" in text))):
                raise ProviderAuthError(f"鉴权失败(code={code}): {msg}")
            # 3) 配额/余额
            if code in QUOTA_CODES or "金额不足" in text or "请充值" in text or "余额不足" in text:
                raise ProviderQuotaError(f"配额不足(code={code}): {msg}")
            # 4) 可重试（限频/解析失败/系统错误）
            if code in RETRY_CODES and attempt < self.max_retries:
                await asyncio.sleep(self.retry_backoff * (attempt + 1))
                continue
            raise ProviderError(f"dajiala 返回错误(code={code}): {msg}")

        raise last_err or ProviderError("dajiala 请求失败")

    # ---------- 接口实现 ----------
    async def search_accounts(self, query: str, key: str) -> list[AccountInfo]:
        payload = await self._request("search_mp", {
            "keyword": query,
            "page": "1",
            "size": str(settings.fetch_default_page_size),
            "mode": 1,  # 1 模糊 / 2 精确
        }, key)
        data = payload.get("data")
        items = data if isinstance(data, list) else []
        return [self._map_account(it) for it in items if isinstance(it, dict)]

    async def resolve_account(self, ref: str, key: str) -> Optional[AccountInfo]:
        ref = (ref or "").strip()
        if not ref:
            return None
        # 文章链接 → 用 article_info 反解公众号信息
        if "mp.weixin.qq.com" in ref or ref.startswith("http"):
            payload = await self._request("article_info", {"url": ref}, key)
            data = payload.get("data")
            if isinstance(data, list) and data:
                return self._map_account(data[0])
            return None
        # 名称 / 微信号 / 原始id → avatar_type
        payload = await self._request("mp_info", {"name": ref}, key)
        data = payload.get("data")
        if isinstance(data, dict) and data:
            return self._map_account(data)
        return None

    async def fetch_article_list(
        self,
        account: AccountInfo,
        key: str,
        time_start: Optional[datetime] = None,
        time_end: Optional[datetime] = None,
        need_content: bool = False,  # 已废弃：正文由 fetch_service 按需调 fetch_content
    ) -> list[ArticleInfo]:
        articles: list[ArticleInfo] = []
        offset: Optional[str] = None
        pages = 0
        while pages < settings.fetch_max_pages_per_account:
            # post_history 接受 ghid / url / nickname 其一（不接受 biz）
            params: dict[str, Any] = {}
            if account.gh_id:
                params["ghid"] = account.gh_id
            elif account.profile_url:
                params["url"] = account.profile_url
            else:
                params["nickname"] = account.name
            if offset:
                params["offset"] = offset

            payload = await self._request("post_history", params, key)
            data = payload.get("data")
            items = data if isinstance(data, list) else []
            if not items:
                break
            pages += 1
            page_has_inrange = False
            for it in items:
                if not isinstance(it, dict):
                    continue
                # 跳过已删除（msg_status=7 / is_deleted=1）
                if it.get("msg_status") == 7 or str(it.get("is_deleted")) == "1":
                    continue
                art = self._map_article(it)
                if not art.url:
                    continue
                if art.publish_time:
                    if time_start and art.publish_time < time_start:
                        continue
                    if time_end and art.publish_time > time_end:
                        continue
                    page_has_inrange = True
                articles.append(art)

            is_end = payload.get("is_end")
            next_offset = payload.get("offset")
            if is_end == 1 or not next_offset:
                break
            # 本页全部早于起始时间（列表按时间倒序）→ 提前终止
            if not page_has_inrange and time_start is not None:
                break
            offset = next_offset
        return articles

    async def fetch_content(self, article: ArticleInfo, key: str) -> ArticleInfo:
        """取正文（article_detail，0.03元/次）。

        实测（2026-08）：该接口字段在**顶层**（content/title/author/...），
        不像其他接口包一层 data；且 content 有两种形态——
        多数文章是纯文本，部分是整页 HTML（<DOCTYPE...>），需自行提取文本。
        mode=2 按文档为「纯文字+富文本」，实测不影响返回，仍传以对齐文档。
        """
        art = ArticleInfo(url=article.url, title=article.title, msgid=article.msgid,
                          author=article.author, publish_time=article.publish_time,
                          cover=article.cover, digest=article.digest)
        payload = await self._request("post_detail_text", {"url": article.url, "mode": 2}, key)
        data = payload.get("data")
        if not isinstance(data, dict):  # 顶层字段形态（实测），data 形态兜底
            data = payload
        raw_content = _pick(data, ["content", "content_text", "text"]) or ""
        raw_rich = _pick(data, ["content_multi_text", "html", "content_html"]) or ""
        if looks_like_html(raw_content):
            art.content_text = html_to_text(raw_content)
        else:
            art.content_text = raw_content.strip() or None
        art.content_html = raw_rich or None
        if not art.content_text and raw_rich:  # 纯文本缺失时从富文本提取
            art.content_text = html_to_text(raw_rich)
        # 顺带补齐元数据（详情接口比列表接口字段全）
        art.author = _pick(data, ["author", "nickname"]) or art.author
        art.cover = _pick(data, ["cover_url", "cdn_url", "cover"]) or art.cover
        art.digest = _pick(data, ["desc", "digest"]) or art.digest
        art.publish_time = (_to_time(_pick(data, ["post_time_str", "post_time", "pubtime"]))
                            or art.publish_time)
        art.raw = data
        return art

    async def fetch_metrics(self, article: ArticleInfo, key: str, fields: list[str]) -> MetricsInfo:
        payload = await self._request("post_metrics", {"url": article.url}, key)
        raw = payload.get("data")
        raw = raw if isinstance(raw, dict) else {}
        m = MetricsInfo(raw=raw)
        for f in fields:
            if f in METRIC_FIELD_MAP:
                setattr(m, f, _to_int(_pick(raw, METRIC_FIELD_MAP[f])))
        # comment_count 一并返回；-1 表示该文未开通评论，置 None 避免误判评论下降
        if m.comment_count is None:
            m.comment_count = _to_int(_pick(raw, METRIC_FIELD_MAP["comment_count"]))
        if m.comment_count == -1:
            m.comment_count = None
        return m

    async def fetch_comments(self, article: ArticleInfo, key: str) -> list[CommentInfo]:
        comments: list[CommentInfo] = []
        buffer: Optional[str] = None
        pages = 0
        while pages < settings.fetch_max_pages_per_account:
            params: dict[str, Any] = {"url": article.url}
            if buffer:
                params["buffer"] = buffer
            try:
                payload = await self._request("post_comments", params, key)
            except ProviderError as e:
                # 该接口 code=103 含义为「文章没有开通评论功能」（与其他接口的限频含义不同）
                if "code=103" in str(e):
                    return []
                raise
            data = payload.get("data")
            items = data if isinstance(data, list) else []
            for it in items:
                if not isinstance(it, dict):
                    continue
                cid = _pick(it, COMMENT_FIELD_MAP["comment_id"])
                if cid is None:  # 无 id 时用 昵称+内容 哈希兜底
                    cid = hashlib.md5(
                        (str(it.get("nick_name")) + str(it.get("content"))).encode()
                    ).hexdigest()[:16]
                comments.append(CommentInfo(
                    comment_id=str(cid),
                    nickname=_pick(it, COMMENT_FIELD_MAP["nickname"]),
                    content=_pick(it, COMMENT_FIELD_MAP["content"]),
                    like_num=_to_int(_pick(it, COMMENT_FIELD_MAP["like_num"])),
                    is_sub=False,   # 一级评论；二级评论走 article_sub_comment（默认不逐条拉取以控成本）
                    parent_id=None,
                    comment_time=_to_time(_pick(it, COMMENT_FIELD_MAP["comment_time"])),
                    raw=it,
                ))
            pages += 1
            next_buffer = payload.get("buffer")
            continue_flag = payload.get("continue_flag")
            if not next_buffer or continue_flag in (0, False):
                break
            buffer = next_buffer
        return comments

    async def search_articles(
        self, keyword: str, key: str, *,
        sort_type: int = 0, publish_time_type: int = 0,
        offset: int = 0, cookies_buffer: str = "", current_page: int = 1,
    ) -> SearchPage:
        """搜一搜·文章关键词搜索（web_search，0.5元/次）。

        实测（2026-09，样本 docs/dajiala_api/web_search_sample.json）：
          * data 是 box 列表，每个 box 的 items[] 才是文章（通常每 box 一条）；
          * 翻页游标在顶层：offset（下一页 offset）+ cookies（JSON 字符串，
            内含 cookies_buffer，下一页请求原样回传）；continueFlag=1 表示还有；
          * 标题/摘要含 <em class="highlight"> 高亮标签；公众号名在 item.source.title；
          * 每个 box 上有 totalCount（命中总数）。
        """
        payload = await self._request("web_search", {
            "mode": 1,
            "keyword": keyword,
            "search_type": 1,                       # 1=文章（2=视频，0=全部）
            "publish_time_type": publish_time_type,  # 0不限/1最近1天/2最近7天/3最近半年
            "sort_type": sort_type,                  # 0综合/1最新/2最热
            "currentPage": current_page,
            "offset": offset,
            "cookies_buffer": cookies_buffer,        # 首页为空（_request 会丢弃空串）
        }, key)

        data = payload.get("data")
        boxes = data if isinstance(data, list) else []
        items: list[SearchedArticle] = []
        total: Optional[int] = None
        for box in boxes:
            if not isinstance(box, dict):
                continue
            if total is None:
                total = _to_int(box.get("totalCount"))
            for it in (box.get("items") or []):
                if not isinstance(it, dict):
                    continue
                art = self._map_searched(it)
                if art.url:
                    items.append(art)

        # 翻页游标：cookies 是 JSON 字符串，取其中 cookies_buffer
        next_buffer = ""
        raw_cookies = payload.get("cookies")
        if isinstance(raw_cookies, str) and raw_cookies:
            try:
                next_buffer = str(json.loads(raw_cookies).get("cookies_buffer") or "")
            except (ValueError, AttributeError):
                next_buffer = ""

        return SearchPage(
            items=items,
            continue_flag=payload.get("continueFlag") in (1, True, "1"),
            offset=_to_int(payload.get("offset")) or 0,
            cookies_buffer=next_buffer,
            total=total,
            cost=_to_float(payload.get("cost_money")),
            remain=_to_float(payload.get("remain_money")),
        )

    async def get_balance(self, key: str) -> dict[str, Any]:
        """查询 API 余额（免费）。"""
        payload = await self._request("balance", {}, key)
        return {
            "remain_money": payload.get("remain_money"),
            "yesterday_money": payload.get("yesterday_money"),
            "request_time": payload.get("request_time"),
        }

    # ---------- 字段映射 ----------
    def _map_account(self, raw: dict[str, Any]) -> AccountInfo:
        return AccountInfo(
            biz=str(_pick(raw, ACCOUNT_FIELD_MAP["biz"]) or ""),
            name=str(_pick(raw, ACCOUNT_FIELD_MAP["name"]) or ""),
            gh_id=_pick(raw, ACCOUNT_FIELD_MAP["gh_id"]),
            avatar=_pick(raw, ACCOUNT_FIELD_MAP["avatar"]),
            intro=_pick(raw, ACCOUNT_FIELD_MAP["intro"]),
            verify=_pick(raw, ACCOUNT_FIELD_MAP["verify"]),
            profile_url=_pick(raw, ACCOUNT_FIELD_MAP["profile_url"]),
            raw=raw,
        )

    def _map_article(self, raw: dict[str, Any]) -> ArticleInfo:
        return ArticleInfo(
            url=str(_pick(raw, ARTICLE_FIELD_MAP["url"]) or ""),
            msgid=(str(_pick(raw, ARTICLE_FIELD_MAP["msgid"]))
                   if _pick(raw, ARTICLE_FIELD_MAP["msgid"]) is not None else None),
            title=str(_pick(raw, ARTICLE_FIELD_MAP["title"]) or "(无标题)"),
            author=_pick(raw, ARTICLE_FIELD_MAP["author"]),
            publish_time=_to_time(_pick(raw, ARTICLE_FIELD_MAP["publish_time"])),
            cover=_pick(raw, ARTICLE_FIELD_MAP["cover"]),
            digest=_pick(raw, ARTICLE_FIELD_MAP["digest"]),
            raw=raw,
        )

    def _map_searched(self, raw: dict[str, Any]) -> SearchedArticle:
        url = str(_pick(raw, ["doc_url", "url"]) or "")
        source = raw.get("source") if isinstance(raw.get("source"), dict) else {}
        return SearchedArticle(
            url=url,
            title=_strip_em(_pick(raw, ["title"])) or "(无标题)",
            account_name=str(_pick(source, ["title", "name"]) or ""),
            biz=biz_from_url(url),
            digest=_strip_em(_pick(raw, ["desc", "digest"])),
            publish_time=_to_time(_pick(raw, ["timestamp", "date", "publish_time"])),
            cover=_pick(raw, ["thumbUrl", "cover", "thumb_url"]),
            doc_id=(str(raw["docID"]) if raw.get("docID") is not None else None),
            raw=raw,
        )
