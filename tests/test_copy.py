from __future__ import annotations

import unittest
from datetime import datetime

from analytics import DeckMissSummary, MissedCardSummary, TagMissSummary
from copy_text import (
    analytics_caption,
    card_detail_caption,
    check_cards_caption,
    content_pattern_caption,
    deck_concentration_caption,
    study_content_caption,
    tag_concentration_caption,
    term_caption,
    workflow_caption,
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

        self.assertIn("Supporting evidence for the debrief: 2 cards", caption)
        self.assertIn("at least 2 times", caption)
        self.assertIn("Limit: 10", caption)
        self.assertIn("all time", caption)

    def test_deck_concentration_caption_lists_decks(self) -> None:
        caption = deck_concentration_caption([DeckMissSummary("Cardiology", 2, 5)])

        self.assertIn("Decks with repeated misses", caption)
        self.assertIn("Cardiology", caption)
        self.assertIn("2 cards, 5 misses", caption)

    def test_tag_concentration_caption_lists_tags(self) -> None:
        caption = tag_concentration_caption([TagMissSummary("murmurs", 2, 4)])

        self.assertIn("Tags with repeated misses", caption)
        self.assertIn("murmurs", caption)
        self.assertIn("2 cards, 4 misses", caption)

    def test_content_pattern_caption_lists_patterns(self) -> None:
        caption = content_pattern_caption({"Dense card": 2})

        self.assertIn("Card construction clues", caption)
        self.assertIn("Dense card", caption)
        self.assertIn("2 cards", caption)

    def test_term_caption_lists_terms(self) -> None:
        caption = term_caption([("mitral", 2)])

        self.assertIn("Repeated terms to study", caption)
        self.assertIn("mitral", caption)

    def test_workflow_copy_separates_card_fixing_from_study(self) -> None:
        self.assertIn("inspect the cards behind the recommendation", workflow_caption())
        self.assertEqual(check_cards_caption(), "Inspect card quality")
        self.assertEqual(study_content_caption(), "Review material if the cards look clear")

    def test_card_detail_caption_explains_selected_card(self) -> None:
        summary = MissedCardSummary(
            123,
            "Deck",
            "Mitral regurgitation",
            3,
            4,
            datetime(2026, 6, 26),
            source_text="Mitral regurgitation murmur",
            content_labels=("Comparison",),
        )

        caption = card_detail_caption(summary)

        self.assertIn("Selected card: Mitral regurgitation", caption)
        self.assertIn("Clues: Comparison", caption)
        self.assertIn("Misses: 3/4 reviews (75%)", caption)
        self.assertIn("Browser search: cid:123", caption)
        self.assertIn("Text: Mitral regurgitation murmur", caption)

    def test_card_detail_caption_truncates_long_text(self) -> None:
        summary = MissedCardSummary(123, "Deck", "Card", 2, 3, None, source_text="word " * 80)

        caption = card_detail_caption(summary)

        self.assertLess(len(caption), 320)
        self.assertIn("...", caption)


if __name__ == "__main__":
    unittest.main()
