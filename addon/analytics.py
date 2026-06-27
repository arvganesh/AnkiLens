from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


AGAIN_EASE = 1


@dataclass(frozen=True)
class ReviewLogEntry:
    card_id: int
    ease: int
    reviewed_at: datetime
    deck_name: str
    card_label: str
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class MissedCardSummary:
    card_id: int
    deck_name: str
    card_label: str
    misses: int
    total_reviews: int
    last_missed_at: datetime | None
    tags: tuple[str, ...] = ()

    @property
    def miss_rate(self) -> float:
        if self.total_reviews == 0:
            return 0
        return self.misses / self.total_reviews


@dataclass(frozen=True)
class DeckMissSummary:
    deck_name: str
    missed_cards: int
    misses: int


@dataclass(frozen=True)
class TagMissSummary:
    tag: str
    missed_cards: int
    misses: int


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


def filter_review_entries_by_lookback(
    entries: list[ReviewLogEntry],
    *,
    lookback_days: int,
    now: datetime,
) -> list[ReviewLogEntry]:
    if lookback_days <= 0:
        return entries
    cutoff = now - timedelta(days=lookback_days)
    return [entry for entry in entries if entry.reviewed_at >= cutoff]


def summarize_deck_misses(summaries: list[MissedCardSummary], *, limit: int = 5) -> list[DeckMissSummary]:
    grouped: dict[str, DeckMissSummary] = {}
    for summary in summaries:
        current = grouped.get(summary.deck_name)
        grouped[summary.deck_name] = DeckMissSummary(
            deck_name=summary.deck_name,
            missed_cards=(current.missed_cards if current else 0) + 1,
            misses=(current.misses if current else 0) + summary.misses,
        )
    return sorted(grouped.values(), key=lambda deck: (deck.misses, deck.missed_cards), reverse=True)[:limit]


def summarize_tag_misses(summaries: list[MissedCardSummary], *, limit: int = 5) -> list[TagMissSummary]:
    grouped: dict[str, TagMissSummary] = {}
    for summary in summaries:
        for tag in summary.tags:
            current = grouped.get(tag)
            grouped[tag] = TagMissSummary(
                tag=tag,
                missed_cards=(current.missed_cards if current else 0) + 1,
                misses=(current.misses if current else 0) + summary.misses,
            )
    return sorted(grouped.values(), key=lambda tag: (tag.misses, tag.missed_cards), reverse=True)[:limit]


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
        tags=latest.tags,
    )


def _priority(summary: MissedCardSummary) -> tuple[float, int, datetime]:
    last_missed = summary.last_missed_at or datetime.min
    return (summary.miss_rate, summary.misses, last_missed)
