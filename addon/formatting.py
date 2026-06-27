from __future__ import annotations

from datetime import datetime

try:
    from .analytics import MissedCardSummary
except ImportError:
    from analytics import MissedCardSummary


def format_review_date(reviewed_at: datetime | None) -> str:
    if reviewed_at is None:
        return "Not yet"
    return reviewed_at.strftime("%Y-%m-%d")


def priority_label(summary: MissedCardSummary) -> str:
    if summary.miss_rate >= 0.75 and summary.misses >= 3:
        return "Often needs another pass"
    if summary.misses >= 3:
        return "Needs attention"
    return "Recently difficult"
