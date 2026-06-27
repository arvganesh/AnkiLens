from __future__ import annotations

from .analytics import summarize_missed_cards
from .anki_gateway import load_review_entries
from .config import load_config


def register_menu() -> None:
    from aqt import mw
    from aqt.qt import QAction

    action = QAction("Bonsai", mw)
    action.triggered.connect(show_missed_card_analytics)
    mw.form.menuTools.addAction(action)


def show_missed_card_analytics() -> None:
    from aqt import mw

    from .dialog import MissedCardsDialog

    config = load_config(mw.addonManager.getConfig(__package__))
    entries = load_review_entries(mw)
    summaries = summarize_missed_cards(
        entries,
        minimum_misses=config.minimum_misses,
        limit=config.result_limit,
    )
    dialog = MissedCardsDialog(
        summaries,
        minimum_misses=config.minimum_misses,
        result_limit=config.result_limit,
        parent=mw,
    )
    dialog.exec()
