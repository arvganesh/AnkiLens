from __future__ import annotations


def study_target_title(label: str) -> str:
    return f"Suggested next check: review {label}"


def early_learning_title() -> str:
    return "Suggested next check: retry early material"


def card_search_button_text() -> str:
    return "Copy search for this card"


def related_search_button_text() -> str:
    return "Copy search for related cards"


def supporting_cards_button_text() -> str:
    return "See supporting cards"


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
        return "Review this tagged topic, then retry the related cards."
    if kind == "term":
        return "Skim the related cards for the shared concept, then review the source if they still feel unclear."
    if kind == "deck":
        return "Treat this as a broad deck signal: sample the related cards before deciding what to study."
    return "Review the related cards, then decide whether the source material needs another pass."


def no_repair_signal_text() -> str:
    return "No strong card-construction clue stood out."


def early_learning_evidence(count: int) -> str:
    label = "card is" if count == 1 else "cards are"
    return f"{count} early {label} still in first-pass learning."


def early_learning_next_step() -> str:
    return "Treat this as normal learning first: quick source check, then retry."


def short_label(label: str) -> str:
    return label if len(label) <= 64 else label[:61].rstrip() + "..."
