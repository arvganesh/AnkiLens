from __future__ import annotations

try:
    from .analytics import DeckMissSummary, MissedCardSummary, TagMissSummary
    from .browser_search import browser_search_for_card
except ImportError:
    from analytics import DeckMissSummary, MissedCardSummary, TagMissSummary
    from browser_search import browser_search_for_card


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
            f"Cards appear here after needing another pass {minimum_misses} time{_plural(minimum_misses)} {window}."
        )
    return (
        f"Supporting evidence for the debrief: {shown_count} card{_plural(shown_count)} "
        f"needed another pass at least {minimum_misses} times {window}. Limit: {result_limit}."
    )


def evidence_window_title() -> str:
    return "Bonsai Evidence Table"


def evidence_title() -> str:
    return "Evidence Table"


def workflow_caption() -> str:
    return "Use this to inspect the cards behind the recommendation before deciding to edit or study more."


def check_cards_caption() -> str:
    return "Inspect card format"


def study_content_caption() -> str:
    return "Material evidence to sample"


def supporting_metric_labels() -> tuple[str, str, str]:
    return ("cards to inspect", "repeated misses", "evidence window")


def supporting_table_headers() -> tuple[str, ...]:
    return ("Card", "Deck", "Triage", "Format clues", "Misses", "Reviews", "Miss rate", "Last missed")


def selected_card_button_text() -> str:
    return "Open selected card in Browse"


def selected_card_status_text(query: str, *, opened: bool) -> str:
    if opened:
        return "Opened in Browse. Search copied."
    return f"Copied: {query}"


def card_detail_caption(summary: MissedCardSummary) -> str:
    clues = ", ".join(summary.content_labels) if summary.content_labels else "No obvious clue"
    text = _preview_text(summary.source_text)
    lines = [
        f"Selected card: {summary.card_label}",
        f"Format clues: {clues}",
        f"Misses: {summary.misses}/{summary.total_reviews} reviews ({summary.miss_rate:.0%})",
        f"Browser search: {browser_search_for_card(summary.card_id)}",
    ]
    note_context = same_note_context(summary)
    if note_context:
        lines.insert(2, note_context)
    if text:
        lines.append(f"Text: {text}")
    return "\n".join(lines)


def same_note_context(summary: MissedCardSummary) -> str:
    if not summary.note_id or not summary.note_card_count or summary.note_card_count <= 1:
        return ""
    repeated = summary.note_repeated_miss_count or 1
    if repeated <= 1:
        return f"Same note: only this card flagged out of {summary.note_card_count}"
    return f"Same note: {repeated} of {summary.note_card_count} cards flagged"


def _plural(count: int) -> str:
    return "" if count == 1 else "s"


def _preview_text(text: str, *, limit: int = 180) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[: limit - 1].rstrip()}..."


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
    lines = ["Possible format clues:"]
    lines.extend(f"- {label}: {count} card{_plural(count)}" for label, count in pattern_counts.items())
    return "\n".join(lines)


def term_caption(terms: list[tuple[str, int]]) -> str:
    if not terms:
        return ""
    lines = ["Repeated terms to sample:"]
    lines.extend(f"- {term}: {count}" for term, count in terms)
    return "\n".join(lines)
