from __future__ import annotations

from collections import Counter
import re
from typing import Any


STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "is",
    "it", "of", "on", "or", "that", "the", "this", "to", "with",
}


def extract_keywords(text: str = "", max_keywords: int = 5) -> dict[str, Any]:
    """Return frequent non-stopword terms from supplied text, in first-use order."""
    limit = max(1, min(int(max_keywords), 20))
    tokens = re.findall(r"[^\W\d_][\w'-]*", text.lower(), flags=re.UNICODE)
    filtered = [token for token in tokens if len(token) > 1 and token not in STOP_WORDS]
    counts = Counter(filtered)
    first_position = {token: index for index, token in enumerate(filtered)}
    ranked = sorted(counts, key=lambda token: (-counts[token], first_position[token]))[:limit]
    return {"tool": "keywords", "keywords": ranked, "count": len(ranked)}
