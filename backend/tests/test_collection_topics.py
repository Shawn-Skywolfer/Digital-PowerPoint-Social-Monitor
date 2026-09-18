"""聚合分析议题汇总：LLM 返回的 article_indices 兼容性格式测试。

回归背景：DeepSeek 把序号输出成 ["#2", "#3"] 字符串，旧实现只认 int，
导致所有议题篇数为 0（2026-09-18 用户反馈）。
"""
from types import SimpleNamespace

from app.models import Article
from app.services.analysis_service import _aggregate_topic_stats, _parse_idx


def _arts(n: int) -> list[Article]:
    return [Article(id=i, title=f"文章{i}") for i in range(1, n + 1)]


def _metrics(n: int) -> dict:
    return {i: SimpleNamespace(read_num=i * 100, like_num=i * 10)
            for i in range(1, n + 1)}


def test_parse_idx_accepts_common_shapes():
    assert _parse_idx(3) == 3
    assert _parse_idx("3") == 3
    assert _parse_idx("#3") == 3
    assert _parse_idx("  #12 ") == 12
    assert _parse_idx(3.0) == 3
    assert _parse_idx("第5篇") == 5
    assert _parse_idx(True) is None
    assert _parse_idx("abc") is None
    assert _parse_idx(None) is None
    assert _parse_idx(2.5) is None


def test_aggregate_with_string_hash_indices():
    """#2 风格字符串序号：必须正确映射并汇总数字（本次 bug 场景）。"""
    rj = {"topics": [
        {"name": "议题A", "summary": "s", "article_indices": ["#2", "#1", "#2"]},
        {"name": "议题B", "summary": "s", "article_indices": ["3"]},
    ]}
    out = _aggregate_topic_stats(rj, _arts(3), _metrics(3))
    a, b = out["topics"]
    assert a["article_ids"] == [2, 1]          # 去重且保序
    assert a["article_count"] == 2
    assert a["total_read"] == 300              # 200 + 100
    assert a["total_like"] == 30
    assert [t["id"] for t in a["top_articles"]] == [2, 1]  # 按阅读降序
    assert b["article_count"] == 1
    assert out["article_total"] == 3


def test_aggregate_filters_out_of_range_and_garbage():
    rj = {"topics": [
        {"name": "议题A", "article_indices": [0, 4, -1, "x", 2]},
    ]}
    out = _aggregate_topic_stats(rj, _arts(3), _metrics(3))
    assert out["topics"][0]["article_ids"] == [2]
    assert out["topics"][0]["article_count"] == 1


def test_aggregate_empty_topics():
    out = _aggregate_topic_stats({}, _arts(2), _metrics(2))
    assert out["topics"] == []
    assert out["article_total"] == 2
