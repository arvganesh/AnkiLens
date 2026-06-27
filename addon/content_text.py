from __future__ import annotations

import html
import re


FIELD_SEPARATOR = "\x1f"
_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def clean_card_text(raw_text: str) -> str:
    decoded = html.unescape(raw_text.replace(FIELD_SEPARATOR, " "))
    without_breaks = re.sub(r"(?i)<br\s*/?>|</div>|</p>|</li>", " ", decoded)
    without_tags = _TAG_RE.sub(" ", without_breaks)
    return _WHITESPACE_RE.sub(" ", without_tags).strip()
