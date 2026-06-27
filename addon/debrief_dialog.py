from __future__ import annotations

from collections.abc import Callable

from aqt.qt import QDialog, QHBoxLayout, QVBoxLayout

try:
    from .debrief import CardsToFix, Debrief, SessionHabits, StudyTarget
    from .dialog_actions import accept_then
    from .ui_helpers import body_label, panel_card, primary_button, title_label
except ImportError:
    from debrief import CardsToFix, Debrief, SessionHabits, StudyTarget
    from dialog_actions import accept_then
    from ui_helpers import body_label, panel_card, primary_button, title_label


class DebriefDialog(QDialog):
    def __init__(
        self,
        debrief: Debrief,
        *,
        lookback_days: int,
        open_full_analytics: Callable[[], None] | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Bonsai Recent Debrief")
        self.resize(620, 460)
        self.setStyleSheet("QDialog { background: #f5f2ea; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(12)
        layout.addWidget(title_label("Recent Debrief"))
        layout.addWidget(body_label(_intro_text(lookback_days)))
        layout.addWidget(_cards_to_fix_card(debrief.cards_to_fix))
        layout.addWidget(_study_material_card(debrief.study_next))
        layout.addWidget(_review_habits_card(debrief.session_habits))
        if open_full_analytics:
            button = primary_button("Open full analytics")
            button.clicked.connect(lambda _checked=False: accept_then(self, open_full_analytics))
            actions = QHBoxLayout()
            actions.addStretch(1)
            actions.addWidget(button)
            layout.addLayout(actions)
        self.setLayout(layout)


def _intro_text(lookback_days: int) -> str:
    if lookback_days <= 0:
        return "A read-only debrief across all available reviews. Bonsai does not change scheduling."
    return f"A read-only debrief for the last {lookback_days} days. Bonsai does not change scheduling."


def _cards_to_fix_card(cards_to_fix: CardsToFix):
    if not cards_to_fix.cards:
        return panel_card(
            "No card repair stands out",
            "If this material is new, review the source material before doing more cards.",
            featured=True,
        )
    card = cards_to_fix.cards[0]
    rows = (
        ("Card", card.card_label),
        ("Why", f"{', '.join(card.content_labels)}; missed {card.misses}/{card.total_reviews} reviews"),
        ("Next", "Open the card and check whether the prompt is specific enough."),
    )
    return panel_card(
        "Open this card first",
        f"{cards_to_fix.count} card{_plural(cards_to_fix.count)} may be worth checking before studying more.",
        rows=rows,
        featured=True,
    )


def _study_material_card(targets: tuple[StudyTarget, ...]):
    if not targets:
        return panel_card(
            "If the card looks clear, review this material",
            "No repeated material pattern in this window.",
            quiet=True,
        )
    rows = tuple((_target_label(target), _target_detail(target)) for target in targets[:3])
    return panel_card("If the card looks clear, review this material", rows=rows)


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


def _target_detail(target: StudyTarget) -> str:
    detail = f"{target.kind}, {target.count} card{_plural(target.count)}"
    if target.related_cards:
        detail += f"; examples: {', '.join(target.related_cards)}"
    return detail


def _target_label(target: StudyTarget) -> str:
    if target.kind != "tag":
        return target.label
    return target.label.replace("::", " / ").replace("_", " ")


def _plural(count: int) -> str:
    return "" if count == 1 else "s"
