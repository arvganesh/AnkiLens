from __future__ import annotations

try:
    from .debrief import SessionHabits
except ImportError:
    from debrief import SessionHabits


def session_context_text(habits: SessionHabits) -> str:
    if habits.review_count < 5:
        return ""
    if habits.again_rate >= 0.35:
        return (
            f"Session note: {habits.again_rate:.0%} Again across {habits.review_count} reviews. "
            "If many cards felt new, refresh the source before editing cards."
        )
    if has_reliable_timing(habits) and habits.seconds_per_timed_card < 3:
        return (
            f"Session note: {habits.seconds_per_timed_card:.1f}s/card. "
            "If you were rushing, treat misses as weaker evidence."
        )
    return ""


def has_reliable_timing(habits: SessionHabits) -> bool:
    return (
        habits.seconds_per_timed_card is not None
        and habits.timed_review_count >= max(5, int(habits.review_count * 0.8))
    )
