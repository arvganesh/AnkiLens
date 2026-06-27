from __future__ import annotations

import unittest
from datetime import datetime

from analytics import MissedCardSummary
from debrief import SessionHabits
from debrief_dialog_copy import (
    card_search_button_text,
    debrief_intro_text,
    debrief_title,
    debrief_window_title,
    deck_debrief_button_text,
    early_learning_evidence,
    early_learning_check_text,
    early_learning_next_step,
    early_learning_title,
    evidence_confidence_text,
    mixed_repair_signal_text,
    no_pattern_evidence,
    no_pattern_next_step,
    no_pattern_title,
    no_repair_signal_text,
    related_search_button_text,
    repair_action_summary,
    repair_evidence,
    repair_next_step,
    repair_title,
    short_label,
    study_target_title,
    study_next_step,
    supporting_cards_button_text,
    target_display_label,
    target_evidence_text,
)
from session_context import session_context_text


class DebriefDialogTest(unittest.TestCase):
    def test_study_target_title_uses_review_language(self) -> None:
        self.assertEqual(
            study_target_title("Cardiology Valves"),
            "Possible study target: Cardiology Valves",
        )

    def test_tag_targets_are_readable_concepts_with_examples(self) -> None:
        self.assertEqual(
            target_display_label("AnKing::Cardiology::Valves", "tag"),
            "Cardiology Valves",
        )
        self.assertEqual(
            target_display_label("AnKing_Cardiology_Valves", "tag"),
            "Cardiology Valves",
        )
        self.assertEqual(
            target_evidence_text(2, 5, "Cardiology Valves", ("Murmur?", "Aortic stenosis murmur")),
            "2 of 5 reviewed cards missed in Cardiology Valves. Examples: Murmur?, Aortic stenosis murmur.",
        )

    def test_debrief_surface_copy_focuses_on_review_check(self) -> None:
        self.assertEqual(debrief_window_title(), "Bonsai Next Check")
        self.assertEqual(debrief_title(), "Next Check")
        self.assertEqual(deck_debrief_button_text(), "Next Check")

    def test_debrief_intro_names_short_recent_window(self) -> None:
        self.assertEqual(debrief_intro_text(1), "Last 24 hours · read-only · Bonsai does not change scheduling.")
        self.assertIn("Last 2 days", debrief_intro_text(2))

    def test_debrief_action_copy_is_clear_and_cautious(self) -> None:
        self.assertEqual(early_learning_title(), "Likely normal first-pass learning")
        self.assertEqual(card_search_button_text(), "View this card in Browse")
        self.assertEqual(related_search_button_text(), "View related cards in Browse")
        self.assertEqual(supporting_cards_button_text(), "Review evidence cards")
        self.assertEqual(no_repair_signal_text(), "No obvious card-format issue stood out.")
        self.assertIn("One card also has format clues", mixed_repair_signal_text())

    def test_featured_recommendation_copy_separates_evidence_from_action(self) -> None:
        summary = MissedCardSummary(
            1,
            "Cardiology",
            "Aortic stenosis murmur",
            3,
            5,
            datetime(2026, 6, 26),
            content_labels=("Long card", "Dense card"),
        )

        self.assertEqual(repair_title("Aortic stenosis murmur"), "Card worth inspecting: Aortic stenosis murmur")
        self.assertEqual(repair_evidence(summary), "Missed 3/5 recent reviews; clues: Long card, Dense card.")
        self.assertIn("Inspect the prompt first", repair_next_step())
        self.assertEqual(
            study_next_step("tag"),
            "Do a short source refresh for this topic, then retry the related cards.",
        )

    def test_evidence_confidence_copy_does_not_overclaim_thin_signals(self) -> None:
        self.assertEqual(evidence_confidence_text(2, 5), "Limited evidence")
        self.assertEqual(evidence_confidence_text(3, 8), "Stronger evidence")
        self.assertEqual(evidence_confidence_text(3, 8, mixed_signals=True), "Limited evidence")
        self.assertEqual(evidence_confidence_text(3, 0, early_learning=True), "Weak evidence")

    def test_study_next_step_matches_target_kind(self) -> None:
        self.assertIn("shared concept", study_next_step("term"))
        self.assertIn("broad deck signal", study_next_step("deck"))
        self.assertIn("related cards", study_next_step("unknown"))

    def test_no_pattern_copy_stays_actionable_without_overclaiming(self) -> None:
        self.assertEqual(no_pattern_title(), "No clear next check yet")
        self.assertIn("not enough shared signal", no_pattern_evidence())
        self.assertIn("review evidence cards", no_pattern_next_step())
        self.assertIn("wait for a clearer pattern", no_pattern_next_step())

    def test_no_pattern_copy_handles_no_repeated_misses(self) -> None:
        self.assertEqual(no_pattern_title(has_repeated_misses=False), "Nothing to check yet")
        self.assertIn("No card crossed the repeated-miss threshold", no_pattern_evidence(has_repeated_misses=False))
        self.assertIn("Keep reviewing", no_pattern_next_step(has_repeated_misses=False))

    def test_repair_action_summary_names_evidence_and_uncertainty(self) -> None:
        summary = MissedCardSummary(
            1,
            "Cardiology",
            "Aortic stenosis murmur",
            3,
            5,
            datetime(2026, 6, 26),
            content_labels=("Long card", "Dense card"),
        )

        body = repair_action_summary(summary)

        self.assertIn("Missed 3/5 recent reviews", body)
        self.assertIn("clues: Long card, Dense card", body)
        self.assertIn("leave it and review the source if the card is clear", body)

    def test_short_label_truncates_long_card_names(self) -> None:
        self.assertEqual(short_label("A" * 70), "A" * 61 + "...")

    def test_early_learning_copy_frames_normal_first_pass_learning(self) -> None:
        self.assertEqual(early_learning_evidence(2), "2 early cards are still in first-pass learning, not mature lapses.")
        self.assertEqual(
            early_learning_next_step(),
            "Do a quick source refresh, then retry. Do not edit these cards yet.",
        )
        self.assertIn("weak evidence", early_learning_check_text())
        self.assertIn("after more reps", early_learning_check_text())

    def test_session_context_is_hidden_for_tiny_windows(self) -> None:
        context = session_context_text(SessionHabits(4, 1, 0.25, "Evening"))

        self.assertEqual(context, "")

    def test_session_context_hides_normal_observed_stats(self) -> None:
        context = session_context_text(SessionHabits(10, 2, 0.2, "Evening", 1, 7.0, 7.0))

        self.assertEqual(context, "")

    def test_session_context_warns_when_again_rate_is_high(self) -> None:
        context = session_context_text(SessionHabits(10, 4, 0.4, "Evening", 1, 7.0, 7.0))

        self.assertIn("40% Again across 10 reviews", context)
        self.assertIn("refresh the source before editing cards", context)

    def test_session_context_warns_when_reviewing_unusually_fast(self) -> None:
        context = session_context_text(SessionHabits(10, 2, 0.2, "Evening", 8, 60.0, 7.5))

        self.assertEqual(context, "")

        fast_context = session_context_text(SessionHabits(10, 2, 0.2, "Evening", 8, 20.0, 2.5))

        self.assertIn("2.5s/card", fast_context)
        self.assertIn("treat misses as weaker evidence", fast_context)


if __name__ == "__main__":
    unittest.main()
