from __future__ import annotations


def debrief_window_title() -> str:
    return "Bonsai Missed Cards"


def debrief_title() -> str:
    return "Missed cards"


def debrief_intro_text(lookback_days: int) -> str:
    if lookback_days <= 0:
        return "Read-only patterns across available reviews. Bonsai does not change scheduling."
    if lookback_days == 1:
        return "Last 24 hours · read-only · Bonsai does not change scheduling."
    return f"Last {lookback_days} days · read-only · Bonsai does not change scheduling."


def deck_debrief_button_text() -> str:
    return "Analyze missed cards"


def study_target_title(
    label: str,
    *,
    kind: str = "",
    mostly_early: bool = False,
    early_count: int = 0,
    mature_count: int = 0,
    lapsed_count: int = 0,
) -> str:
    if kind == "tag" and mostly_early:
        return f"New material to keep reviewing: {label}"
    if kind == "tag" and lapsed_count > early_count + mature_count:
        return f"Worth checking: {label}"
    if kind == "tag" and mature_count >= 2 and mature_count >= early_count:
        return f"Revisit this material: {label}"
    return f"Check related material: {label}"


def target_display_label(label: str, kind: str) -> str:
    if kind != "tag":
        return label
    parts = label.replace("::", "_").split("_")
    readable = [part for part in parts if part and part.lower() != "anking"]
    return " ".join(readable) if readable else label.replace("_", " ")


def target_evidence_text(
    count: int,
    reviewed_count: int,
    label: str,
    related_cards: tuple[str, ...] = (),
    *,
    active_cards: bool = False,
    early_count: int = 0,
    mature_count: int = 0,
    lapsed_count: int = 0,
) -> str:
    card_label = "card" if reviewed_count == 1 else "cards"
    scope = "related " if active_cards else ""
    sample = "In this window, " if _is_small_sample(reviewed_count) else ""
    evidence = f"{sample}{count} of {reviewed_count} {scope}{card_label} in {label} needed another pass."
    maturity = _maturity_text(early_count, mature_count, lapsed_count)
    if maturity:
        evidence += f" {maturity}."
    if related_cards:
        evidence += f" Examples: {', '.join(related_cards)}."
    return evidence


def target_signal_text(
    count: int,
    reviewed_count: int,
    *,
    active_cards: bool = False,
    mixed_signals: bool = False,
) -> str:
    card_label = "card" if reviewed_count == 1 else "cards"
    scope = "related " if active_cards else ""
    confidence = evidence_confidence_text(count, reviewed_count, mixed_signals=mixed_signals)
    return f"{count} of {reviewed_count} {scope}{card_label} needed another pass; {confidence.lower()}."


def target_detail_text(
    related_cards: tuple[str, ...] = (),
    *,
    early_count: int = 0,
    mature_count: int = 0,
    lapsed_count: int = 0,
) -> str:
    details = []
    maturity = _maturity_text(early_count, mature_count, lapsed_count)
    if maturity:
        details.append(f"{maturity}.")
    if related_cards:
        details.append(f"Examples: {', '.join(related_cards)}.")
    return " ".join(details) if details else "Bonsai saw this pattern in the current review window."


def early_learning_title() -> str:
    return "Early cards need a light check"


def scoped_early_learning_title(label: str) -> str:
    return f"Early cards in {label} need a light check"


def card_search_button_text() -> str:
    return "Show card in Browse"


def repair_title(label: str) -> str:
    return f"Card to inspect: {label}"


def same_note_cluster_title(label: str) -> str:
    return f"One note to inspect: {label}"


def same_note_cluster_evidence(card) -> str:
    return (
        f"{card.note_repeated_miss_count} cards from the same note needed another pass. "
        "Treat this as one note to inspect, not proof the whole topic is weak."
    )


def same_note_cluster_next_step() -> str:
    return "Open one of those cards and inspect the note. Edit only if the prompts ask too much or overlap."


def same_note_cluster_check_text() -> str:
    return "If the prompts look clear, leave them alone and keep reviewing normally."


def related_search_button_text() -> str:
    return "Show related cards"


def missed_examples_button_text() -> str:
    return "Show missed examples"


def evidence_confidence_text(
    missed_count: int,
    reviewed_count: int,
    *,
    early_learning: bool = False,
    mixed_signals: bool = False,
) -> str:
    if early_learning:
        return "Early learning"
    if mixed_signals:
        return "Check both causes"
    if missed_count >= 4 and reviewed_count >= 10 and not mixed_signals:
        return "Consistent enough to check"
    return "Worth a quick check"


def supporting_cards_button_text() -> str:
    return "See supporting cards"


def repair_action_summary(card) -> str:
    clues = ", ".join(card.content_labels) if card.content_labels else "repeated misses"
    return (
        f"Needed another pass on {card.misses}/{card.total_reviews} recent reviews; surface clues: {clues}. "
        "Open it first and read the prompt. Edit only if it asks too much; if it is clear, leave it alone and study nearby material."
    )


def repair_evidence(card) -> str:
    clues = ", ".join(card.content_labels) if card.content_labels else "repeated misses"
    return f"Needed another pass on {card.misses}/{card.total_reviews} recent reviews; possible card issue: {clues}."


def repair_next_step() -> str:
    return "Open the card and read the prompt. Edit only if it asks too much; if it is clear, leave it alone."


def study_next_step(
    kind: str,
    *,
    mostly_early: bool = False,
    early_count: int = 0,
    mature_count: int = 0,
    lapsed_count: int = 0,
) -> str:
    if mostly_early:
        return (
            "Treat this as newly encountered material first. Keep reviewing, and only study extra if these examples "
            "still feel unfamiliar after the session."
        )
    if lapsed_count > early_count + mature_count:
        return (
            "Open related cards first. If the prompts look clear, this may just be old material that needs another pass."
        )
    if mature_count >= 2 and mature_count >= early_count:
        return (
            "Open related cards and read the prompts. If they are clear and still feel unfamiliar, "
            "revisit the surrounding concept."
        )
    if kind == "tag":
        return (
            "Open a few related cards first. If the prompts are clear and the examples still feel unfamiliar, "
            "revisit nearby material for this tag."
        )
    if kind == "term":
        return "Skim the examples with this repeated wording. If they still feel unfamiliar, review the material around that concept."
    if kind == "deck":
        return "Treat this as broad deck context: check related cards before deciding what, if anything, to study."
    return "Review the related cards, then decide whether the surrounding material needs another pass."


def no_repair_signal_text() -> str:
    return "No obvious card-format issue stood out, so check related cards before deciding to study more."


def mixed_repair_signal_text() -> str:
    return "One card may also need editing; check the card before choosing edit vs study."


def no_pattern_title(*, has_repeated_misses: bool = True) -> str:
    if not has_repeated_misses:
        return "No action needed yet"
    return "No clear action yet"


def no_pattern_evidence(*, has_repeated_misses: bool = True) -> str:
    if not has_repeated_misses:
        return "No card crossed the repeated-miss threshold in this window."
    return "There are repeated misses, but they do not yet point clearly to a card edit or broad study target."


def no_pattern_next_step(*, has_repeated_misses: bool = True) -> str:
    if not has_repeated_misses:
        return "Keep reviewing normally. Bonsai will speak up when a stronger pattern appears."
    return "Do not edit or cram from this alone. If one card felt wrong, view the details; otherwise keep reviewing."


def no_pattern_confidence_text(*, has_repeated_misses: bool = True) -> str:
    if not has_repeated_misses:
        return "No signal"
    return "Not enough signal"


def no_pattern_check_text(*, has_repeated_misses: bool = True) -> str:
    if not has_repeated_misses:
        return "No card needs attention from this window."
    return "Bonsai is intentionally staying quiet until the pattern points to a useful action."


def early_learning_evidence(count: int) -> str:
    label = "card is" if count == 1 else "cards are"
    return f"{count} early {label} new enough that misses may be first-pass learning, not mature lapses."


def scoped_early_learning_evidence(count: int, label: str) -> str:
    card_label = "card is" if count == 1 else "cards are"
    return f"{count} early {card_label} in {label}. Treat this as first-pass learning, not proof the whole topic is weak."


def early_learning_next_step() -> str:
    return "Keep reviewing normally. Study extra only if these felt unfamiliar or cluster around the same concept."


def early_learning_check_text() -> str:
    return "Treat this as normal early learning unless the same cards keep failing after a few more reps."


def short_label(label: str) -> str:
    return label if len(label) <= 64 else label[:61].rstrip() + "..."


def _maturity_text(early_count: int, mature_count: int, lapsed_count: int) -> str:
    parts = []
    if early_count:
        parts.append(f"{early_count} early/new")
    if mature_count:
        parts.append(f"{mature_count} mature")
    if lapsed_count:
        parts.append(f"{lapsed_count} previously learned")
    if not parts or parts == [f"{mature_count} mature"]:
        return ""
    return "Breakdown: " + ", ".join(parts)


def _is_small_sample(reviewed_count: int) -> bool:
    return 0 < reviewed_count < 10
