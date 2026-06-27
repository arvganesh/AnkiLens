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
    margins: list[tuple] = []
    spacings: list[int] = []

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

    def setContentsMargins(self, *args) -> None:
        self.margins.append(args)

    def setSpacing(self, *args) -> None:
        self.spacings.extend(args)


class _FakeSizePolicy:
    class Policy:
        Preferred = object()
        Fixed = object()


def _install_fake_aqt() -> None:
    _FakeWidget.labels = []
    _FakeLayout.stretch_count = 0
    _FakeLayout.margins = []
    _FakeLayout.spacings = []
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
    def test_recommendation_card_leads_with_next_action(self) -> None:
        _install_fake_aqt()
        ui_helpers = importlib.import_module("ui_helpers")

        ui_helpers.recommendation_card(
            "Material evidence to sample: Cardiology Valves",
            confidence="Limited evidence",
            evidence="2 of 5 active cards reviewed in Cardiology Valves needed another pass.",
            next_step="Open the related cards.",
            check="No obvious card-format issue stood out.",
            actions=(_FakeWidget("Find related cards in Browse"),),
        )

        self.assertIn("Recommended next check", _FakeWidget.labels)
        self.assertIn("Next", _FakeWidget.labels)
        self.assertIn("Why", _FakeWidget.labels)
        self.assertIn("Double-check", _FakeWidget.labels)
        self.assertIn(
            "Limited evidence: 2 of 5 active cards reviewed in Cardiology Valves needed another pass.",
            _FakeWidget.labels,
        )
        self.assertIn("Open the related cards.", _FakeWidget.labels)
        self.assertLess(_FakeWidget.labels.index("Next"), _FakeWidget.labels.index("Why"))
        self.assertLess(_FakeWidget.labels.index("Find related cards in Browse"), _FakeWidget.labels.index("Why"))
        self.assertEqual(_FakeLayout.stretch_count, 0)

    def test_detail_blocks_have_breathing_room(self) -> None:
        _install_fake_aqt()
        ui_helpers = importlib.import_module("ui_helpers")

        ui_helpers.recommendation_card(
            "Material evidence to sample: Cardiology Valves",
            confidence="Limited evidence",
            evidence="2 of 5 active cards reviewed in Cardiology Valves needed another pass.",
            next_step="Open the related cards.",
            check="No obvious card-format issue stood out.",
        )

        self.assertIn((0, 3, 0, 3), _FakeLayout.margins)
        self.assertIn(4, _FakeLayout.spacings)
        self.assertIn(5, _FakeLayout.spacings)
        self.assertNotIn(14, _FakeLayout.spacings)


if __name__ == "__main__":
    unittest.main()
