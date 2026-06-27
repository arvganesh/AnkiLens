from __future__ import annotations

import re


_WORD_RE = re.compile(r"[a-z][a-z0-9-]{2,}", re.IGNORECASE)
_STOPWORDS = {
    "and",
    "are",
    "for",
    "from",
    "the",
    "this",
    "that",
    "with",
    "what",
    "when",
    "where",
    "which",
}


def frequent_terms(texts: list[str], *, limit: int = 8) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for text in texts:
        for word in _WORD_RE.findall(text.lower()):
            if word not in _STOPWORDS:
                counts[word] = counts.get(word, 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
