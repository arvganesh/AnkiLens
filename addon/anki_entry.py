from __future__ import annotations

from datetime import datetime

from .analytics import filter_review_entries_by_lookback, summarize_missed_cards
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
    entries = filter_review_entries_by_lookback(
        load_review_entries(mw),
        lookback_days=config.lookback_days,
        now=datetime.now(),
    )
    summaries = summarize_missed_cards(
        entries,
        minimum_misses=config.minimum_misses,
        limit=config.result_limit,
    )
    dialog = MissedCardsDialog(
        summaries,
        minimum_misses=config.minimum_misses,
        result_limit=config.result_limit,
        lookback_days=config.lookback_days,
        parent=mw,
    )
    dialog.exec()
