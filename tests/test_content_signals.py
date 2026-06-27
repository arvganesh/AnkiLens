from __future__ import annotations

import unittest
from datetime import datetime

from analytics import ReviewLogEntry, summarize_content_patterns, summarize_missed_cards
from content_signals import content_labels


class ContentSignalsTest(unittest.TestCase):
    def test_labels_long_cards(self) -> None:
        self.assertIn("Long card", content_labels("word " * 80))

    def test_labels_dense_cards(self) -> None:
        self.assertIn("Dense card", content_labels("word " * 40))

    def test_labels_many_numbers(self) -> None:
        self.assertIn("Many numbers", content_labels("BP 120/80 Na 140 K 4.0 pH 7.4"))

    def test_labels_cloze_heavy_cards(self) -> None:
        self.assertIn("Cloze-heavy", content_labels("{{c1::alpha}} {{c2::beta}}"))

    def test_labels_media_references(self) -> None:
        self.assertIn("Media reference", content_labels("Look at heart_sound.png"))

    def test_missed_card_summary_includes_content_labels(self) -> None:
        summaries = summarize_missed_cards(
            [
                ReviewLogEntry(1, 1, datetime(2026, 6, 1), "Deck", "Card", source_text="word " * 80),
                ReviewLogEntry(1, 1, datetime(2026, 6, 2), "Deck", "Card", source_text="word " * 80),
            ]
        )

        self.assertEqual(summaries[0].content_labels, ("Repeated miss", "Long card", "Dense card"))

    def test_summarizes_content_patterns(self) -> None:
        summaries = summarize_missed_cards(
            [
                ReviewLogEntry(1, 1, datetime(2026, 6, 1), "Deck", "Card", source_text="word " * 80),
                ReviewLogEntry(1, 1, datetime(2026, 6, 2), "Deck", "Card", source_text="word " * 80),
            ]
        )

        self.assertEqual(summarize_content_patterns(summaries)["Long card"], 1)


if __name__ == "__main__":
    unittest.main()
