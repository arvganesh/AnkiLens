from __future__ import annotations

from collections.abc import Callable

from aqt.qt import QDialog, QHBoxLayout, QVBoxLayout, Qt

try:
    from .debrief import CardsToFix, Debrief, SessionHabits, StudyTarget
    from .dialog_actions import accept_then
    from .ui_helpers import body_label, panel_card, primary_button, secondary_button, title_label
except ImportError:
    from debrief import CardsToFix, Debrief, SessionHabits, StudyTarget
    from dialog_actions import accept_then
    from ui_helpers import body_label, panel_card, primary_button, secondary_button, title_label


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
        self.setWindowTitle("Bonsai Recent Misses Debrief")
        self.resize(620, 360)
        self.setStyleSheet("QDialog { background: #f5f2ea; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 20, 24, 18)
        layout.setSpacing(9)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(title_label("Recent Misses Debrief"))
        layout.addWidget(body_label(_intro_text(lookback_days)))
        layout.addSpacing(3)
        layout.addWidget(_next_step_card(debrief, dialog=self, open_card=open_card, open_material=open_material))
        if debrief.cards_to_fix.cards:
            layout.addWidget(_cards_to_fix_card(debrief.cards_to_fix, dialog=self, open_card=None))
        if debrief.cards_to_fix.cards and debrief.study_next:
            layout.addWidget(_study_material_card(debrief.study_next, dialog=self, open_material=open_material))
        layout.addWidget(_review_habits_card(debrief.session_habits))
        if open_full_analytics:
            button = secondary_button("Open full analytics")
            button.clicked.connect(lambda _checked=False: accept_then(self, open_full_analytics))
            actions = QHBoxLayout()
            actions.addStretch(1)
            actions.addWidget(button)
            layout.addLayout(actions)
        layout.addStretch(1)
        self.setLayout(layout)


def _intro_text(lookback_days: int) -> str:
    if lookback_days <= 0:
        return "Read-only patterns across available reviews. Bonsai does not change scheduling."
    return f"Last {lookback_days} days · read-only · Bonsai does not change scheduling."


def _next_step_card(
    debrief: Debrief,
    *,
    dialog: QDialog,
    open_card: Callable[[int], None] | None,
    open_material: Callable[[StudyTarget], None] | None,
):
    if debrief.cards_to_fix.cards:
        card = debrief.cards_to_fix.cards[0]
        actions = ()
        if open_card:
            button = primary_button("Inspect top card")
            button.clicked.connect(lambda _checked=False: _run_then_accept(dialog, lambda: open_card(card.card_id)))
            actions = (button,)
        return panel_card(
            "Best next step: inspect missed cards",
            f"{debrief.cards_to_fix.count} mature card{_plural(debrief.cards_to_fix.count)} "
            f"{_verb(debrief.cards_to_fix.count, 'keeps', 'keep')} missing with card-specific clues. "
            "Check whether the miss came from wording, context, or source knowledge before editing or leaving as-is.",
            actions=actions,
            featured=True,
        )
    if debrief.study_next:
        target = debrief.study_next[0]
        actions = ()
        if open_material:
            button = primary_button("Review related cards")
            button.clicked.connect(lambda _checked=False: _run_then_accept(dialog, lambda: open_material(target)))
            actions = (button,)
        return panel_card(
            f"Best next step: study {_target_label(target)}",
            _study_action_summary(target, debrief.cards_to_fix.early_exposure_count),
            actions=actions,
            featured=True,
        )
    return panel_card(
        "No strong pattern yet",
        "Bonsai found repeated misses, but not enough signal to recommend a card edit or study target.",
        featured=True,
    )


def _cards_to_fix_card(cards_to_fix: CardsToFix, *, dialog: QDialog, open_card: Callable[[int], None] | None):
    if not cards_to_fix.cards:
        body = "No strong card-specific pattern surfaced in this window. Study signals may be more useful here."
        if cards_to_fix.early_exposure_count:
            body += (
                f" {cards_to_fix.early_exposure_count} card{_plural(cards_to_fix.early_exposure_count)} "
                f"{_verb(cards_to_fix.early_exposure_count, 'looks', 'look')} early in learning."
            )
        return panel_card(
            "No card repair stands out",
            body,
            featured=True,
        )
    card = cards_to_fix.cards[0]
    actions = ()
    if open_card:
        button = primary_button("Find top card in Browse")
        button.clicked.connect(lambda _checked=False: _run_then_accept(dialog, lambda: open_card(card.card_id)))
        actions = (button,)
    rows = tuple(
        (
            "Top card" if index == 0 else "Also",
            f"{summary.card_label}: {', '.join(summary.content_labels)}; missed {summary.misses}/{summary.total_reviews} reviews",
        )
        for index, summary in enumerate(cards_to_fix.cards[:3])
    )
    return panel_card(
        "Why this recommendation",
        _cards_to_fix_body(cards_to_fix),
        rows=rows,
        actions=actions,
    )


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
    rows = tuple(("Also watch", _target_summary(target)) for target in targets[1:3])
    actions = ()
    if open_material:
        button = secondary_button("Browse related cards")
        button.clicked.connect(lambda _checked=False: _run_then_accept(dialog, lambda: open_material(top_target)))
        actions = (button,)
    return panel_card(
        f"Related study signal: {_target_label(top_target)}",
        _target_summary(top_target),
        rows=rows,
        actions=actions,
    )


def _review_habits_card(habits: SessionHabits):
    if habits.review_count == 0:
        return panel_card("Review habits", "No reviews found in this window.", quiet=True)
    parts = [
        f"{habits.review_count} reviews",
        f"{habits.again_rate:.0%} Again",
        habits.time_of_day.lower(),
    ]
    if habits.recorded_answer_seconds is not None and habits.seconds_per_timed_card is not None:
        parts.append(f"{habits.seconds_per_timed_card:.1f}s/card")
    return panel_card("Review habits", " · ".join(parts), quiet=True)


def _target_summary(target: StudyTarget) -> str:
    detail = _target_evidence(target, _target_kind_label(target.kind))
    if target.related_cards:
        detail += f" Examples: {', '.join(target.related_cards)}."
    return detail


def _study_action_summary(target: StudyTarget, early_exposure_count: int) -> str:
    detail = f"{_target_evidence(target, _target_label(target))} Skim the source topic, then retry related cards."
    if early_exposure_count:
        detail += (
            f" {early_exposure_count} card{_plural(early_exposure_count)} "
            f"{_verb(early_exposure_count, 'looks', 'look')} early in learning, so do not over-interpret "
            f"{_verb(early_exposure_count, 'it', 'them')} yet."
        )
    return detail


def _target_evidence(target: StudyTarget, label: str) -> str:
    return (
        f"{target.count} of {target.reviewed_count} reviewed card{_plural(target.reviewed_count)} "
        f"missed in {label}."
    )


def _target_kind_label(kind: str) -> str:
    return {"tag": "tag", "term": "word", "deck": "deck"}.get(kind, "pattern")


def _target_label(target: StudyTarget) -> str:
    if target.kind != "tag":
        return target.label
    return target.label.replace("::", " / ").replace("_", " ")


def _plural(count: int) -> str:
    return "" if count == 1 else "s"


def _cards_to_fix_body(cards_to_fix: CardsToFix) -> str:
    body = (
        f"{cards_to_fix.count} card{_plural(cards_to_fix.count)} "
        f"{_verb(cards_to_fix.count, 'shows', 'show')} stronger card-specific clues."
    )
    if cards_to_fix.early_exposure_count:
        body += (
            f" {cards_to_fix.early_exposure_count} card{_plural(cards_to_fix.early_exposure_count)} "
            f"{_verb(cards_to_fix.early_exposure_count, 'looks', 'look')} early in learning."
        )
    return body


def _verb(count: int, singular: str, plural: str) -> str:
    return singular if count == 1 else plural


def _run_then_accept(dialog: QDialog, callback: Callable[[], None]) -> None:
    callback()
    dialog.accept()
