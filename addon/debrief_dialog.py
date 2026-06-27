from __future__ import annotations

from collections.abc import Callable

from aqt.qt import QDialog, QFrame, QHBoxLayout, QScrollArea, QVBoxLayout, Qt, QWidget

try:
    from .debrief import CardsToFix, Debrief, SessionHabits, StudyTarget
    from .debrief_dialog_copy import (
        card_search_button_text,
        debrief_title,
        debrief_intro_text,
        debrief_window_title,
        early_learning_evidence,
        early_learning_check_text,
        early_learning_next_step,
        early_learning_title,
        evidence_confidence_text,
        no_pattern_evidence,
        no_pattern_confidence_text,
        no_pattern_check_text,
        no_pattern_next_step,
        no_pattern_title,
        mixed_repair_signal_text,
        no_repair_signal_text,
        related_search_button_text,
        repair_evidence,
        repair_next_step,
        repair_title,
        short_label,
        scoped_early_learning_evidence,
        scoped_early_learning_title,
        target_display_label,
        target_evidence_text,
        study_target_title,
        study_next_step,
        supporting_cards_button_text,
    )
    from .dialog_actions import accept_then
    from .copy_text import same_note_context
    from .session_context import session_context_text
    from .ui_helpers import body_label, panel_card, primary_button, recommendation_card, secondary_button, title_label
except ImportError:
    from debrief import CardsToFix, Debrief, SessionHabits, StudyTarget
    from debrief_dialog_copy import (
        card_search_button_text,
        debrief_title,
        debrief_intro_text,
        debrief_window_title,
        early_learning_evidence,
        early_learning_check_text,
        early_learning_next_step,
        early_learning_title,
        evidence_confidence_text,
        no_pattern_evidence,
        no_pattern_confidence_text,
        no_pattern_check_text,
        no_pattern_next_step,
        no_pattern_title,
        mixed_repair_signal_text,
        no_repair_signal_text,
        related_search_button_text,
        repair_evidence,
        repair_next_step,
        repair_title,
        short_label,
        scoped_early_learning_evidence,
        scoped_early_learning_title,
        target_display_label,
        target_evidence_text,
        study_target_title,
        study_next_step,
        supporting_cards_button_text,
    )
    from dialog_actions import accept_then
    from copy_text import same_note_context
    from session_context import session_context_text
    from ui_helpers import body_label, panel_card, primary_button, recommendation_card, secondary_button, title_label


class DebriefDialog(QDialog):
    def __init__(
        self,
        debrief: Debrief,
        *,
        lookback_days: int,
        open_card: Callable[[int], None] | None = None,
        open_material: Callable[[StudyTarget], None] | None = None,
        open_full_analytics: Callable[[], None] | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(debrief_window_title())
        self.resize(640, 500)
        self.setStyleSheet("QDialog { background: #f5f2ea; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(26, 22, 26, 20)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(title_label(debrief_title()))
        layout.addWidget(body_label(debrief_intro_text(lookback_days)))

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 4, 0, 0)
        content_layout.setSpacing(12)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_layout.addWidget(_next_step_card(debrief, dialog=self, open_card=open_card, open_material=open_material))
        if debrief.cards_to_fix.cards:
            content_layout.addWidget(_cards_to_fix_card(debrief.cards_to_fix, dialog=self, open_card=open_card))
        if (debrief.cards_to_fix.cards or debrief.study_next) and _early_learning_cards(debrief):
            content_layout.addWidget(_early_learning_card(debrief))
        if debrief.cards_to_fix.cards and debrief.study_next:
            content_layout.addWidget(_study_material_card(debrief.study_next, dialog=self, open_material=open_material))
        context = session_context_text(debrief.session_habits)
        if context:
            content_layout.addWidget(panel_card("Session note", context, quiet=True))
        content.setLayout(content_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        if open_full_analytics:
            button = secondary_button(supporting_cards_button_text())
            button.clicked.connect(lambda _checked=False: accept_then(self, open_full_analytics))
            actions = QHBoxLayout()
            actions.setContentsMargins(0, 4, 0, 0)
            actions.addStretch(1)
            actions.addWidget(button)
            layout.addLayout(actions)
        self.setLayout(layout)


def _next_step_card(
    debrief: Debrief,
    *,
    dialog: QDialog,
    open_card: Callable[[int], None] | None,
    open_material: Callable[[StudyTarget], None] | None,
):
    if getattr(debrief, "repair_is_top_check", bool(debrief.cards_to_fix.cards)):
        card = debrief.cards_to_fix.cards[0]
        actions = ()
        if open_card:
            button = primary_button(card_search_button_text())
            button.clicked.connect(lambda _checked=False: accept_then(dialog, lambda: open_card(card.card_id)))
            actions = (button,)
        return recommendation_card(
            repair_title(short_label(card.card_label)),
            confidence=evidence_confidence_text(card.misses, card.total_reviews),
            evidence=_repair_evidence_with_note_context(card),
            next_step=repair_next_step(),
            check="Inspect first; edit only if the prompt is unclear after opening it.",
            actions=actions,
        )
    if _early_learning_cards(debrief) and getattr(debrief, "early_learning_is_dominant", False):
        target = debrief.study_next[0] if debrief.study_next else None
        actions = ()
        if open_material and target:
            button = secondary_button(related_search_button_text())
            button.clicked.connect(lambda _checked=False: accept_then(dialog, lambda: open_material(target)))
            actions = (button,)
        return recommendation_card(
            scoped_early_learning_title(_target_label(target)) if target else early_learning_title(),
            confidence=evidence_confidence_text(_early_learning_count(debrief), 0, early_learning=True),
            evidence=(
                scoped_early_learning_evidence(_early_learning_count(debrief), _target_label(target))
                if target
                else early_learning_evidence(_early_learning_count(debrief))
            ),
            next_step=early_learning_next_step(),
            check=early_learning_check_text(),
            actions=actions,
        )
    if debrief.study_next:
        target = debrief.study_next[0]
        actions = ()
        if open_material:
            button = secondary_button(related_search_button_text())
            button.clicked.connect(lambda _checked=False: accept_then(dialog, lambda: open_material(target)))
            actions = (button,)
        return recommendation_card(
            study_target_title(_target_label(target)),
            confidence=evidence_confidence_text(
                target.count,
                target.reviewed_count,
                mixed_signals=bool(debrief.cards_to_fix.cards),
            ),
            evidence=_target_evidence(target, _target_label(target)),
            next_step=study_next_step(target.kind, mostly_early=target.mostly_early),
            check=_study_check_text(debrief),
            actions=actions,
        )
    has_repeated_misses = bool(debrief.missed_cards)
    return recommendation_card(
        no_pattern_title(has_repeated_misses=has_repeated_misses),
        confidence=no_pattern_confidence_text(has_repeated_misses=has_repeated_misses),
        evidence=no_pattern_evidence(has_repeated_misses=has_repeated_misses),
        next_step=no_pattern_next_step(has_repeated_misses=has_repeated_misses),
        check=no_pattern_check_text(has_repeated_misses=has_repeated_misses),
    )


def _cards_to_fix_card(cards_to_fix: CardsToFix, *, dialog: QDialog, open_card: Callable[[int], None] | None):
    if not cards_to_fix.cards:
        body = "No repeated card-surface pattern stood out in this window. Study evidence may be more useful here."
        return panel_card(
            "No card repair stands out",
            body,
        )
    card = cards_to_fix.cards[0]
    actions = ()
    if open_card:
        button = secondary_button(card_search_button_text())
        button.clicked.connect(lambda _checked=False: accept_then(dialog, lambda: open_card(card.card_id)))
        actions = (button,)
    rows = tuple(
        (
            "Start here" if index == 0 else "Also check",
            f"{summary.card_label}: {_repair_clues(summary)}; needed another pass on {summary.misses}/{summary.total_reviews} reviews",
        )
        for index, summary in enumerate(cards_to_fix.cards[:3])
    )
    return panel_card(
        "Card-format evidence",
        _cards_to_fix_body(cards_to_fix),
        rows=rows,
        actions=actions,
    )


def _repair_evidence_with_note_context(card) -> str:
    note_context = same_note_context(card)
    if not note_context:
        return repair_evidence(card)
    return f"{repair_evidence(card)} {note_context}"


def _repair_clues(summary) -> str:
    return ", ".join(summary.content_labels) if summary.content_labels else "repeated misses"


def _study_material_card(
    targets: tuple[StudyTarget, ...],
    *,
    dialog: QDialog,
    open_material: Callable[[StudyTarget], None] | None,
):
    if not targets:
        return panel_card(
            "No study pattern yet",
            "No repeated material pattern in this window.",
            quiet=True,
        )
    top_target = targets[0]
    rows = (
        ("Sample", _target_label(top_target)),
        ("Why", _target_summary(top_target)),
    ) + tuple(("Also sample", _target_summary(target)) for target in targets[1:3])
    actions = ()
    if open_material:
        button = secondary_button(related_search_button_text())
        button.clicked.connect(lambda _checked=False: accept_then(dialog, lambda: open_material(top_target)))
        actions = (button,)
    return panel_card(
        "Material evidence to sample",
        rows=rows,
        actions=actions,
    )


def _early_learning_card(debrief: Debrief):
    rows = tuple(
        (
            "Early card" if index == 0 else "Also",
            f"{summary.card_label}: needed another pass on {summary.misses}/{summary.total_reviews} reviews",
        )
        for index, summary in enumerate(_early_learning_cards(debrief)[:3])
    )
    return panel_card("Early learning", _early_learning_body(debrief), rows=rows)


def _target_summary(target: StudyTarget) -> str:
    return _target_evidence(target, _target_kind_label(target.kind))


def _early_learning_body(debrief: Debrief) -> str:
    count = _early_learning_count(debrief)
    return (
        f"{count} early card{_plural(count)} "
        f"{_verb(count, 'is', 'are')} still early in learning. Treat this as normal first-pass learning, "
        "not a card-edit signal; study extra only if these felt unfamiliar or clustered."
    )


def _early_learning_cards(debrief: Debrief) -> tuple:
    early_learning = getattr(debrief, "early_learning", None)
    return tuple(getattr(early_learning, "cards", ()) or ())


def _early_learning_count(debrief: Debrief) -> int:
    early_learning = getattr(debrief, "early_learning", None)
    return getattr(early_learning, "count", len(_early_learning_cards(debrief)))


def _target_evidence(target: StudyTarget, label: str) -> str:
    return target_evidence_text(
        target.count,
        target.reviewed_count,
        label,
        target.related_cards,
        active_cards=target.kind == "tag",
        early_count=target.early_count,
        mature_count=target.mature_count,
        lapsed_count=target.lapsed_count,
    )


def _study_check_text(debrief: Debrief) -> str:
    if debrief.cards_to_fix.cards:
        return mixed_repair_signal_text()
    return no_repair_signal_text()


def _target_kind_label(kind: str) -> str:
    return {"tag": "tag", "term": "word", "deck": "deck"}.get(kind, "pattern")


def _target_label(target: StudyTarget) -> str:
    return target_display_label(target.label, target.kind)


def _plural(count: int) -> str:
    return "" if count == 1 else "s"


def _cards_to_fix_body(cards_to_fix: CardsToFix) -> str:
    return (
        f"{cards_to_fix.count} card{_plural(cards_to_fix.count)} "
        f"{_verb(cards_to_fix.count, 'has', 'have')} surface clues worth checking."
    )


def _verb(count: int, singular: str, plural: str) -> str:
    return singular if count == 1 else plural
