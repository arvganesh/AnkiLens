from __future__ import annotations

import unittest

from analytics import DeckMissSummary, NoteTypeMissSummary, TagMissSummary
from copy_text import (
    analytics_caption,
    deck_concentration_caption,
    note_type_concentration_caption,
    tag_concentration_caption,
)


class AnalyticsCopyTest(unittest.TestCase):
    def test_empty_caption_mentions_threshold(self) -> None:
        caption = analytics_caption(
            shown_count=0,
            minimum_misses=3,
            result_limit=20,
            lookback_days=30,
        )

        self.assertIn("No repeated misses found", caption)
        self.assertIn("after 3 Again ratings", caption)
        self.assertIn("last 30 days", caption)

    def test_result_caption_mentions_count_threshold_and_limit(self) -> None:
        caption = analytics_caption(
            shown_count=2,
            minimum_misses=2,
            result_limit=10,
            lookback_days=0,
        )

        self.assertIn("Showing 2 cards", caption)
        self.assertIn("at least 2 times", caption)
        self.assertIn("Limit: 10", caption)
        self.assertIn("all time", caption)

    def test_deck_concentration_caption_lists_decks(self) -> None:
        caption = deck_concentration_caption([DeckMissSummary("Cardiology", 2, 5)])

        self.assertIn("concentrated", caption)
        self.assertIn("Cardiology", caption)
        self.assertIn("2 cards, 5 misses", caption)

    def test_tag_concentration_caption_lists_tags(self) -> None:
        caption = tag_concentration_caption([TagMissSummary("murmurs", 2, 4)])

        self.assertIn("Tags with repeated misses", caption)
        self.assertIn("murmurs", caption)
        self.assertIn("2 cards, 4 misses", caption)

    def test_note_type_concentration_caption_lists_note_types(self) -> None:
        caption = note_type_concentration_caption([NoteTypeMissSummary("Cloze", 3, 8)])

        self.assertIn("Note types with repeated misses", caption)
        self.assertIn("Cloze", caption)
        self.assertIn("3 cards, 8 misses", caption)


if __name__ == "__main__":
    unittest.main()
