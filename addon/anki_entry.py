from __future__ import annotations

from .analytics import summarize_missed_cards
from .anki_gateway import load_review_entries


def register_menu() -> None:
    from aqt import mw
    from aqt.qt import QAction

    action = QAction("Missed Card Analytics", mw)
    action.triggered.connect(show_missed_card_analytics)
    mw.form.menuTools.addAction(action)


def show_missed_card_analytics() -> None:
    from aqt import mw

    from .dialog import MissedCardsDialog

    entries = load_review_entries(mw)
    summaries = summarize_missed_cards(entries)
    dialog = MissedCardsDialog(summaries, mw)
    dialog.exec()
