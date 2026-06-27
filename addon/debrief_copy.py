from __future__ import annotations

try:
    from .debrief import CardsToFix, SessionHabits, StudyTarget
except ImportError:
    from debrief import CardsToFix, SessionHabits, StudyTarget


def study_next_caption(targets: tuple[StudyTarget, ...]) -> str:
    if not targets:
        return "Study next:\n- No repeated content targets found in this window."
    lines = ["Study next:"]
    lines.extend(f"- {target.label} ({target.kind}, {target.count} cards)" for target in targets)
    return "\n".join(lines)


def cards_to_fix_caption(cards_to_fix: CardsToFix) -> str:
    if cards_to_fix.count == 0:
        return "Cards to fix:\n- No repeated-miss cards with construction clues found."
    lines = [f"Cards to fix:\n- {cards_to_fix.count} card{_plural(cards_to_fix.count)} may need editing."]
    if cards_to_fix.clues:
        clues = ", ".join(f"{label}: {count}" for label, count in cards_to_fix.clues)
        lines.append(f"- Common clues: {clues}")
    return "\n".join(lines)


def review_habits_caption(habits: SessionHabits) -> str:
    if habits.review_count == 0:
        return "Review habits:\n- No reviews found in this window."
    return "\n".join(
        [
            "Review habits:",
            f"- Reviews: {habits.review_count}",
            f"- Again rate: {habits.again_rate:.0%} ({habits.again_count} Again ratings)",
            f"- Latest review time: {habits.time_of_day}",
        ]
    )


def _plural(count: int) -> str:
    return "" if count == 1 else "s"
