from __future__ import annotations

import unittest

from debrief import CardsToFix, SessionHabits, StudyTarget
from debrief_copy import cards_to_fix_caption, review_habits_caption, study_next_caption


class DebriefCopyTest(unittest.TestCase):
    def test_study_next_caption_lists_targets_without_scheduler_language(self) -> None:
        caption = study_next_caption((StudyTarget("mitral", "term", 2, ("Card 1", "Card 2")),))

        self.assertIn("Study next", caption)
        self.assertIn("mitral", caption)
        self.assertIn("examples: Card 1, Card 2", caption)
        self.assertNotIn("due", caption.lower())
        self.assertNotIn("must", caption.lower())

    def test_cards_to_fix_caption_is_conditional(self) -> None:
        caption = cards_to_fix_caption(CardsToFix(1, (("Weak cue", 1),), ()))

        self.assertIn("1 card may need editing", caption)
        self.assertIn("Weak cue", caption)

    def test_session_habits_caption_reports_observed_facts(self) -> None:
        caption = review_habits_caption(SessionHabits(10, 2, 0.2, "Evening", 10, 75.0, 7.5))

        self.assertIn("Review habits", caption)
        self.assertIn("Reviews: 10", caption)
        self.assertIn("Again rate: 20%", caption)
        self.assertIn("Latest review time: Evening", caption)
        self.assertIn("Recorded answer time: 1m 15s", caption)
        self.assertIn("Avg/card: 7.5s", caption)

    def test_session_habits_caption_hides_missing_duration(self) -> None:
        caption = review_habits_caption(SessionHabits(10, 2, 0.2, "Evening"))

        self.assertNotIn("Recorded answer time", caption)
        self.assertNotIn("Avg/card", caption)


if __name__ == "__main__":
    unittest.main()
