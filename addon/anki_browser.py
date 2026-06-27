from __future__ import annotations

try:
    from .browser_search import browser_search_for_card
except ImportError:
    from browser_search import browser_search_for_card


def open_browser_search(mw, query: str, *, dialog_open=None):
    if dialog_open is None:
        from aqt import dialogs

        dialog_open = dialogs.open
    browser = dialog_open("Browser", mw)
    browser.search_for(query)
    browser.raise_()
    browser.activateWindow()
    return browser


def open_card_in_browser(mw, card_id: int):
    return open_browser_search(mw, browser_search_for_card(card_id))
