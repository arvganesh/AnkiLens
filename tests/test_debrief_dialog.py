from __future__ import annotations

import unittest
from datetime import datetime

from analytics import MissedCardSummary
from debrief import SessionHabits
from debrief_dialog_copy import (
    card_search_button_text,
    early_learning_title,
    related_search_button_text,
    repair_action_summary,
    short_label,
    study_target_title,
)
from session_context import session_context_text


class DebriefDialogTest(unittest.TestCase):
    def test_study_target_title_uses_review_language(self) -> None:
        self.assertEqual(
            study_target_title("AnKing Cardiology Valves"),
            "Suggested next check: review AnKing Cardiology Valves",
        )

    def test_debrief_action_copy_is_clear_and_cautious(self) -> None:
        self.assertEqual(early_learning_title(), "Suggested next check: retry early material")
        self.assertEqual(card_search_button_text(), "Copy search for this card")
        self.assertEqual(related_search_button_text(), "Copy search for related cards")

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
