"""微信文章相关的纯函数工具：链接归一化、HTML→纯文本。

链接归一化的背景：post_history 每次返回的文章 URL 都带一次性参数
（chksm/scene/sessionid 随请求变化），同一篇文章在不同抓取任务里 URL 不同，
按 URL 去重会失效。文章的稳定身份是 __biz + mid + idx + sn 四元组。
"""
from __future__ import annotations

import html
import re
from urllib.parse import parse_qs, urlsplit

# 正文提取时要丢弃的块级标签（转换为换行）
_BLOCK_TAGS = ("p", "div", "section", "br", "li", "tr", "h1", "h2", "h3",
               "h4", "h5", "h6", "blockquote", "table", "ul", "ol", "hr")


def canonical_url_key(url: str) -> str:
    """提取微信文章 URL 的稳定身份键。

    长链接形态: mp.weixin.qq.com/s?__biz=..&mid=..&idx=..&sn=..&chksm=..(一次性)
      → "wx:<biz>|<mid>|<idx>|<sn>"
    短链接/其他形态（/s/<token>、custom:// 等）→ "url:<去空白后的原始URL>"
    解析不出时返回 "url:<原URL>"，保证任何输入都有确定键。
    """
    url = (url or "").strip()
    if not url:
        return ""
    try:
        parts = urlsplit(url)
    except ValueError:
        return f"url:{url}"
    host = parts.netloc.lower()
    if host.endswith("mp.weixin.qq.com") and parts.path.startswith("/s"):
        qs = parse_qs(parts.query)
        biz = qs.get("__biz", [None])[0]
        mid = qs.get("mid", [None])[0]
        idx = qs.get("idx", [None])[0]
        sn = qs.get("sn", [None])[0]
        if biz and mid and sn:
            return f"wx:{biz}|{mid}|{idx or '1'}|{sn}"
    return f"url:{url}"


def biz_from_url(url: str) -> str | None:
    """从微信文章链接解析公众号 biz（__biz 参数）；解析不出返回 None。"""
    url = (url or "").strip()
    if not url:
        return None
    try:
        parts = urlsplit(url)
    except ValueError:
        return None
    if not parts.netloc.lower().endswith("mp.weixin.qq.com"):
        return None
    return parse_qs(parts.query).get("__biz", [None])[0]


def looks_like_html(s: str) -> bool:
    """粗略判断字符串是否为 HTML（article_detail 的 content 字段两种形态都出现过）。"""
    if not s:
        return False
    head = s[:200].lower()
    if "<!doctype" in head or "<html" in head:
        return True
    return bool(re.search(r"<(section|div|p|span|img|br)\b", s))


def html_to_text(src: str) -> str:
    """把文章 HTML（完整页面或富文本片段）转成可读的纯文本。

    保留段落换行；丢弃 script/style/head；图片用 [图片] 占位。
    """
    if not src:
        return ""
    s = src
    # 丢弃脚本/样式/注释/head
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<(script|style|head)[^>]*>.*?</\1>", "", s, flags=re.S | re.I)
    # 图片占位（正文里的图，方便阅读时知道此处有图）
    s = re.sub(r"<img\b[^>]*>", " [图片] ", s, flags=re.I)
    # 块级标签 → 换行
    s = re.sub(r"</?(?:" + "|".join(_BLOCK_TAGS) + r")[^>]*>", "\n", s, flags=re.I)
    # 其余标签直接剥掉
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    # 行内空白收敛、空行合并
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in s.splitlines()]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines).strip()
