from __future__ import annotations

from typing import Any


def open_card_in_browser(mw: Any, card_id: int, dialogs: Any | None = None) -> Any:
    if dialogs is None:
        from aqt import dialogs

    card = mw.col.get_card(card_id)
    return dialogs.open("Browser", mw, card=card)
