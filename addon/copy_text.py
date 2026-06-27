from __future__ import annotations

try:
    from .analytics import DeckMissSummary, TagMissSummary
except ImportError:
    from analytics import DeckMissSummary, TagMissSummary


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
            f"Cards appear here after {minimum_misses} Again rating{_plural(minimum_misses)} {window}."
        )
    return (
        f"Showing {shown_count} card{_plural(shown_count)} that needed another pass "
        f"at least {minimum_misses} times {window}. Limit: {result_limit}."
    )


def workflow_caption() -> str:
    return "Repeated misses can mean the card needs editing, the content needs more study, or both."


def check_cards_caption() -> str:
    return "Check the cards first"


def study_content_caption() -> str:
    return "Then study the content"


def _plural(count: int) -> str:
    return "" if count == 1 else "s"


def _lookback_label(lookback_days: int) -> str:
    if lookback_days <= 0:
        return "across all time"
    return f"in the last {lookback_days} days"


def deck_concentration_caption(decks: list[DeckMissSummary]) -> str:
    if not decks:
        return ""
    lines = ["Decks with repeated misses:"]
    lines.extend(
        f"- {deck.deck_name}: {deck.missed_cards} card{_plural(deck.missed_cards)}, {deck.misses} misses"
        for deck in decks
    )
    return "\n".join(lines)


def tag_concentration_caption(tags: list[TagMissSummary]) -> str:
    if not tags:
        return ""
    lines = ["Tags with repeated misses:"]
    lines.extend(
        f"- {tag.tag}: {tag.missed_cards} card{_plural(tag.missed_cards)}, {tag.misses} misses"
        for tag in tags
    )
    return "\n".join(lines)


def content_pattern_caption(pattern_counts: dict[str, int]) -> str:
    if not pattern_counts:
        return ""
    lines = ["Card construction clues:"]
    lines.extend(f"- {label}: {count} card{_plural(count)}" for label, count in pattern_counts.items())
    return "\n".join(lines)


def term_caption(terms: list[tuple[str, int]]) -> str:
    if not terms:
        return ""
    lines = ["Repeated terms to study:"]
    lines.extend(f"- {term}: {count}" for term, count in terms)
    return "\n".join(lines)
