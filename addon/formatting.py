from __future__ import annotations

from datetime import datetime


def format_review_date(reviewed_at: datetime | None) -> str:
    if reviewed_at is None:
        return "Not yet"
    return reviewed_at.strftime("%Y-%m-%d")
