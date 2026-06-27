from __future__ import annotations

from collections.abc import Callable
from typing import Protocol


class AcceptsDialog(Protocol):
    def accept(self) -> None: ...


def accept_then(dialog: AcceptsDialog, callback: Callable[[], None]) -> None:
    dialog.accept()
    callback()
