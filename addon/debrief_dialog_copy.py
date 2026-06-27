from __future__ import annotations


def debrief_window_title() -> str:
    return "Bonsai Next Check"


def debrief_title() -> str:
    return "Next Check"


def deck_debrief_button_text() -> str:
    return "Next Check"


def study_target_title(label: str) -> str:
    return f"Missed concept: {label}"


def target_display_label(label: str, kind: str) -> str:
    if kind != "tag":
        return label
    parts = label.replace("::", "_").split("_")
    readable = [part for part in parts if part and part.lower() != "anking"]
    return " ".join(readable) if readable else label.replace("_", " ")


def target_evidence_text(count: int, reviewed_count: int, label: str, related_cards: tuple[str, ...] = ()) -> str:
    card_label = "card" if reviewed_count == 1 else "cards"
    evidence = f"{count} of {reviewed_count} reviewed {card_label} missed in {label}."
    if related_cards:
        evidence += f" Examples: {', '.join(related_cards)}."
    return evidence


def early_learning_title() -> str:
    return "Likely normal first-pass learning"


def card_search_button_text() -> str:
    return "Open this card in Browse"


def repair_title(label: str) -> str:
    return f"Possible card issue: {label}"


def related_search_button_text() -> str:
    return "Open examples in Browse"


def supporting_cards_button_text() -> str:
    return "Review evidence cards"


def repair_action_summary(card) -> str:
    clues = ", ".join(card.content_labels) if card.content_labels else "repeated misses"
    return (
        f"Missed {card.misses}/{card.total_reviews} recent reviews; clues: {clues}. "
        "Inspect it first: simplify overloaded wording, or leave it and review the source if the card is clear."
    )


def repair_evidence(card) -> str:
    clues = ", ".join(card.content_labels) if card.content_labels else "repeated misses"
    return f"Missed {card.misses}/{card.total_reviews} recent reviews; clues: {clues}."


def repair_next_step() -> str:
    return "Inspect the prompt first. If it is clear, study the source instead of editing."


def study_next_step(kind: str) -> str:
    if kind == "tag":
        return "Do a short source refresh for this topic, then retry the related cards."
    if kind == "term":
        return "Skim the examples for the shared concept, then review the source if they still feel unclear."
    if kind == "deck":
        return "Treat this as a broad deck signal: sample the related cards before deciding what to study."
    return "Review the related cards, then decide whether the source material needs another pass."


def no_repair_signal_text() -> str:
    return "No strong card-construction clue stood out."


def mixed_repair_signal_text() -> str:
    return "One card also has construction clues; sample examples before deciding whether to edit or study."


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
    return f"{count} early {label} still in first-pass learning, not mature lapses."


def early_learning_next_step() -> str:
    return "Do a quick source refresh, then retry. Do not edit these cards yet."


def early_learning_check_text() -> str:
    return "Treat this as weak evidence unless the same cards keep failing after more reps."


def short_label(label: str) -> str:
    return label if len(label) <= 64 else label[:61].rstrip() + "..."
