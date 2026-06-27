from __future__ import annotations

import re


_WORD_RE = re.compile(r"[a-z][a-z0-9-]*", re.IGNORECASE)
_STOPWORDS = {
    "and",
    "anki",
    "are",
    "back",
    "basic",
    "card",
    "deck",
    "for",
    "front",
    "from",
    "note",
    "test",
    "the",
    "this",
    "that",
    "with",
    "what",
    "when",
    "where",
    "which",
}


def frequent_terms(texts: list[str], *, limit: int = 8, minimum_cards: int = 2) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for text in texts:
        for term in set(_terms_in_text(text)):
            counts[term] = counts.get(term, 0) + 1
    repeated = [(term, count) for term, count in counts.items() if count >= minimum_cards]
    return sorted(repeated, key=lambda item: (-item[1], item[0]))[:limit]


def _terms_in_text(text: str) -> list[str]:
    terms = []
    for match in _WORD_RE.findall(text):
        term = match.lower()
        if term not in _STOPWORDS and _is_content_term(match):
            terms.append(term)
    return terms


def _is_content_term(term: str) -> bool:
    return len(term) >= 4 or (term.isupper() and len(term) >= 2)
