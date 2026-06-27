from __future__ import annotations

try:
    from .debrief import CardsToFix, SessionHabits, StudyTarget
except ImportError:
    from debrief import CardsToFix, SessionHabits, StudyTarget


def study_next_caption(targets: tuple[StudyTarget, ...]) -> str:
    if not targets:
        return "Study material:\n- No repeated material pattern found in this window."
    lines = ["Study material if the cards look okay:"]
    for target in targets:
        related = f"; examples: {', '.join(target.related_cards)}" if target.related_cards else ""
        lines.append(f"- {target.label} ({target.kind}, {target.count} cards{related})")
    return "\n".join(lines)


def cards_to_fix_caption(cards_to_fix: CardsToFix) -> str:
    if cards_to_fix.count == 0:
        return (
            "Check first: card issue or unstudied material?\n"
            "- No repeated-miss cards with obvious construction clues found.\n"
            "- If this material is new, review the source material before doing more cards."
        )
    card = cards_to_fix.cards[0] if cards_to_fix.cards else None
    lines = [
        "Check first: card issue or unstudied material?",
        f"- {cards_to_fix.count} card{_plural(cards_to_fix.count)} may be worth fixing before studying more.",
    ]
    if card:
        lines.append(f"- Start with: {card.card_label}")
        lines.append(f"- Why: {', '.join(card.content_labels)}; missed {card.misses}/{card.total_reviews} reviews")
        lines.append(f"- Next: open the card and check whether the prompt is specific enough.")
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


def _format_seconds(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    remainder = seconds % 60
    return f"{minutes}m {remainder:.0f}s"
