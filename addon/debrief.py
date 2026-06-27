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
    reviewed_count: int
    related_cards: tuple[str, ...] = ()

    @property
    def miss_rate(self) -> float:
        if self.reviewed_count == 0:
            return 0
        return self.count / self.reviewed_count


@dataclass(frozen=True)
class CardsToFix:
    count: int
    clues: tuple[tuple[str, int], ...]
    cards: tuple[MissedCardSummary, ...]


@dataclass(frozen=True)
class EarlyLearning:
    count: int
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
    early_learning: EarlyLearning
    session_habits: SessionHabits
    missed_cards: tuple[MissedCardSummary, ...]

    @property
    def early_learning_is_dominant(self) -> bool:
        return self.early_learning.count >= 2 and all(summary.is_early_exposure for summary in self.missed_cards)

    @property
    def repair_is_top_check(self) -> bool:
        if not self.cards_to_fix.cards:
            return False
        if not self.study_next:
            return True
        repair = self.cards_to_fix.cards[0]
        study = self.study_next[0]
        return self.cards_to_fix.count >= study.count or repair.misses >= study.count


_STRONG_REPAIR_LABELS = frozenset(
    {
        "Long card",
        "Dense card",
        "Many numbers",
        "List-like",
        "Media reference",
    }
)


def build_debrief(
    entries: list[ReviewLogEntry],
    *,
    minimum_misses: int = 2,
    result_limit: int = 20,
    study_limit: int = 3,
) -> Debrief:
    missed_cards = summarize_missed_cards(entries, minimum_misses=minimum_misses, limit=result_limit)
    all_missed_cards = summarize_missed_cards(entries, minimum_misses=minimum_misses, limit=len(entries))
    early_candidates = summarize_missed_cards(entries, minimum_misses=1, limit=len(entries))
    early_learning = _early_learning(early_candidates)
    study_targets = tuple(_study_targets(entries, all_missed_cards, limit=study_limit))
    if not study_targets and early_learning.count >= 2:
        study_targets = tuple(_study_targets(entries, list(early_learning.cards), limit=study_limit))
    return Debrief(
        study_next=study_targets,
        cards_to_fix=_cards_to_fix(missed_cards),
        early_learning=early_learning,
        session_habits=_session_habits(entries),
        missed_cards=tuple(missed_cards),
    )


def _study_targets(entries: list[ReviewLogEntry], summaries: list[MissedCardSummary], *, limit: int) -> list[StudyTarget]:
    tag_targets = [
        StudyTarget(
            tag.tag,
            "tag",
            tag.missed_cards,
            _reviewed_cards(entries, lambda entry, tag=tag.tag: tag in entry.tags),
            _related_cards(summaries, lambda summary, tag=tag.tag: tag in summary.tags),
        )
        for tag in summarize_tag_misses(summaries)
        if tag.missed_cards >= 2
    ]
    tag_targets = _supported_targets(tag_targets, minimum_reviewed=5, minimum_rate=0.25)
    if tag_targets:
        return sorted(tag_targets, key=_target_priority)[:limit]

    term_targets = [
        StudyTarget(
            term,
            "term",
            count,
            _reviewed_cards(entries, lambda entry, term=term: term in entry.source_text.lower()),
            _related_cards(summaries, lambda summary, term=term: term in summary.source_text.lower()),
        )
        for term, count in summarize_terms(summaries)
    ]
    term_targets = _supported_targets(term_targets, minimum_reviewed=4, minimum_rate=0.25)
    if term_targets:
        return sorted(term_targets, key=_target_priority)[:limit]

    targets = [
        StudyTarget(
            deck.deck_name,
            "deck",
            deck.missed_cards,
            _reviewed_cards(entries, lambda entry, deck_name=deck.deck_name: entry.deck_name == deck_name),
            _related_cards(summaries, lambda summary, deck_name=deck.deck_name: summary.deck_name == deck_name),
        )
        for deck in summarize_deck_misses(summaries)
    ]
    return sorted(_supported_targets(targets, minimum_reviewed=5, minimum_rate=0.20), key=_target_priority)[:limit]


def _cards_to_fix(summaries: list[MissedCardSummary]) -> CardsToFix:
    cards = tuple(summary for summary in summaries if _has_repair_signal(summary) and not summary.is_early_exposure)
    clues = tuple(summarize_content_patterns(list(cards)).items())
    return CardsToFix(count=len(cards), clues=clues, cards=cards)


def _early_learning(summaries: list[MissedCardSummary]) -> EarlyLearning:
    cards = tuple(summary for summary in summaries if summary.is_early_exposure)
    return EarlyLearning(count=len(cards), cards=cards)


def _has_repair_signal(summary: MissedCardSummary) -> bool:
    labels = set(summary.content_labels)
    return bool(labels & _STRONG_REPAIR_LABELS) or len(labels) >= 2


def _kind_priority(kind: str) -> int:
    return {"tag": 0, "term": 1, "deck": 2}.get(kind, 3)


def _target_priority(target: StudyTarget) -> tuple[float, int, int, str]:
    return (-target.miss_rate, -target.count, _kind_priority(target.kind), target.label)


def _supported_targets(targets: list[StudyTarget], *, minimum_reviewed: int, minimum_rate: float) -> list[StudyTarget]:
    return [target for target in targets if target.reviewed_count >= minimum_reviewed and target.miss_rate >= minimum_rate]


def _reviewed_cards(entries: list[ReviewLogEntry], matches) -> int:
    return len({entry.card_id for entry in entries if matches(entry)})


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
