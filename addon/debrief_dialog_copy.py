from __future__ import annotations


def debrief_window_title() -> str:
    return "Bonsai Next Check"


def debrief_title() -> str:
    return "Next Check"


def debrief_intro_text(lookback_days: int) -> str:
    if lookback_days <= 0:
        return "Read-only patterns across available reviews. Bonsai does not change scheduling."
    if lookback_days == 1:
        return "Last 24 hours · read-only · Bonsai does not change scheduling."
    return f"Last {lookback_days} days · read-only · Bonsai does not change scheduling."


def deck_debrief_button_text() -> str:
    return "What should I check?"


def study_target_title(label: str) -> str:
    return f"Possible study target: {label}"


def target_display_label(label: str, kind: str) -> str:
    if kind != "tag":
        return label
    parts = label.replace("::", "_").split("_")
    readable = [part for part in parts if part and part.lower() != "anking"]
    return " ".join(readable) if readable else label.replace("_", " ")


def target_evidence_text(count: int, reviewed_count: int, label: str, related_cards: tuple[str, ...] = ()) -> str:
    card_label = "card" if reviewed_count == 1 else "cards"
    evidence = f"{count} of {reviewed_count} {card_label} reviewed in {label} needed another pass."
    if related_cards:
        evidence += f" Examples: {', '.join(related_cards)}."
    return evidence


def early_learning_title() -> str:
    return "Early cards need a light check"


def card_search_button_text() -> str:
    return "Open card in Browse"


def repair_title(label: str) -> str:
    return f"Card worth inspecting: {label}"


def related_search_button_text() -> str:
    return "Find related cards in Browse"


def evidence_confidence_text(
    missed_count: int,
    reviewed_count: int,
    *,
    early_learning: bool = False,
    mixed_signals: bool = False,
) -> str:
    if early_learning:
        return "Early signal"
    if mixed_signals:
        return "Mixed signal"
    if missed_count >= 4 and reviewed_count >= 10 and not mixed_signals:
        return "Supported pattern"
    return "Small pattern"


def supporting_cards_button_text() -> str:
    return "Open evidence table"


def repair_action_summary(card) -> str:
    clues = ", ".join(card.content_labels) if card.content_labels else "repeated misses"
    return (
        f"Needed another pass on {card.misses}/{card.total_reviews} recent reviews; clues: {clues}. "
        "Inspect it first: simplify overloaded wording, or leave it and review the source if the card is clear."
    )


def repair_evidence(card) -> str:
    clues = ", ".join(card.content_labels) if card.content_labels else "repeated misses"
    return f"Needed another pass on {card.misses}/{card.total_reviews} recent reviews; clues: {clues}."


def repair_next_step() -> str:
    return "Inspect the prompt first. If it is clear, study the source instead of editing."


def study_next_step(kind: str) -> str:
    if kind == "tag":
        return "Sample the related cards. If they feel unfamiliar, do a short source refresh before retrying."
    if kind == "term":
        return "Skim the examples with this repeated wording, then review the source if they still feel unfamiliar."
    if kind == "deck":
        return "Treat this as a broad deck signal: sample the related cards before deciding what to study."
    return "Review the related cards, then decide whether the source material needs another pass."


def no_repair_signal_text() -> str:
    return "No obvious card-format issue stood out, so check the source before editing cards."


def mixed_repair_signal_text() -> str:
    return "One card also has format clues; sample evidence before choosing edit vs study."


def no_pattern_title(*, has_repeated_misses: bool = True) -> str:
    if not has_repeated_misses:
        return "Nothing to check yet"
    return "No clear next check yet"


def no_pattern_evidence(*, has_repeated_misses: bool = True) -> str:
    if not has_repeated_misses:
        return "No card crossed the repeated-miss threshold in this window."
    return "There are repeated misses, but not enough shared signal to point at a card edit or study target."


def no_pattern_next_step(*, has_repeated_misses: bool = True) -> str:
    if not has_repeated_misses:
        return "Keep reviewing. Bonsai will speak up when a stronger pattern appears."
    return "If one card feels suspicious, review evidence cards. Otherwise keep reviewing and wait for a clearer pattern."


def early_learning_evidence(count: int) -> str:
    label = "card is" if count == 1 else "cards are"
    return f"{count} early {label} new enough that misses may be first-pass learning, not mature lapses."


def early_learning_next_step() -> str:
    return "If these felt unfamiliar, review the source briefly. Do not edit these cards yet."


def early_learning_check_text() -> str:
    return "Treat this as weak evidence unless the same cards keep failing after a few more reps."


def short_label(label: str) -> str:
    return label if len(label) <= 64 else label[:61].rstrip() + "..."
