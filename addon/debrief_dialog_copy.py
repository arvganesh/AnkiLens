from __future__ import annotations


def study_target_title(label: str) -> str:
    return f"Suggested next check: review {label}"


def early_learning_title() -> str:
    return "Suggested next check: retry early material"


def card_search_button_text() -> str:
    return "Copy search for this card"


def related_search_button_text() -> str:
    return "Copy search for related cards"


def repair_action_summary(card) -> str:
    clues = ", ".join(card.content_labels) if card.content_labels else "repeated misses"
    return (
        f"Missed {card.misses}/{card.total_reviews} recent reviews; clues: {clues}. "
        "Inspect it first: simplify overloaded wording, or leave it and review the source if the card is clear."
    )


def short_label(label: str) -> str:
    return label if len(label) <= 64 else label[:61].rstrip() + "..."
