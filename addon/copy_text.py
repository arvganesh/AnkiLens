from __future__ import annotations

try:
    from .analytics import DeckMissSummary
except ImportError:
    from analytics import DeckMissSummary


def analytics_caption(
    *,
    shown_count: int,
    minimum_misses: int,
    result_limit: int,
    lookback_days: int,
) -> str:
    window = _lookback_label(lookback_days)
    if shown_count == 0:
        return (
            f"No repeated misses found {window}.\n\n"
            f"When a card needs another pass at least {minimum_misses} times, "
            "Bonsai will show it here."
        )
    return (
        f"Showing {shown_count} card{_plural(shown_count)} that needed another pass "
        f"at least {minimum_misses} times {window}. Limit: {result_limit}."
    )


def _plural(count: int) -> str:
    return "" if count == 1 else "s"


def _lookback_label(lookback_days: int) -> str:
    if lookback_days <= 0:
        return "across all time"
    return f"in the last {lookback_days} days"


def deck_concentration_caption(decks: list[DeckMissSummary]) -> str:
    if not decks:
        return ""
    lines = ["Where repeated misses are concentrated:"]
    lines.extend(
        f"- {deck.deck_name}: {deck.missed_cards} card{_plural(deck.missed_cards)}, {deck.misses} misses"
        for deck in decks
    )
    return "\n".join(lines)
