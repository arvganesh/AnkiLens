from __future__ import annotations

import importlib
import sys
import types
import unittest


class _FakeWidget:
    labels: list[str] = []

    def __init__(self, text: str = "") -> None:
        self.text = text
        if text:
            self.labels.append(text)

    def setAlignment(self, *_args) -> None:
        pass

    def setFixedWidth(self, *_args) -> None:
        pass

    def setFrameShape(self, *_args) -> None:
        pass

    def setLayout(self, layout) -> None:
        self.layout = layout

    def setSizePolicy(self, *_args) -> None:
        pass

    def setStyleSheet(self, *_args) -> None:
        pass

    def setWordWrap(self, *_args) -> None:
        pass


class _FakeFrame(_FakeWidget):
    class Shape:
        StyledPanel = object()


class _FakeLayout:
    stretch_count = 0

    def __init__(self) -> None:
        self.items = []

    def addLayout(self, item, *args) -> None:
        self.items.append(("layout", item, args))

    def addSpacing(self, *args) -> None:
        self.items.append(("spacing", args))

    def addStretch(self, *_args) -> None:
        _FakeLayout.stretch_count += 1

    def addWidget(self, item, *args) -> None:
        self.items.append(("widget", item, args))

    def setContentsMargins(self, *_args) -> None:
        pass

    def setSpacing(self, *_args) -> None:
        pass


class _FakeSizePolicy:
    class Policy:
        Preferred = object()
        Fixed = object()


def _install_fake_aqt() -> None:
    _FakeWidget.labels = []
    _FakeLayout.stretch_count = 0
    qt = types.ModuleType("aqt.qt")
    qt.QFrame = _FakeFrame
    qt.QHBoxLayout = _FakeLayout
    qt.QLabel = _FakeWidget
    qt.QPushButton = _FakeWidget
    qt.QSizePolicy = _FakeSizePolicy
    qt.QVBoxLayout = _FakeLayout
    qt.Qt = types.SimpleNamespace(AlignmentFlag=types.SimpleNamespace(AlignTop=object()))
    aqt = types.ModuleType("aqt")
    aqt.qt = qt
    sys.modules["aqt"] = aqt
    sys.modules["aqt.qt"] = qt
    sys.modules.pop("ui_helpers", None)


class UiHelpersTest(unittest.TestCase):
    def test_recommendation_card_separates_evidence_next_and_check(self) -> None:
        _install_fake_aqt()
        ui_helpers = importlib.import_module("ui_helpers")

        ui_helpers.recommendation_card(
            "Possible study target: Cardiology Valves",
            confidence="Limited evidence",
            evidence="2 of 5 active cards reviewed in Cardiology Valves needed another pass.",
            next_step="Open the related cards.",
            check="No obvious card-format issue stood out.",
            actions=(_FakeWidget("Find related cards in Browse"),),
        )

        self.assertIn("Evidence", _FakeWidget.labels)
        self.assertIn("Next", _FakeWidget.labels)
        self.assertIn("Check", _FakeWidget.labels)
        self.assertIn("Open the related cards.", _FakeWidget.labels)
        self.assertEqual(_FakeLayout.stretch_count, 0)


if __name__ == "__main__":
    unittest.main()
