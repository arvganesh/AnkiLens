from __future__ import annotations

import unittest

from analytics import MissedCardSummary
from debrief import CardsToFix, EarlyLearning, SessionHabits, StudyTarget
from debrief_copy import cards_to_fix_caption, early_learning_caption, review_habits_caption, study_next_caption


class DebriefCopyTest(unittest.TestCase):
    def test_study_next_caption_lists_targets_without_scheduler_language(self) -> None:
        caption = study_next_caption((StudyTarget("mitral", "term", 2, 6, ("Card 1", "Card 2")),))

        self.assertIn("Review: mitral", caption)
        self.assertIn("2 of 6 reviewed cards missed in word", caption)
        self.assertIn("Examples: Card 1, Card 2", caption)
        self.assertNotIn("if the card", caption.lower())
        self.assertNotIn("due", caption.lower())
        self.assertNotIn("must", caption.lower())

    def test_tag_study_next_caption_names_active_cards(self) -> None:
        caption = study_next_caption((StudyTarget("AnKing::Cardiology::Valves", "tag", 2, 5, ("Murmur?",)),))

        self.assertIn("2 of 5 reviewed active cards missed in tag", caption)

    def test_cards_to_fix_caption_lists_capped_cards_to_inspect(self) -> None:
        card = MissedCardSummary(
            123,
            "Deck",
            "Mitral regurgitation",
            3,
            4,
            None,
            content_labels=("Weak cue", "Comparison"),
        )

        caption = cards_to_fix_caption(CardsToFix(1, (("Weak cue", 1),), (card,)))

        self.assertIn("Cards worth checking", caption)
        self.assertIn("1 mature card shows stronger card-specific clues", caption)
        self.assertIn("Mitral regurgitation: Weak cue, Comparison; missed 3/4 reviews", caption)

    def test_cards_to_fix_caption_handles_no_construction_clues(self) -> None:
        caption = cards_to_fix_caption(CardsToFix(0, (), ()))

        self.assertIn("No card repair stands out", caption)
        self.assertIn("No strong card-specific pattern surfaced", caption)

    def test_early_learning_caption_keeps_evidence_cautious(self) -> None:
        caption = early_learning_caption(EarlyLearning(2, ()))

        self.assertIn("Early material", caption)
        self.assertIn("2 early cards are still early in learning", caption)
        self.assertIn("weak evidence before editing from it alone", caption)
        self.assertNotIn("unlearned", caption.lower())
        self.assertNotIn("bad card", caption.lower())

    def test_session_habits_caption_reports_observed_facts(self) -> None:
        caption = review_habits_caption(SessionHabits(10, 2, 0.2, "Evening", 10, 75.0, 7.5))

        self.assertIn("Session context", caption)
        self.assertIn("Reviews: 10", caption)
        self.assertIn("Again rate: 20%", caption)
        self.assertIn("Latest review time: Evening", caption)
        self.assertIn("Recorded answer time: 1m 15s", caption)
        self.assertIn("Avg/card: 7.5s", caption)
        self.assertIn("Context only", caption)

    def test_session_habits_caption_hides_missing_duration(self) -> None:
        caption = review_habits_caption(SessionHabits(10, 2, 0.2, "Evening"))

        self.assertNotIn("Recorded answer time", caption)
        self.assertNotIn("Avg/card", caption)


if __name__ == "__main__":
    unittest.main()
