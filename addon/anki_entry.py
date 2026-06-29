from __future__ import annotations

import importlib
import sys
import threading
from datetime import datetime
from urllib.parse import unquote

try:
    from .analytics import AGAIN_EASE, HARD_EASE, filter_review_entries_by_lookback
    from .anki_browser import open_browser_search
    from .anki_gateway import load_review_entries
    from .config import load_config
    from .debrief import build_debrief
    from .demo_data import build_demo_review_entries
except ImportError:
    from analytics import AGAIN_EASE, HARD_EASE, filter_review_entries_by_lookback
    from anki_browser import open_browser_search
    from anki_gateway import load_review_entries
    from config import load_config
    from debrief import build_debrief
    from demo_data import build_demo_review_entries


DECK_SCOPE_MESSAGE_PREFIX = "ankilens:deck:"
LOOKBACK_SCOPE_MESSAGE_PREFIX = "ankilens:lookback:"
BROWSE_SEARCH_MESSAGE_PREFIX = "ankilens:browse:"
LOOKBACK_OPTIONS = (7, 30, 90)
_selected_deck_name: str | None = None
_selected_lookback_days: int | None = None
_llm_request_counter = 0


def register_toolbar() -> None:
    from aqt import gui_hooks

    gui_hooks.top_toolbar_did_init_links.append(_add_top_toolbar_link)
    gui_hooks.webview_did_receive_js_message.append(_handle_js_message)
    _add_tools_menu()


def _add_top_toolbar_link(links, toolbar) -> None:
    links.append(
        toolbar.create_link(
            "ankilens",
            "AnkiLens",
            show_ankilens_page,
            tip="Analyze missed cards",
            id="ankilens-top-tab",
        )
    )


def _add_tools_menu() -> None:
    from aqt import mw
    from aqt.qt import QAction, QMenu

    menu = QMenu("AnkiLens", mw)
    api_key_action = QAction("Set API key", mw)
    api_key_action.triggered.connect(open_api_key_dialog)
    menu.addAction(api_key_action)
    mw.form.menuTools.addMenu(menu)


def open_api_key_dialog() -> None:
    from aqt import mw
    from aqt.qt import QInputDialog, QLineEdit

    api_key, accepted = QInputDialog.getText(
        mw,
        "AnkiLens API key",
        "OpenRouter API key:",
        QLineEdit.EchoMode.Password,
        "",
    )
    if not accepted:
        return
    if not _save_api_key(api_key):
        _show_info("No API key was saved.")
        return
    _show_info("AnkiLens API key saved.")
    show_ankilens_page()


def _show_info(message: str) -> None:
    from aqt.utils import showInfo

    showInfo(message)


def _save_api_key(api_key: str) -> bool:
    cleaned = api_key.strip()
    if not cleaned:
        return False
    from aqt import mw

    raw_config = mw.addonManager.getConfig(__package__) or {}
    raw_config["llm_api_key"] = cleaned
    raw_config["llm_summary_enabled"] = True
    mw.addonManager.writeConfig(__package__, raw_config)
    return True


def _handle_js_message(handled, message: str, _context):
    if message.startswith(DECK_SCOPE_MESSAGE_PREFIX):
        _set_selected_deck(unquote(message.removeprefix(DECK_SCOPE_MESSAGE_PREFIX)))
        show_ankilens_page()
        return (True, None)
    if message.startswith(LOOKBACK_SCOPE_MESSAGE_PREFIX):
        _set_selected_lookback_days(message.removeprefix(LOOKBACK_SCOPE_MESSAGE_PREFIX))
        show_ankilens_page()
        return (True, None)
    if message.startswith(BROWSE_SEARCH_MESSAGE_PREFIX):
        _open_search_from_debrief(unquote(message.removeprefix(BROWSE_SEARCH_MESSAGE_PREFIX)))
        return (True, None)
    return handled


def show_ankilens_page() -> None:
    from aqt import mw

    current_build_debrief = _load_debrief_builder()
    page = _load_debrief_page_module()
    config = load_config(mw.addonManager.getConfig(__package__))
    api_key_configured = _api_key_configured(config)
    lookback_days = _valid_selected_lookback(config.debrief_lookback_days)
    now = datetime.now()
    entries = _debrief_entries(_load_review_entries(mw, config, now=now), lookback_days=lookback_days, now=now)
    deck_options = _deck_options(entries)
    selected_deck = _valid_selected_deck(deck_options)
    scoped_entries = _filter_entries_by_deck(entries, selected_deck)
    miss_eases = _miss_eases(config)
    debrief = current_build_debrief(
        scoped_entries,
        minimum_misses=config.minimum_misses,
        result_limit=config.result_limit,
        miss_eases=miss_eases,
    )
    mw.web.stdHtml(
        page.debrief_page_html(
            debrief,
            lookback_days=lookback_days,
            lookback_options=LOOKBACK_OPTIONS,
            deck_options=deck_options,
            selected_deck=selected_deck,
            deck_label=_deck_display_label(selected_deck) if selected_deck else None,
            llm_enabled=config.llm_summary_enabled,
            api_key_configured=api_key_configured,
        )
    )
    if api_key_configured:
        _attach_llm_summary_to_page(
            mw.web,
            scoped_entries,
            config,
            debrief.evidence,
            grounding=page.grounding_text(_deck_display_label(selected_deck) if selected_deck else None, lookback_days),
            miss_eases=miss_eases,
        )


def _load_debrief_builder():
    if __package__:
        for module_name in _debrief_model_module_names(__package__):
            module = sys.modules.get(module_name)
            if module:
                importlib.reload(module)
        module = importlib.import_module(f"{__package__}.debrief")
        return module.build_debrief
    return build_debrief


def _debrief_model_module_names(package: str) -> tuple[str, ...]:
    return (
        f"{package}.content_signals",
        f"{package}.analytics",
        f"{package}.debrief",
    )


def _load_llm_summary_builder():
    if __package__:
        module_name = f"{__package__}.llm_summary"
        module = sys.modules.get(module_name)
        if module:
            importlib.reload(module)
        module = importlib.import_module(module_name)
        return module.build_llm_summary
    from llm_summary import build_llm_summary as current_build_llm_summary

    return current_build_llm_summary


def _load_debrief_page_module():
    if __package__:
        module_name = f"{__package__}.debrief_page"
        module = sys.modules.get(module_name)
        if module:
            importlib.reload(module)
        return importlib.import_module(module_name)
    import debrief_page as current_debrief_page

    return current_debrief_page


def _attach_llm_summary_to_page(web, entries, config, evidence=None, *, grounding: str = "", miss_eases: tuple[int, ...] | None = None) -> None:
    page = _load_debrief_page_module()
    request_id = _next_llm_request_id()
    web._ankilens_llm_request_id = request_id

    def update_page(summary) -> None:
        if getattr(web, "_ankilens_llm_request_id", None) != request_id:
            return
        error_message = getattr(summary, "message", "")
        web.eval(
            page.llm_summary_status_update_js(error_message, evidence, grounding=grounding)
            if error_message
            else page.llm_summary_update_js(summary, evidence, grounding=grounding)
            if summary
            else page.llm_summary_status_update_js("No LLM insight returned for this deck/window.", evidence, grounding=grounding)
        )

    _start_llm_summary_worker(
        web,
        entries,
        config,
        update_page,
        miss_eases=miss_eases or _miss_eases(config),
    )


def _next_llm_request_id() -> int:
    global _llm_request_counter
    _llm_request_counter += 1
    return _llm_request_counter


def _start_llm_summary_worker(parent, entries, config, callback, *, miss_eases: tuple[int, ...] | None = None) -> None:
    if not config.llm_summary_enabled:
        return
    from aqt.qt import QObject, pyqtSignal

    class LlmSummaryNotifier(QObject):
        summary_ready = pyqtSignal(object)

    notifier = LlmSummaryNotifier(parent)
    notifier.summary_ready.connect(callback)

    def run() -> None:
        summary = _load_llm_summary_builder()(entries, config, miss_eases=miss_eases or _miss_eases(config))
        notifier.summary_ready.emit(summary)

    thread = threading.Thread(target=run, daemon=True)
    parent._ankilens_llm_notifier = notifier
    parent._ankilens_llm_thread = thread
    thread.start()


def _miss_eases(config) -> tuple[int, ...]:
    return (AGAIN_EASE, HARD_EASE) if getattr(config, "count_hard_as_miss", False) else (AGAIN_EASE,)


def _api_key_configured(config) -> bool:
    if getattr(config, "llm_api_key", ""):
        return True
    if not getattr(config, "llm_api_key_env", ""):
        return False
    import os

    if os.environ.get(config.llm_api_key_env):
        return True
    try:
        from .llm_summary import _env_file_value
    except ImportError:
        from llm_summary import _env_file_value

    return bool(_env_file_value(config.llm_api_key_env))


def _debrief_entries(entries, config=None, *, lookback_days: int | None = None, now: datetime):
    if lookback_days is None:
        lookback_days = config.debrief_lookback_days
    return filter_review_entries_by_lookback(
        entries,
        lookback_days=lookback_days,
        now=now,
    )


def _load_review_entries(mw, config, *, now: datetime):
    entries = load_review_entries(mw)
    if config.demo_data_enabled:
        return entries + build_demo_review_entries(now)
    return entries


def _deck_options(entries) -> tuple[str, ...]:
    return tuple(sorted({entry.deck_name for entry in entries if entry.deck_name}))


def _valid_selected_deck(deck_options: tuple[str, ...]) -> str | None:
    if _selected_deck_name in deck_options:
        return _selected_deck_name
    return deck_options[0] if deck_options else None


def _set_selected_deck(deck_name: str) -> None:
    global _selected_deck_name
    _selected_deck_name = deck_name


def _valid_selected_lookback(default_lookback_days: int) -> int:
    if _selected_lookback_days in LOOKBACK_OPTIONS:
        return _selected_lookback_days
    if default_lookback_days in LOOKBACK_OPTIONS:
        return default_lookback_days
    return 30


def _set_selected_lookback_days(raw_days: str) -> None:
    global _selected_lookback_days
    try:
        days = int(raw_days)
    except ValueError:
        return
    if days in LOOKBACK_OPTIONS:
        _selected_lookback_days = days


def _filter_entries_by_deck(entries, deck_name: str | None):
    if not deck_name:
        return entries
    return [entry for entry in entries if entry.deck_name == deck_name]


def _deck_display_label(deck_name: str | None) -> str | None:
    if not deck_name:
        return None
    parts = [part.strip() for part in deck_name.split("::") if part.strip()]
    if len(parts) > 3:
        return " / ".join((parts[0], *parts[-2:]))
    if len(parts) > 1:
        return " / ".join(parts)
    return deck_name


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
    exact_card_count = _exact_card_search_count(query)
    if opened and exact_card_count:
        if exact_card_count == 1:
            return "Opened card in Browse. Search copied."
        return f"Opened {exact_card_count} missed examples in Browse. Search copied."
    if opened:
        return "Opened in Browse. Search copied."
    if exact_card_count == 1:
        return (
            f"Copied search for this card:\n\n"
            f"{query}\n\nOpen Browse and paste it into the search field."
        )
    if exact_card_count and exact_card_count > 1:
        return (
            f"Copied search for {exact_card_count} missed examples:\n\n"
            f"{query}\n\nOpen Browse and paste it into the search field."
        )
    return f"Copied search for Anki Browse:\n\n{query}\n\nOpen Browse and paste it into the search field."


def _exact_card_search_count(query: str) -> int:
    parts = [part.strip() for part in query.split(" or ")]
    if not parts or not all(part.startswith("cid:") for part in parts):
        return 0
    return len(parts)
