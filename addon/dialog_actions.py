from __future__ import annotations

from collections.abc import Callable
from typing import Protocol


class AcceptsDialog(Protocol):
    def accept(self) -> None: ...


def accept_then(
    dialog: AcceptsDialog,
    callback: Callable[[], None],
    *,
    schedule: Callable[[Callable[[], None]], None] | None = None,
) -> None:
    dialog.accept()
    (schedule or _schedule_after_dialog_close())(callback)


def _schedule_after_dialog_close() -> Callable[[Callable[[], None]], None]:
    try:
        from aqt.qt import QTimer
    except Exception:
        return lambda callback: callback()
    return lambda callback: QTimer.singleShot(0, callback)
