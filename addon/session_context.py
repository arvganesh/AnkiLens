from __future__ import annotations

try:
    from .debrief import SessionHabits
except ImportError:
    from debrief import SessionHabits


def session_context_text(habits: SessionHabits) -> str:
    if habits.review_count < 5:
        return ""
    parts = [
        f"Context: {habits.review_count} reviews",
        f"{habits.again_rate:.0%} Again",
        habits.time_of_day.lower(),
    ]
    if has_reliable_timing(habits):
        parts.append(f"{habits.seconds_per_timed_card:.1f}s/card")
    return " · ".join(parts)


def has_reliable_timing(habits: SessionHabits) -> bool:
    return (
        habits.seconds_per_timed_card is not None
        and habits.timed_review_count >= max(5, int(habits.review_count * 0.8))
    )
