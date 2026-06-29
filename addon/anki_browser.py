from __future__ import annotations


def browser_search_for_cards(card_ids: tuple[int, ...]) -> str:
    return " or ".join(f"cid:{card_id}" for card_id in _unique_card_ids(card_ids))


def open_browser_search(mw, query: str, *, dialog_open=None):
    if dialog_open is None:
        from aqt import dialogs

        dialog_open = dialogs.open
    return dialog_open("Browser", mw, search=(query,))


def _unique_card_ids(card_ids: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(dict.fromkeys(card_id for card_id in card_ids if card_id))
