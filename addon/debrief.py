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
    early_count: int = 0
    mature_count: int = 0
    lapsed_count: int = 0
    source_count: int = 0
    related_card_ids: tuple[int, ...] = ()

    @property
    def miss_rate(self) -> float:
        if self.reviewed_count == 0:
            return 0
        return self.count / self.reviewed_count

    @property
    def mostly_early(self) -> bool:
        return self.early_count >= 2 and self.early_count > self.mature_count + self.lapsed_count


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
class LlmImprovement:
    insight: str
    action: str


@dataclass(frozen=True)
class LlmDebriefSummary:
    positives: tuple[str, ...]
    improvements: tuple[LlmImprovement, ...]
    action_card_ids: tuple[int, ...] = ()


@dataclass(frozen=True)
class DebriefEvidence:
    reviewed_cards: int
    missed_cards: int
    reviews: int
    misses: int

    @property
    def again_rate(self) -> float:
        if self.reviews == 0:
            return 0
        return self.misses / self.reviews


@dataclass(frozen=True)
class Debrief:
    study_next: tuple[StudyTarget, ...]
    cards_to_fix: CardsToFix
    early_learning: EarlyLearning
    session_habits: SessionHabits
    evidence: DebriefEvidence
    missed_cards: tuple[MissedCardSummary, ...]
    same_note_cluster: MissedCardSummary | None = None
    llm_summary: LlmDebriefSummary | None = None

    @property
    def next_check_kind(self) -> str:
        if self.repair_is_top_check:
            return "repair"
        if self.early_learning_is_dominant:
            return "early_learning"
        if self.same_note_cluster and self.study_next and _same_note_dominates_target(
            self.same_note_cluster,
            self.study_next[0],
            self.missed_cards,
        ):
            return "same_note"
        if self.study_next:
            return "study"
        if self.same_note_cluster:
            return "same_note"
        return "none"

    @property
    def early_learning_is_dominant(self) -> bool:
        return (
            self.early_learning.count >= 2
            and all(_is_fresh_exposure(summary) for summary in self.early_learning.cards)
            and all(_is_fresh_exposure(summary) for summary in self.missed_cards)
        )

    @property
    def repair_is_top_check(self) -> bool:
        if not self.cards_to_fix.cards:
            return False
        if not self.study_next:
            return True
        repair = self.cards_to_fix.cards[0]
        study = self.study_next[0]
        return (
            self.cards_to_fix.count >= study.count
            or repair.misses >= study.count
            or (_severe_repair_signal(repair) and study.miss_rate <= 0.30)
        )


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
        cards_to_fix=_cards_to_fix(all_missed_cards),
        early_learning=early_learning,
        session_habits=_session_habits(entries),
        evidence=_debrief_evidence(entries),
        missed_cards=tuple(missed_cards),
        same_note_cluster=_same_note_cluster(all_missed_cards),
    )


def _study_targets(entries: list[ReviewLogEntry], summaries: list[MissedCardSummary], *, limit: int) -> list[StudyTarget]:
    tag_targets = [
        StudyTarget(
            tag.tag,
            "tag",
            _matched_summary_count(summaries, lambda summary, tag=tag.tag: tag in summary.tags and _is_active(summary)),
            _reviewed_cards(entries, lambda entry, tag=tag.tag: tag in entry.tags and _is_active(entry)),
            _related_cards(summaries, lambda summary, tag=tag.tag: tag in summary.tags and _is_active(summary)),
            *_target_maturity(summaries, lambda summary, tag=tag.tag: tag in summary.tags and _is_active(summary)),
            _matched_source_count(summaries, lambda summary, tag=tag.tag: tag in summary.tags and _is_active(summary)),
            related_card_ids=_related_card_ids(
                summaries,
                lambda summary, tag=tag.tag: tag in summary.tags and _is_active(summary),
            ),
        )
        for tag in summarize_tag_misses(summaries)
        if _useful_study_tag(tag.tag)
    ]
    tag_targets = _supported_targets(tag_targets, minimum_reviewed=5, minimum_rate=0.25)

    term_targets = [
        StudyTarget(
            term,
            "term",
            count,
            _reviewed_cards(entries, lambda entry, term=term: term in entry.source_text.lower()),
            _related_cards(summaries, lambda summary, term=term: term in summary.source_text.lower()),
            *_target_maturity(summaries, lambda summary, term=term: term in summary.source_text.lower()),
            _matched_source_count(summaries, lambda summary, term=term: term in summary.source_text.lower()),
            related_card_ids=_related_card_ids(
                summaries,
                lambda summary, term=term: term in summary.source_text.lower(),
            ),
        )
        for term, count in summarize_terms(summaries)
    ]
    term_targets = _supported_targets(term_targets, minimum_reviewed=4, minimum_rate=0.25)
    content_targets = sorted(tag_targets + term_targets, key=_target_priority)
    if content_targets:
        return content_targets[:limit]

    targets = [
        StudyTarget(
            deck.deck_name,
            "deck",
            deck.missed_cards,
            _reviewed_cards(entries, lambda entry, deck_name=deck.deck_name: entry.deck_name == deck_name),
            _related_cards(summaries, lambda summary, deck_name=deck.deck_name: summary.deck_name == deck_name),
            *_target_maturity(summaries, lambda summary, deck_name=deck.deck_name: summary.deck_name == deck_name),
            _matched_source_count(summaries, lambda summary, deck_name=deck.deck_name: summary.deck_name == deck_name),
            related_card_ids=_related_card_ids(
                summaries,
                lambda summary, deck_name=deck.deck_name: summary.deck_name == deck_name,
            ),
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


def _same_note_cluster(summaries: list[MissedCardSummary]) -> MissedCardSummary | None:
    candidates = [
        summary
        for summary in summaries
        if summary.note_id
        and summary.note_card_count
        and summary.note_card_count > 1
        and summary.note_repeated_miss_count >= 2
        and not summary.is_early_exposure
    ]
    return candidates[0] if candidates else None


def _same_note_dominates_target(
    cluster_card: MissedCardSummary,
    target: StudyTarget,
    summaries: tuple[MissedCardSummary, ...],
) -> bool:
    note_id = cluster_card.note_id
    if not note_id or not cluster_card.note_card_count or cluster_card.note_card_count <= 1:
        return False
    matched_cards = {
        summary.card_id
        for summary in summaries
        if _target_matches_summary(target, summary) and not summary.is_early_exposure
    }
    if not matched_cards:
        return False
    same_note_cards = {
        summary.card_id
        for summary in summaries
        if summary.card_id in matched_cards and summary.note_id == note_id
    }
    return len(same_note_cards) > len(matched_cards) / 2


def _target_matches_summary(target: StudyTarget, summary: MissedCardSummary) -> bool:
    if target.kind == "tag":
        return target.label in summary.tags and _is_active(summary)
    if target.kind == "term":
        return target.label in summary.source_text.lower()
    if target.kind == "deck":
        return summary.deck_name == target.label
    return False


def _is_fresh_exposure(summary: MissedCardSummary) -> bool:
    return summary.is_early_exposure and (
        summary.misses == 1 or (summary.card_reps is not None and summary.card_reps <= 2)
    )


def _has_repair_signal(summary: MissedCardSummary) -> bool:
    labels = set(summary.content_labels)
    return bool(labels & _STRONG_REPAIR_LABELS) or len(labels) >= 2


def _severe_repair_signal(summary: MissedCardSummary) -> bool:
    labels = set(summary.content_labels)
    return summary.miss_rate >= 0.75 and len(labels & _STRONG_REPAIR_LABELS) >= 2


def _kind_priority(kind: str) -> int:
    return {"tag": 0, "term": 1, "deck": 2}.get(kind, 3)


def _target_priority(target: StudyTarget) -> tuple[int, int, int, float, int, int, str]:
    return (
        _specific_topic_priority(target),
        _support_priority(target),
        -target.count,
        -target.miss_rate,
        _kind_priority(target.kind),
        -_tag_specificity(target),
        target.label,
    )


def _support_priority(target: StudyTarget) -> int:
    if target.count >= 4 and target.reviewed_count >= 10:
        return 0
    if target.reviewed_count >= 10:
        return 1
    return 2


_BROAD_TAG_PARTS = frozenset({"ak", "anking", "deck", "decks", "step", "step1", "step2", "v11", "v12"})
_IGNORED_STUDY_TAGS = frozenset({"insights_demo", "bonsai_demo"})


def _useful_study_tag(tag: str) -> bool:
    if tag.lower() in _IGNORED_STUDY_TAGS:
        return False
    parts = _tag_parts(tag)
    if not parts:
        return False
    return any(part not in _BROAD_TAG_PARTS and not part.startswith("v") for part in parts)


def _tag_specificity(target: StudyTarget) -> int:
    if target.kind != "tag":
        return 0
    return len([part for part in _tag_parts(target.label) if part not in _BROAD_TAG_PARTS])


def _specific_topic_priority(target: StudyTarget) -> int:
    parts = _tag_parts(target.label) if target.kind == "tag" else []
    if target.kind == "tag" and _tag_specificity(target) >= 2 and target.count >= 4:
        return 0
    return 1


def _tag_parts(tag: str) -> list[str]:
    return [part.lower() for part in tag.replace("::", "_").split("_") if part]


def _supported_targets(targets: list[StudyTarget], *, minimum_reviewed: int, minimum_rate: float) -> list[StudyTarget]:
    return [
        target
        for target in targets
        if target.reviewed_count >= minimum_reviewed and target.source_count >= 2 and target.miss_rate >= minimum_rate
    ]


def _matched_summary_count(summaries: list[MissedCardSummary], matches) -> int:
    return len({summary.card_id for summary in summaries if matches(summary)})


def _matched_source_count(summaries: list[MissedCardSummary], matches) -> int:
    return len({_study_evidence_id(summary) for summary in summaries if matches(summary)})


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


def _related_card_ids(summaries: list[MissedCardSummary], matches) -> tuple[int, ...]:
    card_ids = []
    seen_card_ids = set()
    for summary in summaries:
        if matches(summary) and summary.card_id not in seen_card_ids:
            seen_card_ids.add(summary.card_id)
            card_ids.append(summary.card_id)
    return tuple(card_ids[:3])


def _target_maturity(summaries: list[MissedCardSummary], matches) -> tuple[int, int, int]:
    early = mature = lapsed = 0
    seen_card_ids = set()
    for summary in summaries:
        if not matches(summary) or summary.card_id in seen_card_ids:
            continue
        seen_card_ids.add(summary.card_id)
        if summary.is_early_exposure:
            early += 1
        elif summary.card_lapses and summary.card_lapses > 0:
            lapsed += 1
        else:
            mature += 1
    return early, mature, lapsed


def _study_evidence_id(item) -> tuple[str, int]:
    note_id = getattr(item, "note_id", None)
    if note_id is not None:
        return ("note", note_id)
    return ("card", item.card_id)


def _is_active(item) -> bool:
    return getattr(item, "card_queue", None) != -1


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


def _debrief_evidence(entries: list[ReviewLogEntry]) -> DebriefEvidence:
    return DebriefEvidence(
        reviewed_cards=len({entry.card_id for entry in entries}),
        missed_cards=len({entry.card_id for entry in entries if entry.ease == AGAIN_EASE}),
        reviews=len(entries),
        misses=sum(1 for entry in entries if entry.ease == AGAIN_EASE),
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
