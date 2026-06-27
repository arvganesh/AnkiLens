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
    def test_debrief_does_not_surface_dense_details_path(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")

        self.assertFalse(hasattr(debrief_dialog, "supporting_cards_button_text"))

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
        self.assertEqual(calls[0][0][0], "Also check card format")
        self.assertIn("1 card may need a card-format check", calls[0][0][1])
        self.assertEqual(calls[0][1]["rows"][0][0], "Start here")
        self.assertIn("Aortic stenosis: Long card; needed another pass on 3/4 reviews", calls[0][1]["rows"][0][1])
        self.assertTrue(calls[0][1]["quiet"])

    def test_cards_to_fix_support_panel_can_open_top_card(self) -> None:
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
        self.assertEqual(button_calls, ["Show card in Browse"])
        self.assertEqual(panel_calls[0][1]["actions"][0].text, "Show card in Browse")
        self.assertTrue(panel_calls[0][1]["quiet"])

    def test_primary_repair_card_is_not_repeated_as_support_panel(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")

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
            exclude_card_id=1,
        )

        self.assertIsNone(widget)

    def test_support_panel_shows_other_repair_cards_only(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        original_panel_card = debrief_dialog.panel_card
        original_secondary_button = debrief_dialog.secondary_button
        calls = []
        button_calls = []
        debrief_dialog.panel_card = lambda *args, **kwargs: calls.append((args, kwargs)) or "panel"
        debrief_dialog.secondary_button = lambda text: button_calls.append(text) or _FakeButton(text)
        try:
            widget = debrief_dialog._cards_to_fix_card(
                CardsToFix(
                    count=2,
                    clues=(("Long card", 1), ("Dense card", 1)),
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
                        MissedCardSummary(
                            2,
                            "Cardiology",
                            "Mitral regurgitation",
                            2,
                            3,
                            datetime(2026, 6, 26),
                            content_labels=("Dense card",),
                        ),
                    ),
                ),
                dialog=None,
                open_card=lambda _card_id: None,
                exclude_card_id=1,
            )
        finally:
            debrief_dialog.panel_card = original_panel_card
            debrief_dialog.secondary_button = original_secondary_button

        self.assertEqual(widget, "panel")
        self.assertEqual(calls[0][0][0], "Also check card format")
        self.assertIn("1 other card may need a card-format check", calls[0][0][1])
        self.assertEqual(calls[0][1]["rows"][0][0], "Also check")
        self.assertIn("Mitral regurgitation: Dense card", calls[0][1]["rows"][0][1])
        self.assertNotIn("Aortic stenosis", calls[0][1]["rows"][0][1])
        self.assertEqual(button_calls, ["Show card in Browse"])
        self.assertEqual(calls[0][1]["actions"][0].text, "Show card in Browse")

    def test_no_cards_to_fix_panel_uses_check_language(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        original_panel_card = debrief_dialog.panel_card
        calls = []
        debrief_dialog.panel_card = lambda *args, **kwargs: calls.append((args, kwargs)) or "panel"
        try:
            widget = debrief_dialog._cards_to_fix_card(CardsToFix(0, (), ()), dialog=None, open_card=None)
        finally:
            debrief_dialog.panel_card = original_panel_card

        self.assertEqual(widget, "panel")
        self.assertIn("Other cards may be more useful to check", calls[0][0][1])
        self.assertNotIn("evidence", calls[0][0][1].lower())
        self.assertTrue(calls[0][1]["quiet"])

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
        self.assertEqual(calls[0][0][0], "Ignore for now: early cards")
        self.assertIn("normal first-pass learning", calls[0][0][1])
        self.assertIn("not a card-edit signal", calls[0][0][1])
        self.assertIn("study extra only if these felt unfamiliar or clustered", calls[0][0][1])
        self.assertTrue(calls[0][1]["quiet"])
        self.assertNotIn("source", calls[0][0][1].lower())
        self.assertNotIn("weak evidence", calls[0][0][1].lower())

    def test_repeated_low_rep_support_copy_does_not_call_it_first_pass_learning(self) -> None:
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
                                2,
                                2,
                                datetime(2026, 6, 26),
                                card_reps=4,
                            ),
                        ),
                    ),
                    session_habits=SessionHabits(2, 2, 1.0, "Morning"),
                    missed_cards=(),
                )
            )
        finally:
            debrief_dialog.panel_card = original_panel_card

        self.assertEqual(widget, "panel")
        self.assertIn("early in review history", calls[0][0][1])
        self.assertIn("Do not over-interpret yet", calls[0][0][1])
        self.assertIn("same cards keep failing after a few more reps", calls[0][0][1])
        self.assertNotIn("first-pass learning", calls[0][0][1])

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
        cluster = MissedCardSummary(
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
        )
        debrief_dialog.recommendation_card = lambda *args, **kwargs: calls.append((args, kwargs)) or "recommendation"
        debrief_dialog.secondary_button = lambda text: button_calls.append(text) or _FakeButton(text)
        try:
            widget = debrief_dialog._next_step_card(
                Debrief(
                    study_next=(),
                    cards_to_fix=CardsToFix(0, (), ()),
                    early_learning=EarlyLearning(0, ()),
                    session_habits=SessionHabits(4, 2, 0.5, "Morning"),
                    missed_cards=(cluster,),
                    same_note_cluster=cluster,
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
        self.assertEqual(button_calls, ["Show card in Browse"])

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
        self.assertEqual(calls[0][0][0], "Also check cards")
        self.assertEqual(calls[0][1]["rows"][0][0], "Also check")
        self.assertEqual(calls[0][1]["rows"][1][0], "Why")
        self.assertEqual(calls[0][1]["rows"][2][0], "Also check")
        self.assertIn("Cardiology Valves", calls[0][1]["rows"][1][1])
        self.assertIn("mitral", calls[0][1]["rows"][2][1])
        self.assertNotIn(" in word", calls[0][1]["rows"][2][1])
        self.assertTrue(calls[0][1]["quiet"])
        self.assertNotIn("signal", calls[0][0][0].lower())
        self.assertNotIn("related material", calls[0][0][0].lower())

    def test_study_support_panel_does_not_compete_with_primary_check(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        self.assertTrue(
            debrief_dialog._show_study_support(
                Debrief(
                    study_next=(StudyTarget("AnKing::Cardiology::Valves", "tag", 2, 5, ("Murmur?",)),),
                    cards_to_fix=CardsToFix(
                        1,
                        (("Long card", 1),),
                        (
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
                    early_learning=EarlyLearning(0, ()),
                    session_habits=SessionHabits(5, 2, 0.4, "Morning"),
                    missed_cards=(),
                )
            )
        )

    def test_same_note_primary_can_still_show_related_material_support(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        cluster = MissedCardSummary(
            1,
            "AnKing",
            "Aortic stenosis cloze",
            2,
            3,
            datetime(2026, 6, 26),
            tags=("AnKing::Cardiology::Valves",),
            note_id=50,
            note_card_count=4,
            note_repeated_miss_count=2,
            card_reps=8,
        )

        debrief = Debrief(
            study_next=(StudyTarget("AnKing::Cardiology::Valves", "tag", 2, 5, ("Murmur?",)),),
            cards_to_fix=CardsToFix(0, (), ()),
            early_learning=EarlyLearning(0, ()),
            session_habits=SessionHabits(5, 2, 0.4, "Morning"),
            missed_cards=(cluster,),
            same_note_cluster=cluster,
        )

        self.assertEqual(debrief.next_check_kind, "same_note")
        self.assertTrue(debrief_dialog._show_study_support(debrief))

    def test_primary_study_target_is_not_repeated_as_support_panel(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        target = StudyTarget("AnKing::Cardiology::Valves", "tag", 2, 5, ("Murmur?",))

        widget = debrief_dialog._study_material_card(
            (target,),
            dialog=None,
            open_material=None,
            exclude_target=target,
        )

        self.assertIsNone(widget)

    def test_study_support_panel_shows_other_targets_only(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        original_panel_card = debrief_dialog.panel_card
        calls = []
        top_target = StudyTarget("AnKing::Cardiology::Valves", "tag", 2, 5, ("Murmur?",))
        other_target = StudyTarget("mitral", "term", 2, 6, ("Mitral regurgitation",))
        debrief_dialog.panel_card = lambda *args, **kwargs: calls.append((args, kwargs)) or "panel"
        try:
            widget = debrief_dialog._study_material_card(
                (top_target, other_target),
                dialog=None,
                open_material=None,
                exclude_target=top_target,
            )
        finally:
            debrief_dialog.panel_card = original_panel_card

        self.assertEqual(widget, "panel")
        self.assertEqual(calls[0][0][0], "Also check cards")
        self.assertEqual(calls[0][1]["rows"][0][0], "Also check")
        self.assertIn("Mitral regurgitation", calls[0][1]["rows"][0][1])
        self.assertNotIn("Murmur?", calls[0][1]["rows"][0][1])

    def test_study_support_panel_hides_duplicate_missed_examples(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        primary = StudyTarget(
            "AnKing::Cardiology::Valves",
            "tag",
            2,
            5,
            ("Murmur?", "Aortic stenosis murmur"),
            related_card_ids=(10, 11),
        )
        duplicate = StudyTarget(
            "stenosis",
            "term",
            2,
            4,
            ("Murmur?", "Aortic stenosis murmur"),
            related_card_ids=(10, 11),
        )

        widget = debrief_dialog._study_material_card(
            (primary, duplicate),
            dialog=None,
            open_material=None,
            exclude_target=primary,
        )

        self.assertIsNone(widget)

    def test_study_support_panel_hides_same_displayed_target(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        primary = StudyTarget(
            "AnKing::Cardiology::Valves",
            "tag",
            80,
            300,
            ("Valve physiology missed example 300",),
            related_card_ids=(300,),
        )
        same_display_label = StudyTarget(
            "AnKing_Cardiology_Valves",
            "tag",
            2,
            5,
            ("Murmur?", "Aortic stenosis murmur"),
            related_card_ids=(10, 11),
        )

        widget = debrief_dialog._study_material_card(
            (primary, same_display_label),
            dialog=None,
            open_material=None,
            exclude_target=primary,
        )

        self.assertIsNone(widget)

    def test_study_support_panel_keeps_distinct_missed_examples(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        original_panel_card = debrief_dialog.panel_card
        calls = []
        primary = StudyTarget(
            "AnKing::Cardiology::Valves",
            "tag",
            2,
            5,
            ("Murmur?", "Aortic stenosis murmur"),
            related_card_ids=(10, 11),
        )
        distinct = StudyTarget(
            "mitral",
            "term",
            2,
            6,
            ("Mitral regurgitation",),
            related_card_ids=(12,),
        )
        debrief_dialog.panel_card = lambda *args, **kwargs: calls.append((args, kwargs)) or "panel"
        try:
            widget = debrief_dialog._study_material_card(
                (primary, distinct),
                dialog=None,
                open_material=None,
                exclude_target=primary,
            )
        finally:
            debrief_dialog.panel_card = original_panel_card

        self.assertEqual(widget, "panel")
        self.assertIn("Mitral regurgitation", calls[0][1]["rows"][0][1])

    def test_study_support_panel_can_open_exact_missed_examples(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        original_panel_card = debrief_dialog.panel_card
        original_secondary_button = debrief_dialog.secondary_button
        calls = []
        button_calls = []
        target = StudyTarget(
            "AnKing::Cardiology::Valves",
            "tag",
            2,
            5,
            ("Murmur?",),
            related_card_ids=(10, 11),
        )
        debrief_dialog.panel_card = lambda *args, **kwargs: calls.append((args, kwargs)) or "panel"
        debrief_dialog.secondary_button = lambda text: button_calls.append(text) or _FakeButton(text)
        try:
            widget = debrief_dialog._study_material_card(
                (target,),
                dialog=None,
                open_material=lambda _target: None,
            )
        finally:
            debrief_dialog.panel_card = original_panel_card
            debrief_dialog.secondary_button = original_secondary_button

        self.assertEqual(widget, "panel")
        self.assertEqual(button_calls, ["Show 2 missed examples"])
        self.assertEqual(calls[0][1]["actions"][0].text, "Show 2 missed examples")

    def test_study_support_panel_names_single_exact_missed_example(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        original_panel_card = debrief_dialog.panel_card
        original_secondary_button = debrief_dialog.secondary_button
        calls = []
        button_calls = []
        target = StudyTarget(
            "mitral",
            "term",
            1,
            4,
            ("Mitral regurgitation",),
            related_card_ids=(12,),
        )
        debrief_dialog.panel_card = lambda *args, **kwargs: calls.append((args, kwargs)) or "panel"
        debrief_dialog.secondary_button = lambda text: button_calls.append(text) or _FakeButton(text)
        try:
            widget = debrief_dialog._study_material_card(
                (target,),
                dialog=None,
                open_material=lambda _target: None,
            )
        finally:
            debrief_dialog.panel_card = original_panel_card
            debrief_dialog.secondary_button = original_secondary_button

        self.assertEqual(widget, "panel")
        self.assertEqual(button_calls, ["Show 1 missed example"])
        self.assertEqual(calls[0][1]["actions"][0].text, "Show 1 missed example")

    def test_study_support_panel_does_not_add_broad_search_action(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        original_panel_card = debrief_dialog.panel_card
        original_secondary_button = debrief_dialog.secondary_button
        calls = []
        button_calls = []
        debrief_dialog.panel_card = lambda *args, **kwargs: calls.append((args, kwargs)) or "panel"
        debrief_dialog.secondary_button = lambda text: button_calls.append(text) or _FakeButton(text)
        try:
            widget = debrief_dialog._study_material_card(
                (StudyTarget("AnKing::Cardiology::Valves", "tag", 2, 5, ("Murmur?",)),),
                dialog=None,
                open_material=lambda _target: None,
            )
        finally:
            debrief_dialog.panel_card = original_panel_card
            debrief_dialog.secondary_button = original_secondary_button

        self.assertEqual(widget, "panel")
        self.assertEqual(button_calls, [])
        self.assertEqual(calls[0][1]["actions"], ())

    def test_study_recommendation_uses_maturity_specific_next_step(self) -> None:
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
                    study_next=(
                        StudyTarget(
                            "AnKing::Cardiology::Valves",
                            "tag",
                            4,
                            8,
                            ("Aortic stenosis", "Mitral regurgitation"),
                            early_count=1,
                            mature_count=3,
                            related_card_ids=(10, 11),
                        ),
                    ),
                    cards_to_fix=CardsToFix(0, (), ()),
                    early_learning=EarlyLearning(0, ()),
                    session_habits=SessionHabits(8, 4, 0.5, "Evening"),
                    missed_cards=(),
                ),
                dialog=None,
                open_card=None,
                open_material=lambda _target: None,
            )
        finally:
            debrief_dialog.recommendation_card = original_recommendation_card
            debrief_dialog.secondary_button = original_secondary_button

        self.assertEqual(widget, "recommendation")
        self.assertEqual(calls[0][0][0], "Check missed examples from Cardiology Valves")
        self.assertEqual(calls[0][1]["confidence"], "4 of 8 cards in this group needed another pass.")
        self.assertIn("Look at the missed examples", calls[0][1]["next_step"])
        self.assertIn("revisit the surrounding concept", calls[0][1]["next_step"])
        self.assertIn("3 mature", calls[0][1]["evidence"])
        self.assertNotIn("4 of 8", calls[0][1]["evidence"])
        self.assertEqual(button_calls, ["Show 2 missed examples"])

    def test_study_recommendation_names_hidden_large_missed_set(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        original_recommendation_card = debrief_dialog.recommendation_card
        calls = []
        debrief_dialog.recommendation_card = lambda *args, **kwargs: calls.append((args, kwargs)) or "recommendation"
        try:
            widget = debrief_dialog._next_step_card(
                Debrief(
                    study_next=(
                        StudyTarget(
                            "AnKing::Cardiology::Valves",
                            "tag",
                            80,
                            300,
                            (
                                "Valve physiology missed example 298 with long AnKing-style clinical wording",
                                "Valve physiology missed example 299 with long AnKing-style clinical wording",
                                "Valve physiology missed example 300 with long AnKing-style clinical wording",
                            ),
                            lapsed_count=80,
                            related_card_ids=(298, 299, 300),
                        ),
                    ),
                    cards_to_fix=CardsToFix(0, (), ()),
                    early_learning=EarlyLearning(0, ()),
                    session_habits=SessionHabits(380, 80, 0.21, "Evening"),
                    missed_cards=(),
                ),
                dialog=None,
                open_card=None,
                open_material=None,
            )
        finally:
            debrief_dialog.recommendation_card = original_recommendation_card

        self.assertEqual(widget, "recommendation")
        self.assertIn("+78 more missed cards", calls[0][1]["evidence"])
        self.assertLessEqual(len(calls[0][1]["evidence"].split("Breakdown:")[0]), 150)

    def test_study_recommendation_names_missed_examples_when_action_is_exact_cards(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        original_recommendation_card = debrief_dialog.recommendation_card
        calls = []
        debrief_dialog.recommendation_card = lambda *args, **kwargs: calls.append((args, kwargs)) or "recommendation"
        try:
            widget = debrief_dialog._next_step_card(
                Debrief(
                    study_next=(
                        StudyTarget(
                            "AnKing::Cardiology::Valves",
                            "tag",
                            2,
                            5,
                            ("Murmur?", "Aortic stenosis murmur"),
                            lapsed_count=2,
                            related_card_ids=(10, 11),
                        ),
                    ),
                    cards_to_fix=CardsToFix(0, (), ()),
                    early_learning=EarlyLearning(0, ()),
                    session_habits=SessionHabits(5, 2, 0.4, "Evening"),
                    missed_cards=(),
                ),
                dialog=None,
                open_card=None,
                open_material=None,
            )
        finally:
            debrief_dialog.recommendation_card = original_recommendation_card

        self.assertEqual(widget, "recommendation")
        self.assertEqual(calls[0][0][0], "Check missed examples from Cardiology Valves")
        self.assertIn("Check the missed examples", calls[0][1]["next_step"])
        self.assertNotIn("Open related cards", calls[0][1]["next_step"])
        self.assertNotIn("related cards", calls[0][1]["next_step"])
        self.assertIn("may just need another pass", calls[0][1]["next_step"])
        self.assertIn("inspect these examples", calls[0][1]["check"])

    def test_broad_study_recommendation_keeps_cautious_title(self) -> None:
        _install_fake_aqt()
        debrief_dialog = importlib.import_module("debrief_dialog")
        original_recommendation_card = debrief_dialog.recommendation_card
        calls = []
        debrief_dialog.recommendation_card = lambda *args, **kwargs: calls.append((args, kwargs)) or "recommendation"
        try:
            widget = debrief_dialog._next_step_card(
                Debrief(
                    study_next=(
                        StudyTarget(
                            "AnKing::Cardiology::Valves",
                            "tag",
                            2,
                            5,
                            ("Murmur?", "Aortic stenosis murmur"),
                            lapsed_count=2,
                        ),
                    ),
                    cards_to_fix=CardsToFix(0, (), ()),
                    early_learning=EarlyLearning(0, ()),
                    session_habits=SessionHabits(5, 2, 0.4, "Evening"),
                    missed_cards=(),
                ),
                dialog=None,
                open_card=None,
                open_material=None,
            )
        finally:
            debrief_dialog.recommendation_card = original_recommendation_card

        self.assertEqual(widget, "recommendation")
        self.assertEqual(calls[0][0][0], "Worth checking: Cardiology Valves")


if __name__ == "__main__":
    unittest.main()
