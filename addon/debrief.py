from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

try:
    from .analytics import (
        AGAIN_EASE,
        MissedCardSummary,
        ReviewLogEntry,
        summarize_content_patterns,
        summarize_deck_misses,
        summarize_missed_cards,
        summarize_tag_misses,
        summarize_terms,
    )
except ImportError:
    from analytics import (
        AGAIN_EASE,
        MissedCardSummary,
        ReviewLogEntry,
        summarize_content_patterns,
        summarize_deck_misses,
        summarize_missed_cards,
        summarize_tag_misses,
        summarize_terms,
    )


@dataclass(frozen=True)
class StudyTarget:
    label: str
    kind: str
    count: int
    related_cards: tuple[str, ...] = ()


@dataclass(frozen=True)
class CardsToFix:
    count: int
    clues: tuple[tuple[str, int], ...]
    cards: tuple[MissedCardSummary, ...]


@dataclass(frozen=True)
class SessionHabits:
    review_count: int
    again_count: int
    again_rate: float
    time_of_day: str
    timed_review_count: int = 0
    recorded_answer_seconds: float | None = None
    seconds_per_timed_card: float | None = None


@dataclass(frozen=True)
class Debrief:
    study_next: tuple[StudyTarget, ...]
    cards_to_fix: CardsToFix
    session_habits: SessionHabits
    missed_cards: tuple[MissedCardSummary, ...]


def build_debrief(
    entries: list[ReviewLogEntry],
    *,
    minimum_misses: int = 2,
    result_limit: int = 20,
    study_limit: int = 3,
) -> Debrief:
    missed_cards = summarize_missed_cards(entries, minimum_misses=minimum_misses, limit=result_limit)
    return Debrief(
        study_next=tuple(_study_targets(missed_cards, limit=study_limit)),
        cards_to_fix=_cards_to_fix(missed_cards),
        session_habits=_session_habits(entries),
        missed_cards=tuple(missed_cards),
    )


def _study_targets(summaries: list[MissedCardSummary], *, limit: int) -> list[StudyTarget]:
    targets: list[StudyTarget] = []
    targets.extend(
        StudyTarget(term, "term", count, _related_cards(summaries, lambda summary, term=term: term in summary.source_text.lower()))
        for term, count in summarize_terms(summaries)
    )
    targets.extend(
        StudyTarget(
            deck.deck_name,
            "deck",
            deck.missed_cards,
            _related_cards(summaries, lambda summary, deck_name=deck.deck_name: summary.deck_name == deck_name),
        )
        for deck in summarize_deck_misses(summaries)
    )
    targets.extend(
        StudyTarget(tag.tag, "tag", tag.missed_cards, _related_cards(summaries, lambda summary, tag=tag.tag: tag in summary.tags))
        for tag in summarize_tag_misses(summaries)
    )
    return sorted(targets, key=lambda target: (-target.count, _kind_priority(target.kind), target.label))[:limit]


def _cards_to_fix(summaries: list[MissedCardSummary]) -> CardsToFix:
    cards = tuple(summary for summary in summaries if summary.content_labels)
    clues = tuple(summarize_content_patterns(list(cards)).items())
    return CardsToFix(count=len(cards), clues=clues, cards=cards)


def _kind_priority(kind: str) -> int:
    return {"term": 0, "deck": 1, "tag": 2}.get(kind, 3)


def _related_cards(summaries: list[MissedCardSummary], matches) -> tuple[str, ...]:
    labels = []
    seen_card_ids = set()
    for summary in summaries:
        if matches(summary) and summary.card_id not in seen_card_ids:
            seen_card_ids.add(summary.card_id)
            labels.append(summary.card_label)
    return tuple(labels[:3])


def _session_habits(entries: list[ReviewLogEntry]) -> SessionHabits:
    ordered = sorted(entries, key=lambda entry: entry.reviewed_at)
    review_count = len(ordered)
    again_count = sum(1 for entry in ordered if entry.ease == AGAIN_EASE)
    durations = _valid_durations_ms(ordered)
    total_seconds = sum(durations) / 1000 if durations else None
    return SessionHabits(
        review_count=review_count,
        again_count=again_count,
        again_rate=again_count / review_count if review_count else 0,
        time_of_day=_time_of_day(ordered[-1].reviewed_at) if ordered else "No reviews",
        timed_review_count=len(durations),
        recorded_answer_seconds=total_seconds,
        seconds_per_timed_card=(total_seconds / len(durations)) if total_seconds is not None else None,
    )


def _valid_durations_ms(entries: list[ReviewLogEntry]) -> list[int]:
    return [entry.duration_ms for entry in entries if entry.duration_ms is not None and entry.duration_ms >= 0]


def _time_of_day(reviewed_at: datetime) -> str:
    hour = reviewed_at.hour
    if 5 <= hour < 12:
        return "Morning"
    if 12 <= hour < 17:
        return "Afternoon"
    if 17 <= hour < 22:
        return "Evening"
    return "Late night"
