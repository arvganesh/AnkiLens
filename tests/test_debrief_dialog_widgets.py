from __future__ import annotations

import importlib
import sys
import types
import unittest
from datetime import datetime

from analytics import MissedCardSummary
from debrief import CardsToFix


class _QtBase:
    pass


class _QFrame(_QtBase):
    class Shape:
        NoFrame = object()
        StyledPanel = object()


class _QSizePolicy:
    class Policy:
        Preferred = object()
        Fixed = object()


def _install_fake_aqt() -> None:
    qt = types.ModuleType("aqt.qt")
    qt.QDialog = _QtBase
    qt.QFrame = _QFrame
    qt.QHBoxLayout = _QtBase
    qt.QLabel = _QtBase
    qt.QPushButton = _QtBase
    qt.QScrollArea = _QtBase
    qt.QSizePolicy = _QSizePolicy
    qt.QVBoxLayout = _QtBase
    qt.QWidget = _QtBase
    qt.Qt = types.SimpleNamespace(AlignmentFlag=types.SimpleNamespace(AlignTop=object()))
    aqt = types.ModuleType("aqt")
    aqt.qt = qt
    sys.modules.setdefault("aqt", aqt)
    sys.modules.setdefault("aqt.qt", qt)


class DebriefDialogWidgetTest(unittest.TestCase):
    def test_cards_to_fix_card_returns_support_panel(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        original_panel_card = debrief_dialog.panel_card
        calls = []
        debrief_dialog.panel_card = lambda *args, **kwargs: calls.append((args, kwargs)) or "panel"
        try:
            widget = debrief_dialog._cards_to_fix_card(
                CardsToFix(
                    count=1,
                    clues=(("Long card", 1),),
                    cards=(
                        MissedCardSummary(
                            1,
                            "Cardiology",
                            "Aortic stenosis",
                            3,
                            4,
                            datetime(2026, 6, 26),
                            content_labels=("Long card",),
                        ),
                    ),
                ),
                dialog=None,
                open_card=None,
            )
        finally:
            debrief_dialog.panel_card = original_panel_card

        self.assertEqual(widget, "panel")
        self.assertEqual(calls[0][0][0], "Why this recommendation")
        self.assertIn("1 card shows stronger card-specific clues", calls[0][0][1])
        self.assertEqual(calls[0][1]["rows"][0][0], "Top card")
        self.assertIn("Aortic stenosis: Long card; missed 3/4 reviews", calls[0][1]["rows"][0][1])


if __name__ == "__main__":
    unittest.main()
