from __future__ import annotations

try:
    from .debrief import CardsToFix, SessionHabits, StudyTarget
except ImportError:
    from debrief import CardsToFix, SessionHabits, StudyTarget


def study_next_caption(targets: tuple[StudyTarget, ...]) -> str:
    if not targets:
        return "No study pattern yet:\n- No repeated material pattern in this window."
    top_target = targets[0]
    lines = [f"Study: {_target_label(top_target)}", f"- {_target_summary(top_target)}"]
    if len(targets) > 1:
        lines.append("- Also watch: " + "; ".join(_target_summary(target) for target in targets[1:3]))
    return "\n".join(lines)


def _target_summary(target: StudyTarget) -> str:
    detail = (
        f"{target.count} of {target.reviewed_count} reviewed card{_plural(target.reviewed_count)} "
        f"missed in {_target_kind_label(target.kind)}."
    )
    if target.related_cards:
        detail += f" Examples: {', '.join(target.related_cards)}."
    return detail


def _target_label(target: StudyTarget) -> str:
    if target.kind != "tag":
        return target.label
    return target.label.replace("::", " / ").replace("_", " ")


def _target_kind_label(kind: str) -> str:
    return {"tag": "tag", "term": "word", "deck": "deck"}.get(kind, "pattern")


def cards_to_fix_caption(cards_to_fix: CardsToFix) -> str:
    if cards_to_fix.count == 0:
        lines = ["No card repair stands out:", "- No obvious card-construction issue surfaced in this window."]
        if cards_to_fix.early_exposure_count:
            lines.append(
                f"- {cards_to_fix.early_exposure_count} card{_plural(cards_to_fix.early_exposure_count)} "
                f"{_verb(cards_to_fix.early_exposure_count, 'looks', 'look')} early in learning."
            )
        return "\n".join(lines)
    lines = [
        "Cards worth checking:",
        f"- {cards_to_fix.count} card{_plural(cards_to_fix.count)} may be worth checking before studying more.",
    ]
    for card in cards_to_fix.cards[:3]:
        lines.append(f"- {card.card_label}: {', '.join(card.content_labels)}; missed {card.misses}/{card.total_reviews} reviews")
    if cards_to_fix.early_exposure_count:
        lines.append(
            f"- {cards_to_fix.early_exposure_count} card{_plural(cards_to_fix.early_exposure_count)} "
            f"{_verb(cards_to_fix.early_exposure_count, 'looks', 'look')} early in learning."
        )
    if cards_to_fix.clues:
        clues = ", ".join(f"{label}: {count}" for label, count in cards_to_fix.clues)
        lines.append(f"- Common clues: {clues}")
    return "\n".join(lines)


def review_habits_caption(habits: SessionHabits) -> str:
    if habits.review_count == 0:
        return "Review habits:\n- No reviews found in this window."
    lines = [
        "Review habits:",
        f"- Reviews: {habits.review_count}",
        f"- Again rate: {habits.again_rate:.0%} ({habits.again_count} Again ratings)",
        f"- Latest review time: {habits.time_of_day}",
    ]
    if habits.recorded_answer_seconds is not None and habits.seconds_per_timed_card is not None:
        lines.append(f"- Recorded answer time: {_format_seconds(habits.recorded_answer_seconds)}")
        lines.append(f"- Avg/card: {habits.seconds_per_timed_card:.1f}s across {habits.timed_review_count} timed reviews")
    return "\n".join(lines)


def _plural(count: int) -> str:
    return "" if count == 1 else "s"


def _verb(count: int, singular: str, plural: str) -> str:
    return singular if count == 1 else plural


def _format_seconds(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    remainder = seconds % 60
    return f"{minutes}m {remainder:.0f}s"
