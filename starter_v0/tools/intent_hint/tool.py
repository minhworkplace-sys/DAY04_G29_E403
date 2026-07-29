from __future__ import annotations

from typing import Any

from tools._shared import fold_text


def _contains_any(text: str, needles: list[str]) -> bool:
    return any(needle in text for needle in needles)


def intent_hint(text: str = "") -> dict[str, Any]:
    folded = fold_text(text)
    missing_fields: list[str] = []
    suggested_tool = "lookup"
    intent = "web_news"
    confidence = 0.45

    if _contains_any(folded, ["http://", "https://", "www."]):
        if _contains_any(folded, ["arxiv", "paper", "bai bao", "bài báo"]):
            suggested_tool = "paper_text" if _contains_any(folded, ["read", "doc", "text", "noi dung", "nội dung"]) else "papers"
            intent = "paper"
            confidence = 0.9
        else:
            suggested_tool = "fetch"
            intent = "url_read"
            confidence = 0.95
    elif _contains_any(folded, ["tweet", "tweets", "twitter", "x.com", "post", "posts"]):
        if _contains_any(folded, ["latest", "moi nhat", "mới nhất", "recent", "from ", "cua ", "của "]):
            suggested_tool = "timeline"
            intent = "account_timeline"
            confidence = 0.8
        else:
            suggested_tool = "social_search"
            intent = "social_search"
            confidence = 0.78
    elif _contains_any(folded, ["policy", "quy dinh", "quy định", "company policy"]):
        suggested_tool = "policy"
        intent = "internal_policy"
        confidence = 0.92
    elif _contains_any(folded, ["send", "post", "dang", "đăng", "gui", "gửi"]):
        suggested_tool = "send"
        intent = "publish"
        missing_fields.append("confirmed")
        confidence = 0.72
    elif _contains_any(folded, ["paper", "arxiv", "preprint"]):
        suggested_tool = "papers"
        intent = "paper_search"
        confidence = 0.84

    normalized_query = text.strip()
    return {
        "tool": "intent_hint",
        "intent": intent,
        "suggested_tool": suggested_tool,
        "normalized_query": normalized_query,
        "missing_fields": missing_fields,
        "confidence": confidence,
    }
