from __future__ import annotations

from dataclasses import dataclass

try:
    from .analytics import DEFAULT_MISS_EASES, ReviewLogEntry
except ImportError:
    from analytics import DEFAULT_MISS_EASES, ReviewLogEntry


@dataclass(frozen=True)
class LlmImprovement:
    insight: str
    action: str


@dataclass(frozen=True)
class LlmDebriefSummary:
    positives: tuple[str, ...]
    improvements: tuple[LlmImprovement, ...]
    study_suggestions: tuple[LlmImprovement, ...] = ()
    action_card_ids: tuple[int, ...] = ()

    @property
    def card_improvements(self) -> tuple[LlmImprovement, ...]:
        return self.improvements


@dataclass(frozen=True)
class LlmDebriefError:
    message: str


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
    evidence: DebriefEvidence
    llm_summary: LlmDebriefSummary | LlmDebriefError | None = None


def build_debrief(
    entries: list[ReviewLogEntry],
    *,
    minimum_misses: int = 2,
    result_limit: int = 20,
    miss_eases: tuple[int, ...] = DEFAULT_MISS_EASES,
) -> Debrief:
    return Debrief(evidence=build_debrief_evidence(entries, miss_eases=miss_eases))


def build_debrief_evidence(entries: list[ReviewLogEntry], *, miss_eases: tuple[int, ...] = DEFAULT_MISS_EASES) -> DebriefEvidence:
    return DebriefEvidence(
        reviewed_cards=len({entry.card_id for entry in entries}),
        missed_cards=len({entry.card_id for entry in entries if entry.ease in miss_eases}),
        reviews=len(entries),
        misses=sum(1 for entry in entries if entry.ease in miss_eases),
    )
