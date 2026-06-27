from __future__ import annotations

from datetime import datetime

try:
    from .analytics import filter_review_entries_by_lookback, summarize_missed_cards
    from .anki_browser import open_browser_search
    from .anki_gateway import load_review_entries
    from .browser_search import browser_search_for_card, browser_search_for_study_target
    from .config import load_config
    from .deck_button import BUTTON_MESSAGE, DEBRIEF_MESSAGE, deck_button_html
    from .debrief import StudyTarget, build_debrief
except ImportError:
    from analytics import filter_review_entries_by_lookback, summarize_missed_cards
    from anki_browser import open_browser_search
    from anki_gateway import load_review_entries
    from browser_search import browser_search_for_card, browser_search_for_study_target
    from config import load_config
    from deck_button import BUTTON_MESSAGE, DEBRIEF_MESSAGE, deck_button_html
    from debrief import StudyTarget, build_debrief


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
    content.stats += deck_button_html(**_deck_browser_summary())


def _deck_browser_summary() -> dict[str, int | None]:
    from aqt import mw

    try:
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
    except Exception:
        return {"missed_cards": None, "lookback_days": None}
    return {"missed_cards": len(summaries), "lookback_days": config.lookback_days}


def _handle_js_message(handled, message: str, _context):
    if message == BUTTON_MESSAGE:
        show_missed_card_analytics()
        return (True, None)
    if message == DEBRIEF_MESSAGE:
        show_session_debrief()
        return (True, None)
    return handled


def show_session_debrief() -> None:
    from aqt import mw

    from .debrief_dialog import DebriefDialog

    config = load_config(mw.addonManager.getConfig(__package__))
    entries = _debrief_entries(load_review_entries(mw), config, now=datetime.now())
    dialog = DebriefDialog(
        build_debrief(entries, minimum_misses=config.minimum_misses, result_limit=config.result_limit),
        lookback_days=config.debrief_lookback_days,
        open_card=_open_card_from_debrief,
        open_material=_open_material_from_debrief,
        open_full_analytics=show_missed_card_analytics,
        parent=mw,
    )
    dialog.exec()


def _debrief_entries(entries, config, *, now: datetime):
    return filter_review_entries_by_lookback(
        entries,
        lookback_days=config.debrief_lookback_days,
        now=now,
    )


def _open_card_from_debrief(card_id: int) -> None:
    _copy_search_from_debrief(browser_search_for_card(card_id))


def _open_material_from_debrief(target: StudyTarget) -> None:
    query = browser_search_for_study_target(target.kind, target.label)
    _open_search_from_debrief(query)


def _open_search_from_debrief(query: str) -> None:
    from aqt.qt import QApplication
    from aqt.utils import showInfo, tooltip

    QApplication.clipboard().setText(query)
    opened = _try_open_browser_search(query)
    message = _browse_search_message(query, opened=opened)
    if opened:
        tooltip(message)
    else:
        showInfo(message)


def _try_open_browser_search(query: str) -> bool:
    try:
        from aqt import mw

        open_browser_search(mw, query)
    except Exception:
        return False
    return True


def _browse_search_message(query: str, *, opened: bool) -> str:
    if opened:
        return "Opened in Browse. Search copied."
    return f"Copied search for Anki Browse:\n\n{query}\n\nOpen Browse and paste it into the search field."


def _copy_search_from_debrief(query: str) -> None:
    _open_search_from_debrief(query)


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
