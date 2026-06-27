from __future__ import annotations

import re


_NUMBER_RE = re.compile(r"\d")
_MEDIA_RE = re.compile(r"\[(?:sound|anki:play)[^\]]*\]|\.(?:png|jpe?g|gif|svg|webp)\b", re.IGNORECASE)
_COMPARISON_RE = re.compile(r"\b(?:vs\.?|versus|compared with|differentiate|distinguish)\b", re.IGNORECASE)


def content_labels(text: str) -> tuple[str, ...]:
    labels = []
    words = text.split()
    if 0 < len(words) <= 3:
        labels.append("Weak cue")
    if len(words) >= 80:
        labels.append("Long card")
    if len(words) >= 40 and _sentence_count(text) <= 2:
        labels.append("Dense card")
    if len(_NUMBER_RE.findall(text)) >= 6:
        labels.append("Many numbers")
    if "{{c" in text.lower() or text.count("[...]") >= 2:
        labels.append("Cloze-heavy")
    if _list_marker_count(text) >= 3:
        labels.append("List-like")
    if _COMPARISON_RE.search(text):
        labels.append("Comparison")
    if _MEDIA_RE.search(text):
        labels.append("Media reference")
    return tuple(labels)


def _sentence_count(text: str) -> int:
    return max(1, sum(text.count(mark) for mark in ".?!"))


def _list_marker_count(text: str) -> int:
    return text.count(";") + text.count(",") + text.count("\n-") + text.count("\n*")
