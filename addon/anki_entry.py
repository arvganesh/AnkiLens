from __future__ import annotations

from datetime import datetime

from .analytics import filter_review_entries_by_lookback, summarize_missed_cards
from .anki_gateway import load_review_entries
from .config import load_config
from .deck_button import BUTTON_MESSAGE, deck_button_html


def register_menu() -> None:
    from aqt import mw
    from aqt.qt import QAction

    action = QAction("Bonsai", mw)
    action.triggered.connect(show_missed_card_analytics)
    mw.form.menuTools.addAction(action)
    _register_deck_browser_button()


def _register_deck_browser_button() -> None:
    from aqt import gui_hooks

    gui_hooks.deck_browser_will_render_content.append(_add_deck_browser_button)
    gui_hooks.webview_did_receive_js_message.append(_handle_js_message)


def _add_deck_browser_button(_deck_browser, content) -> None:
    content.stats += deck_button_html()


def _handle_js_message(handled, message: str, _context):
    if message != BUTTON_MESSAGE:
        return handled
    show_missed_card_analytics()
    return (True, None)


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
