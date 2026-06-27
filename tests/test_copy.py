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
    evidence_title,
    evidence_window_title,
    selected_card_button_text,
    selected_card_status_text,
    review_window_value,
    same_note_context,
    study_content_caption,
    supporting_metric_labels,
    supporting_table_headers,
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
        self.assertIn("after needing another pass 3 times", caption)
        self.assertIn("last 30 days", caption)

    def test_result_caption_mentions_count_threshold_and_limit(self) -> None:
        caption = analytics_caption(
            shown_count=2,
            minimum_misses=2,
            result_limit=10,
            lookback_days=0,
        )

        self.assertIn("Details for the current check: 2 cards", caption)
        self.assertIn("at least 2 times", caption)
        self.assertNotIn("Limit", caption)
        self.assertIn("all time", caption)

    def test_evidence_caption_handles_one_day_window_cleanly(self) -> None:
        caption = analytics_caption(
            shown_count=1,
            minimum_misses=2,
            result_limit=20,
            lookback_days=1,
        )

        self.assertIn("last 24 hours", caption)
        self.assertNotIn("last 1 days", caption)

    def test_evidence_dialog_title_matches_debrief_button_language(self) -> None:
        self.assertEqual(evidence_window_title(), "Bonsai Details")
        self.assertEqual(evidence_title(), "Supporting Details")

    def test_evidence_window_metric_handles_one_day_window_cleanly(self) -> None:
        self.assertEqual(review_window_value(1), "24 hours")
        self.assertEqual(review_window_value(0), "all time")
        self.assertEqual(review_window_value(2), "2 days")

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

        self.assertIn("Format clues to inspect", caption)
        self.assertNotIn("Possible", caption)
        self.assertIn("Dense card", caption)
        self.assertIn("2 cards", caption)

    def test_term_caption_lists_terms(self) -> None:
        caption = term_caption([("mitral", 2)])

        self.assertIn("Repeated wording to check", caption)
        self.assertNotIn("sample", caption.lower())
        self.assertIn("mitral", caption)

    def test_workflow_copy_separates_card_fixing_from_study(self) -> None:
        self.assertIn("inspect the cards behind the recommendation", workflow_caption())
        self.assertEqual(check_cards_caption(), "Inspect card format")
        self.assertEqual(study_content_caption(), "Material to check")

    def test_supporting_metric_labels_are_evidence_oriented(self) -> None:
        self.assertEqual(
            supporting_metric_labels(),
            ("cards to inspect", "repeated misses", "review window"),
        )

    def test_supporting_table_headers_name_card_clues(self) -> None:
        self.assertEqual(
            supporting_table_headers(),
            ("Card", "Deck", "Next check", "Format clues", "Misses", "Reviews", "Miss rate", "Last missed"),
        )

    def test_selected_card_action_opens_browse_with_copy_fallback(self) -> None:
        self.assertEqual(selected_card_button_text(), "Open selected card in Browse")
        self.assertEqual(
            selected_card_status_text("cid:123", opened=True),
            "Opened in Browse. Search copied.",
        )
        self.assertEqual(selected_card_status_text("cid:123", opened=False), "Copied: cid:123")

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
        self.assertIn("Format clues: Comparison", caption)
        self.assertNotIn("Same note:", caption)
        self.assertIn("Needed another pass: 3/4 reviews (75%)", caption)
        self.assertIn("Next: open the card and read the prompt before deciding whether to edit.", caption)
        self.assertNotIn("Misses:", caption)
        self.assertIn("Browser search: cid:123", caption)
        self.assertIn("Text: Mitral regurgitation murmur", caption)

    def test_card_detail_caption_names_missing_format_clues(self) -> None:
        summary = MissedCardSummary(123, "Deck", "Card", 2, 3, None)

        caption = card_detail_caption(summary)

        self.assertIn("Format clues: No format clue", caption)
        self.assertNotIn("No obvious clue", caption)

    def test_card_detail_caption_truncates_long_text(self) -> None:
        summary = MissedCardSummary(123, "Deck", "Card", 2, 3, None, source_text="word " * 80)

        caption = card_detail_caption(summary)

        self.assertLess(len(caption), 320)
        self.assertIn("...", caption)

    def test_same_note_context_distinguishes_isolated_and_clustered_clozes(self) -> None:
        unavailable = MissedCardSummary(122, "Deck", "Solo", 2, 3, None)
        isolated = MissedCardSummary(
            123,
            "Deck",
            "Card",
            2,
            3,
            None,
            note_id=50,
            note_card_count=4,
            note_repeated_miss_count=1,
        )
        clustered = MissedCardSummary(
            124,
            "Deck",
            "Sibling",
            2,
            3,
            None,
            note_id=50,
            note_card_count=4,
            note_repeated_miss_count=3,
        )

        self.assertEqual(same_note_context(unavailable), "")
        self.assertEqual(same_note_context(isolated), "Same note: only this card needed another pass out of 4")
        self.assertEqual(
            same_note_context(clustered),
            "Same note: 3 of 4 sibling cards also needed another pass; inspect them together before editing or studying more",
        )


if __name__ == "__main__":
    unittest.main()
