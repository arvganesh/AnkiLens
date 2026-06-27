from __future__ import annotations


def analytics_caption(*, shown_count: int, minimum_misses: int, result_limit: int) -> str:
    if shown_count == 0:
        return (
            "No repeated misses found yet.\n\n"
            f"When a card needs another pass at least {minimum_misses} times, "
            "Bonsai will show it here."
        )
    return (
        f"Showing {shown_count} card{_plural(shown_count)} that needed another pass "
        f"at least {minimum_misses} times. Limit: {result_limit}."
    )


def _plural(count: int) -> str:
    return "" if count == 1 else "s"
