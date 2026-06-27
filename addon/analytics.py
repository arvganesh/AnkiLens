from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


AGAIN_EASE = 1


@dataclass(frozen=True)
class ReviewLogEntry:
    card_id: int
    ease: int
    reviewed_at: datetime
    deck_name: str
    card_label: str


@dataclass(frozen=True)
class MissedCardSummary:
    card_id: int
    deck_name: str
    card_label: str
    misses: int
    total_reviews: int
    last_missed_at: datetime | None

    @property
    def miss_rate(self) -> float:
        if self.total_reviews == 0:
            return 0
        return self.misses / self.total_reviews


def summarize_missed_cards(
    entries: list[ReviewLogEntry],
    *,
    minimum_misses: int = 2,
    limit: int = 20,
) -> list[MissedCardSummary]:
    grouped: dict[int, list[ReviewLogEntry]] = {}
    for entry in entries:
        grouped.setdefault(entry.card_id, []).append(entry)

    summaries = [_summarize_card(card_entries) for card_entries in grouped.values()]
    candidates = [summary for summary in summaries if summary.misses >= minimum_misses]
    return sorted(candidates, key=_priority, reverse=True)[:limit]


def _summarize_card(entries: list[ReviewLogEntry]) -> MissedCardSummary:
    ordered = sorted(entries, key=lambda entry: entry.reviewed_at)
    missed = [entry for entry in ordered if entry.ease == AGAIN_EASE]
    latest = ordered[-1]

    return MissedCardSummary(
        card_id=latest.card_id,
        deck_name=latest.deck_name,
        card_label=latest.card_label,
        misses=len(missed),
        total_reviews=len(ordered),
        last_missed_at=missed[-1].reviewed_at if missed else None,
    )


def _priority(summary: MissedCardSummary) -> tuple[float, int, datetime]:
    last_missed = summary.last_missed_at or datetime.min
    return (summary.miss_rate, summary.misses, last_missed)
