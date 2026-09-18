"""分析引擎：把文章 + 模块模板 + 维度 组装成 prompt，调用 LLM 并解析结果。"""
from __future__ import annotations

import json
import re
from typing import Optional

from ..llm.base import LLMClient
from ..models.analysis import AnalysisDimension, AnalysisModule, AnalysisTarget
from ..models.article import Article


def _fmt_dimensions(dimensions: list[AnalysisDimension]) -> str:
    lines = []
    for i, d in enumerate(dimensions, 1):
        prompt = f"：{d.prompt}" if d.prompt else ""
        lines.append(f"{i}. {d.name}{prompt}")
    return "\n".join(lines) if lines else "1. 综合分析：请给出整体分析结论"


def _fmt_comments(article: Article, limit: int = 200) -> str:
    comments = sorted(article.comments, key=lambda c: (c.like_num or 0), reverse=True)[:limit]
    if not comments:
        return "(暂无评论)"
    lines = []
    for c in comments:
        like = f"(赞{c.like_num})" if c.like_num else ""
        lines.append(f"- {c.nickname or '匿名'}{like}: {c.content or ''}")
    return "\n".join(lines)


def build_prompt(
    module: AnalysisModule,
    article: Article,
    dimensions: list[AnalysisDimension],
    content_max_chars: int = 6000,
) -> str:
    content = (article.content_text or article.digest or "")
    if len(content) > content_max_chars:
        content = content[:content_max_chars] + "…(略)"
    template = module.prompt_template or (
        "请分析文章《{title}》。\n正文：\n{content}\n评论：\n{comments}\n维度：\n{dimensions}"
    )
    prompt = template
    prompt = prompt.replace("{title}", article.title or "")
    prompt = prompt.replace("{content}", content or "(未抓取正文)")
    prompt = prompt.replace("{comments}", _fmt_comments(article))
    prompt = prompt.replace("{dimensions}", _fmt_dimensions(dimensions))
    prompt = prompt.replace("{account}", article.account.name if article.account else "")
    return prompt


def parse_result_json(text: str) -> Optional[dict]:
    """尽力从 LLM 输出中提取 JSON 对象。"""
    if not text:
        return None
    # 去掉 ```json 围栏
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    candidate = m.group(1) if m else None
    if candidate is None:
        # 找第一个 { 到最后一个 }
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end + 1]
    if candidate:
        try:
            return json.loads(candidate)
        except (json.JSONDecodeError, ValueError):
            return None
    return None


async def analyze_article(
    llm: LLMClient,
    module: AnalysisModule,
    article: Article,
    dimensions: list[AnalysisDimension],
) -> tuple[str, Optional[dict], Optional[int]]:
    """返回 (result_text, result_json, total_tokens)。"""
    if module.target == AnalysisTarget.comment and not article.comments:
        return "(该文章暂无评论数据，无法做评论分析)", None, None
    prompt = build_prompt(module, article, dimensions)
    result = await llm.chat([{"role": "user", "content": prompt}])
    return result.text, parse_result_json(result.text), result.total_tokens


# ============================================================
# 聚合分析（collection）：一批文章整体出一份报告
# 设计：LLM 只做"提炼议题 + 把文章归入议题"，阅读/点赞等数字由代码精确汇总
# ============================================================
COLLECTION_MAX_ARTICLES = 200  # 超出时按阅读量截断，控制 prompt 长度

DEFAULT_COLLECTION_TEMPLATE = (
    "你是资深的新能源/数字能源行业社媒分析师。以下是近期抓取的 {count} 篇公众号文章"
    "（每行格式：#序号 《标题》（公众号，阅读X，点赞Y）摘要）。\n\n"
    "{article_list}\n\n"
    "请综合分析并**只输出 JSON**（不要 markdown 围栏、不要多余文字）：\n"
    "{\n"
    '  "overview": "这批内容的总体概述（3~5句）",\n'
    '  "topics": [{"name": "议题名", "summary": "该议题的核心内容与关注点", '
    '"article_indices": [对应的文章序号]}],\n'
    '  "dimension_insights": {"维度名": "该维度下的结论"}\n'
    "}\n"
    "要求：\n"
    "1. topics 提炼 5~10 个议题，按受关注程度从高到低排序；\n"
    "2. article_indices 使用上文的 #序号对应的**整数**（如 [2, 3, 8]，不要带 \"#\" 号、不要加引号）；"
    "一篇文章可归入多个议题，也可不归入任何议题；\n"
    "3. 每个议题的 summary 要具体，指出大家关心什么、讨论的焦点是什么；\n"
    "4. dimension_insights 针对以下每个分析维度给出跨文章的整体结论：\n{dimensions}"
)


def build_collection_prompt(
    module: AnalysisModule,
    items: list[dict],
    dimensions: list[AnalysisDimension],
) -> str:
    """items: [{idx,title,account,read_num,like_num,digest}]（已截断到上限）。"""
    lines = []
    for it in items:
        digest = (it.get("digest") or "")[:80]
        lines.append(
            f"#{it['idx']} 《{it.get('title') or ''}》（{it.get('account') or '未知'}，"
            f"阅读{it.get('read_num') if it.get('read_num') is not None else '?'}，"
            f"点赞{it.get('like_num') if it.get('like_num') is not None else '?'}）{digest}"
        )
    template = module.prompt_template or DEFAULT_COLLECTION_TEMPLATE
    prompt = template
    prompt = prompt.replace("{count}", str(len(items)))
    prompt = prompt.replace("{article_list}", "\n".join(lines))
    prompt = prompt.replace("{dimensions}", _fmt_dimensions(dimensions))
    return prompt
