from __future__ import annotations

import importlib
import sys
import types
import unittest


class _FakeWidget:
    labels: list[str] = []

    def __init__(self, text: str = "") -> None:
        self.text = text
        self.style = ""
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

    def setStyleSheet(self, style: str) -> None:
        self.style = style

    def setWordWrap(self, *_args) -> None:
        pass


class _FakeFrame(_FakeWidget):
    class Shape:
        StyledPanel = object()


class _FakeLayout:
    stretch_count = 0
    margins: list[tuple] = []
    spacings: list[int] = []
    action_rows: list[tuple] = []
    panel_action_orders: list[tuple[str, ...]] = []

    def __init__(self) -> None:
        self.items = []

    def addLayout(self, item, *args) -> None:
        self.items.append(("layout", item, args))
        if any(getattr(child[1], "text", "") == "Show related cards" for child in getattr(item, "items", ())):
            self.action_rows.append(tuple(self.items))
        action_order = tuple(
            child[0] if child[0] == "stretch" else getattr(child[1], "text", "")
            for child in getattr(item, "items", ())
            if child[0] == "stretch" or getattr(child[1], "text", "")
        )
        if "Show missed examples" in action_order:
            self.panel_action_orders.append(action_order)

    def addSpacing(self, *args) -> None:
        self.items.append(("spacing", args))

    def addStretch(self, *_args) -> None:
        _FakeLayout.stretch_count += 1
        self.items.append(("stretch", None, ()))

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
    _FakeLayout.action_rows = []
    _FakeLayout.panel_action_orders = []
    qt = types.ModuleType("aqt.qt")
    qt.QFrame = _FakeFrame
    qt.QHBoxLayout = _FakeLayout
    qt.QLabel = _FakeWidget
    qt.QPushButton = _FakeWidget
    qt.QSizePolicy = _FakeSizePolicy
    qt.QVBoxLayout = _FakeLayout
    qt.Qt = types.SimpleNamespace(AlignmentFlag=types.SimpleNamespace(AlignTop=object(), AlignLeft=object()))
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
            "Check related material: Cardiology Valves",
            confidence="Worth a quick check",
            evidence="2 of 5 related cards in Cardiology Valves needed another pass.",
            next_step="Open the related cards.",
            check="No obvious card-format issue stood out.",
            actions=(_FakeWidget("Show related cards"),),
        )

        self.assertIn("Check first", _FakeWidget.labels)
        self.assertNotIn("Next", _FakeWidget.labels)
        self.assertIn("What Bonsai saw", _FakeWidget.labels)
        self.assertIn("Before studying more", _FakeWidget.labels)
        self.assertIn(
            "Worth a quick check\n2 of 5 related cards in Cardiology Valves needed another pass.",
            _FakeWidget.labels,
        )
        self.assertIn("Open the related cards.", _FakeWidget.labels)
        self.assertLess(_FakeWidget.labels.index("Open the related cards."), _FakeWidget.labels.index("What Bonsai saw"))
        self.assertLess(_FakeWidget.labels.index("Show related cards"), _FakeWidget.labels.index("What Bonsai saw"))
        self.assertEqual(len(_FakeLayout.action_rows), 1)
        self.assertEqual(_FakeLayout.stretch_count, 1)

    def test_detail_blocks_have_breathing_room(self) -> None:
        _install_fake_aqt()
        ui_helpers = importlib.import_module("ui_helpers")

        ui_helpers.recommendation_card(
            "Check related material: Cardiology Valves",
            confidence="Worth a quick check",
            evidence="2 of 5 related cards in Cardiology Valves needed another pass.",
            next_step="Open the related cards.",
            check="No obvious card-format issue stood out.",
        )

        self.assertIn((0, 4, 0, 4), _FakeLayout.margins)
        self.assertIn((20, 16, 20, 18), _FakeLayout.margins)
        self.assertIn(4, _FakeLayout.spacings)
        self.assertNotIn(5, _FakeLayout.spacings)
        self.assertNotIn(14, _FakeLayout.spacings)

    def test_recommendation_card_uses_subtle_container_treatment(self) -> None:
        _install_fake_aqt()
        ui_helpers = importlib.import_module("ui_helpers")

        card = ui_helpers.recommendation_card(
            "Check related material: Cardiology Valves",
            confidence="Worth a quick check",
            evidence="2 of 5 related cards in Cardiology Valves needed another pass.",
            next_step="Open the related cards.",
            check="No obvious card-format issue stood out.",
        )

        self.assertIn("background: #fbfdf7", card.style)
        self.assertIn("border-radius: 12px", card.style)

    def test_why_text_breaks_dense_evidence_into_short_lines(self) -> None:
        _install_fake_aqt()
        ui_helpers = importlib.import_module("ui_helpers")

        text = ui_helpers._why_text(
            "Worth a quick check",
            "In this window, 2 of 5 cards needed another pass. Breakdown: 2 previously learned. Examples: Murmur?, AS murmur.",
        )

        self.assertEqual(
            text,
            (
                "Worth a quick check\n"
                "In this window, 2 of 5 cards needed another pass.\n"
                "Breakdown: 2 previously learned.\n"
                "Examples: Murmur?, AS murmur."
            ),
        )

    def test_quiet_panels_are_compact(self) -> None:
        _install_fake_aqt()
        ui_helpers = importlib.import_module("ui_helpers")

        ui_helpers.panel_card("Session note", "Keep reviewing normally.", quiet=True)

        self.assertIn((14, 10, 14, 10), _FakeLayout.margins)
        self.assertIn(4, _FakeLayout.spacings)
        self.assertNotIn(8, _FakeLayout.spacings)

    def test_panel_actions_stay_close_to_guidance(self) -> None:
        _install_fake_aqt()
        ui_helpers = importlib.import_module("ui_helpers")

        ui_helpers.panel_card(
            "Also check related material",
            rows=(("Also check", "Cardiology Valves"),),
            actions=(_FakeWidget("Show missed examples"),),
            quiet=True,
        )

        self.assertEqual(_FakeLayout.panel_action_orders, [("Show missed examples", "stretch")])

    def test_tertiary_button_is_low_emphasis(self) -> None:
        _install_fake_aqt()
        ui_helpers = importlib.import_module("ui_helpers")

        button = ui_helpers.tertiary_button("View details")

        self.assertEqual(button.text, "View details")
        self.assertIn("background: transparent", button.style)
        self.assertIn("border: none", button.style)
        self.assertIn("text-decoration: underline", button.style)


if __name__ == "__main__":
    unittest.main()
