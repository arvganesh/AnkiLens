from __future__ import annotations

import importlib
import sys
import types
import unittest
from datetime import datetime

from analytics import MissedCardSummary
from debrief import CardsToFix, Debrief, EarlyLearning, SessionHabits, StudyTarget


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


class _FakeSignal:
    def connect(self, callback) -> None:
        self.callback = callback


class _FakeButton:
    def __init__(self, text: str) -> None:
        self.text = text
        self.clicked = _FakeSignal()


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
        self.assertEqual(calls[0][0][0], "Card-format evidence")
        self.assertIn("1 card has surface clues worth checking", calls[0][0][1])
        self.assertEqual(calls[0][1]["rows"][0][0], "Start here")
        self.assertIn("Aortic stenosis: Long card; needed another pass on 3/4 reviews", calls[0][1]["rows"][0][1])

    def test_cards_to_fix_support_action_is_secondary(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        original_panel_card = debrief_dialog.panel_card
        original_secondary_button = debrief_dialog.secondary_button
        panel_calls = []
        button_calls = []
        debrief_dialog.panel_card = lambda *args, **kwargs: panel_calls.append((args, kwargs)) or "panel"
        debrief_dialog.secondary_button = lambda text: button_calls.append(text) or _FakeButton(text)
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
                open_card=lambda _card_id: None,
            )
        finally:
            debrief_dialog.panel_card = original_panel_card
            debrief_dialog.secondary_button = original_secondary_button

        self.assertEqual(widget, "panel")
        self.assertEqual(button_calls, ["Open card in Browse"])
        self.assertIsInstance(panel_calls[0][1]["actions"][0], _FakeButton)

    def test_early_learning_support_panel_uses_material_language(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        original_panel_card = debrief_dialog.panel_card
        calls = []
        debrief_dialog.panel_card = lambda *args, **kwargs: calls.append((args, kwargs)) or "panel"
        try:
            widget = debrief_dialog._early_learning_card(
                Debrief(
                    study_next=(),
                    cards_to_fix=CardsToFix(0, (), ()),
                    early_learning=EarlyLearning(
                        1,
                        (
                            MissedCardSummary(
                                1,
                                "Cardiology",
                                "Aortic stenosis",
                                1,
                                1,
                                datetime(2026, 6, 26),
                            ),
                        ),
                    ),
                    session_habits=SessionHabits(1, 1, 1.0, "Morning"),
                    missed_cards=(),
                )
            )
        finally:
            debrief_dialog.panel_card = original_panel_card

        self.assertEqual(widget, "panel")
        self.assertEqual(calls[0][0][0], "Early learning")
        self.assertIn("normal first-pass learning", calls[0][0][1])
        self.assertIn("not a card-edit signal", calls[0][0][1])
        self.assertIn("study extra only if these felt unfamiliar or clustered", calls[0][0][1])
        self.assertNotIn("source", calls[0][0][1].lower())
        self.assertNotIn("weak evidence", calls[0][0][1].lower())

    def test_no_pattern_recommendation_uses_quiet_confidence(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        original_recommendation_card = debrief_dialog.recommendation_card
        calls = []
        debrief_dialog.recommendation_card = lambda *args, **kwargs: calls.append((args, kwargs)) or "recommendation"
        try:
            widget = debrief_dialog._next_step_card(
                Debrief(
                    study_next=(),
                    cards_to_fix=CardsToFix(0, (), ()),
                    early_learning=EarlyLearning(0, ()),
                    session_habits=SessionHabits(1, 0, 0.0, "Morning"),
                    missed_cards=(
                        MissedCardSummary(
                            1,
                            "Cardiology",
                            "Aortic stenosis",
                            2,
                            5,
                            datetime(2026, 6, 26),
                        ),
                    ),
                ),
                dialog=None,
                open_card=None,
                open_material=None,
            )
        finally:
            debrief_dialog.recommendation_card = original_recommendation_card

        self.assertEqual(widget, "recommendation")
        self.assertEqual(calls[0][1]["confidence"], "Not enough signal")
        self.assertIn("intentionally staying quiet", calls[0][1]["check"])
        self.assertNotIn("Weak evidence", calls[0][1]["confidence"])

    def test_same_note_cluster_becomes_inspection_recommendation(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        original_recommendation_card = debrief_dialog.recommendation_card
        original_secondary_button = debrief_dialog.secondary_button
        calls = []
        button_calls = []
        debrief_dialog.recommendation_card = lambda *args, **kwargs: calls.append((args, kwargs)) or "recommendation"
        debrief_dialog.secondary_button = lambda text: button_calls.append(text) or _FakeButton(text)
        try:
            widget = debrief_dialog._next_step_card(
                Debrief(
                    study_next=(),
                    cards_to_fix=CardsToFix(0, (), ()),
                    early_learning=EarlyLearning(0, ()),
                    session_habits=SessionHabits(4, 2, 0.5, "Morning"),
                    missed_cards=(
                        MissedCardSummary(
                            1,
                            "AnKing",
                            "Aortic stenosis cloze",
                            2,
                            3,
                            datetime(2026, 6, 26),
                            note_id=50,
                            note_card_count=4,
                            note_repeated_miss_count=2,
                            card_reps=8,
                        ),
                    ),
                ),
                dialog=None,
                open_card=lambda _card_id: None,
                open_material=None,
            )
        finally:
            debrief_dialog.recommendation_card = original_recommendation_card
            debrief_dialog.secondary_button = original_secondary_button

        self.assertEqual(widget, "recommendation")
        self.assertEqual(calls[0][0][0], "One note to inspect: Aortic stenosis cloze")
        self.assertEqual(calls[0][1]["confidence"], "Same note repeated")
        self.assertIn("not proof the whole topic is weak", calls[0][1]["evidence"])
        self.assertEqual(button_calls, ["Open card in Browse"])

    def test_dominant_early_learning_recommendation_names_scope(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        original_recommendation_card = debrief_dialog.recommendation_card
        calls = []
        debrief_dialog.recommendation_card = lambda *args, **kwargs: calls.append((args, kwargs)) or "recommendation"
        try:
            widget = debrief_dialog._next_step_card(
                Debrief(
                    study_next=(StudyTarget("AnKing::Cardiology::Valves", "tag", 3, 5, ("Murmur?",)),),
                    cards_to_fix=CardsToFix(0, (), ()),
                    early_learning=EarlyLearning(
                        3,
                        (
                            MissedCardSummary(
                                1,
                                "AnKing",
                                "Murmur?",
                                1,
                                1,
                                datetime(2026, 6, 26),
                                is_early_exposure=True,
                                card_reps=1,
                            ),
                            MissedCardSummary(
                                2,
                                "AnKing",
                                "Aortic stenosis",
                                1,
                                1,
                                datetime(2026, 6, 26),
                                is_early_exposure=True,
                                card_reps=1,
                            ),
                            MissedCardSummary(
                                3,
                                "AnKing",
                                "Mitral regurgitation",
                                1,
                                1,
                                datetime(2026, 6, 26),
                                is_early_exposure=True,
                                card_reps=1,
                            ),
                        ),
                    ),
                    session_habits=SessionHabits(5, 3, 0.6, "Morning"),
                    missed_cards=(),
                ),
                dialog=None,
                open_card=None,
                open_material=None,
            )
        finally:
            debrief_dialog.recommendation_card = original_recommendation_card

        self.assertEqual(widget, "recommendation")
        self.assertEqual(calls[0][0][0], "Early cards in Cardiology Valves need a light check")
        self.assertIn("3 early cards are in Cardiology Valves", calls[0][1]["evidence"])
        self.assertIn("not proof the whole topic is weak", calls[0][1]["evidence"])

    def test_study_material_support_panel_is_action_oriented(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        original_panel_card = debrief_dialog.panel_card
        calls = []
        debrief_dialog.panel_card = lambda *args, **kwargs: calls.append((args, kwargs)) or "panel"
        try:
            widget = debrief_dialog._study_material_card(
                (
                    StudyTarget("AnKing::Cardiology::Valves", "tag", 2, 5, ("Murmur?",)),
                    StudyTarget("mitral", "term", 2, 6, ("Mitral regurgitation",)),
                ),
                dialog=None,
                open_material=None,
            )
        finally:
            debrief_dialog.panel_card = original_panel_card

        self.assertEqual(widget, "panel")
        self.assertEqual(calls[0][0][0], "Material evidence to sample")
        self.assertEqual(calls[0][1]["rows"][0][0], "Sample")
        self.assertEqual(calls[0][1]["rows"][1][0], "Why")
        self.assertEqual(calls[0][1]["rows"][2][0], "Also sample")
        self.assertNotIn("signal", calls[0][0][0].lower())


if __name__ == "__main__":
    unittest.main()
