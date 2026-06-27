from __future__ import annotations

import unittest
from datetime import datetime

from analytics import MissedCardSummary
from debrief import SessionHabits
from debrief_dialog_copy import (
    card_search_button_text,
    debrief_title,
    debrief_window_title,
    deck_debrief_button_text,
    early_learning_evidence,
    early_learning_next_step,
    early_learning_title,
    no_repair_signal_text,
    related_search_button_text,
    repair_action_summary,
    repair_evidence,
    repair_next_step,
    short_label,
    study_target_title,
    study_next_step,
    supporting_cards_button_text,
)
from session_context import session_context_text


class DebriefDialogTest(unittest.TestCase):
    def test_study_target_title_uses_review_language(self) -> None:
        self.assertEqual(
            study_target_title("AnKing Cardiology Valves"),
            "Suggested next check: review AnKing Cardiology Valves",
        )

    def test_debrief_surface_copy_focuses_on_review_check(self) -> None:
        self.assertEqual(debrief_window_title(), "Bonsai Review Check")
        self.assertEqual(debrief_title(), "Review Check")
        self.assertEqual(deck_debrief_button_text(), "Review Check")

    def test_debrief_action_copy_is_clear_and_cautious(self) -> None:
        self.assertEqual(early_learning_title(), "Suggested next check: retry early material")
        self.assertEqual(card_search_button_text(), "Copy search for this card")
        self.assertEqual(related_search_button_text(), "Copy search for related cards")
        self.assertEqual(supporting_cards_button_text(), "See supporting cards")
        self.assertEqual(no_repair_signal_text(), "No strong card-construction clue stood out.")

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

        self.assertEqual(repair_evidence(summary), "Missed 3/5 recent reviews; clues: Long card, Dense card.")
        self.assertIn("Inspect the prompt first", repair_next_step())
        self.assertEqual(study_next_step("tag"), "Review this tagged topic, then retry the related cards.")

    def test_study_next_step_matches_target_kind(self) -> None:
        self.assertIn("shared concept", study_next_step("term"))
        self.assertIn("broad deck signal", study_next_step("deck"))
        self.assertIn("related cards", study_next_step("unknown"))

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
        self.assertEqual(early_learning_evidence(2), "2 early cards are still in first-pass learning.")
        self.assertEqual(
            early_learning_next_step(),
            "Treat this as normal learning first: quick source check, then retry.",
        )

    def test_session_context_is_hidden_for_tiny_windows(self) -> None:
        context = session_context_text(SessionHabits(4, 1, 0.25, "Evening"))

        self.assertEqual(context, "")

    def test_session_context_omits_unreliable_timing(self) -> None:
        context = session_context_text(SessionHabits(10, 2, 0.2, "Evening", 1, 7.0, 7.0))

        self.assertEqual(context, "Observed only: 10 reviews · 20% Again · evening")

    def test_session_context_includes_timing_when_most_reviews_are_timed(self) -> None:
        context = session_context_text(SessionHabits(10, 2, 0.2, "Evening", 8, 60.0, 7.5))

        self.assertEqual(context, "Observed only: 10 reviews · 20% Again · evening · 7.5s/card")


if __name__ == "__main__":
    unittest.main()
