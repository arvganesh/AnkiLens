from __future__ import annotations


def study_target_title(label: str) -> str:
    return f"Best next step: review {label}"


def repair_action_summary(card) -> str:
    clues = ", ".join(card.content_labels) if card.content_labels else "repeated misses"
    return (
        f"Missed {card.misses}/{card.total_reviews} recent reviews; clues: {clues}. "
        "Inspect it first: simplify overloaded wording, or leave it and review the source if the card is clear."
    )


def short_label(label: str) -> str:
    return label if len(label) <= 64 else label[:61].rstrip() + "..."
