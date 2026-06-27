from __future__ import annotations

from aqt.qt import QDialog, QVBoxLayout

from .debrief import Debrief
from .debrief_copy import cards_to_fix_caption, review_habits_caption, study_next_caption
from .ui_helpers import body_label, section_label, title_label


class DebriefDialog(QDialog):
    def __init__(self, debrief: Debrief, *, lookback_days: int, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Bonsai Recent Debrief")
        self.resize(520, 420)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)
        layout.addWidget(title_label("Recent Debrief"))
        layout.addWidget(body_label(_intro_text(lookback_days)))
        layout.addWidget(section_label(study_next_caption(debrief.study_next)))
        layout.addWidget(section_label(cards_to_fix_caption(debrief.cards_to_fix)))
        layout.addWidget(section_label(review_habits_caption(debrief.session_habits)))
        self.setLayout(layout)


def _intro_text(lookback_days: int) -> str:
    if lookback_days <= 0:
        return "A read-only debrief across all available reviews. Bonsai does not change scheduling."
    return f"A read-only debrief for the last {lookback_days} days. Bonsai does not change scheduling."
