from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta

try:
    from .content_signals import content_labels
except ImportError:
    from content_signals import content_labels


AGAIN_EASE = 1


@dataclass(frozen=True)
class ReviewLogEntry:
    card_id: int
    ease: int
    reviewed_at: datetime
    deck_name: str
    card_label: str
    note_id: int | None = None
    note_card_count: int | None = None
    tags: tuple[str, ...] = ()
    source_text: str = ""
    duration_ms: int | None = None
    review_type: int | None = None
    card_reps: int | None = None
    card_lapses: int | None = None
    card_type: int | None = None
    card_queue: int | None = None


@dataclass(frozen=True)
class MissedCardSummary:
    card_id: int
    deck_name: str
    card_label: str
    misses: int
    total_reviews: int
    last_missed_at: datetime | None
    tags: tuple[str, ...] = ()
    source_text: str = ""
    content_labels: tuple[str, ...] = ()
    note_id: int | None = None
    note_card_count: int | None = None
    note_repeated_miss_count: int = 0
    first_reviewed_at: datetime | None = None
    learning_review_count: int = 0
    is_early_exposure: bool = False
    card_reps: int | None = None
    card_lapses: int | None = None
    card_queue: int | None = None

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
    candidates = _with_note_context(candidates)
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


def summarize_content_patterns(summaries: list[MissedCardSummary]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for summary in summaries:
        for label in summary.content_labels:
            counts[label] = counts.get(label, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))


def _summarize_card(entries: list[ReviewLogEntry]) -> MissedCardSummary:
    ordered = sorted(entries, key=lambda entry: entry.reviewed_at)
    missed = [entry for entry in ordered if entry.ease == AGAIN_EASE]
    latest = ordered[-1]
    learning_reviews = sum(1 for entry in ordered if entry.review_type in (0, 1, 3))

    return MissedCardSummary(
        card_id=latest.card_id,
        deck_name=latest.deck_name,
        card_label=latest.card_label,
        misses=len(missed),
        total_reviews=len(ordered),
        last_missed_at=missed[-1].reviewed_at if missed else None,
        note_id=latest.note_id,
        note_card_count=latest.note_card_count,
        tags=latest.tags,
        source_text=latest.source_text,
        content_labels=content_labels(latest.source_text),
        first_reviewed_at=ordered[0].reviewed_at,
        learning_review_count=learning_reviews,
        is_early_exposure=_is_early_exposure(ordered, learning_reviews),
        card_reps=latest.card_reps,
        card_lapses=latest.card_lapses,
        card_queue=latest.card_queue,
    )


def _with_note_context(summaries: list[MissedCardSummary]) -> list[MissedCardSummary]:
    repeated_by_note: dict[int, int] = {}
    for summary in summaries:
        if summary.note_id is not None:
            repeated_by_note[summary.note_id] = repeated_by_note.get(summary.note_id, 0) + 1
    return [
        replace(summary, note_repeated_miss_count=repeated_by_note.get(summary.note_id, 0))
        if summary.note_id is not None
        else summary
        for summary in summaries
    ]


def _priority(summary: MissedCardSummary) -> tuple[float, int, datetime]:
    last_missed = summary.last_missed_at or datetime.min
    return (summary.miss_rate, summary.misses, last_missed)


def _is_early_exposure(entries: list[ReviewLogEntry], learning_reviews: int) -> bool:
    latest = entries[-1]
    if latest.card_lapses is not None and latest.card_lapses > 0:
        return False
    if latest.card_reps is not None:
        return latest.card_reps <= 4
    return learning_reviews >= 2 and learning_reviews >= len(entries) / 2
