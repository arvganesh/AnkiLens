from __future__ import annotations

import unittest
from datetime import datetime

from analytics import ReviewLogEntry, summarize_content_patterns, summarize_missed_cards
from content_signals import content_labels


class ContentSignalsTest(unittest.TestCase):
    def test_labels_common_card_quality_signals(self) -> None:
        self.assertIn("Weak cue", content_labels("Broca area"))
        self.assertIn("Long card", content_labels("word " * 80))
        self.assertIn("Many numbers", content_labels("BP 120/80 Na 140 K 4.0 pH 7.4"))
        self.assertIn("Cloze-heavy", content_labels("{{c1::alpha}} {{c2::beta}}"))
        self.assertIn("Comparison", content_labels("Aortic stenosis vs mitral regurgitation"))
        self.assertIn("Media reference", content_labels("Look at heart_sound.png"))

    def test_missed_card_summary_includes_content_labels(self) -> None:
        summaries = summarize_missed_cards(
            [
                ReviewLogEntry(1, 1, datetime(2026, 6, 1), "Deck", "Card", source_text="word " * 80),
                ReviewLogEntry(1, 1, datetime(2026, 6, 2), "Deck", "Card", source_text="word " * 80),
            ]
        )

        self.assertEqual(summaries[0].content_labels, ("Long card", "Dense card"))

    def test_summarizes_content_patterns_from_missed_cards(self) -> None:
        summaries = summarize_missed_cards(
            [
                ReviewLogEntry(1, 1, datetime(2026, 6, 1), "Deck", "Card", source_text="word " * 80),
                ReviewLogEntry(1, 1, datetime(2026, 6, 2), "Deck", "Card", source_text="word " * 80),
            ]
        )

        self.assertEqual(summarize_content_patterns(summaries)["Long card"], 1)


if __name__ == "__main__":
    unittest.main()
