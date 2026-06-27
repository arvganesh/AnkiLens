from __future__ import annotations

import unittest
from datetime import datetime

from analytics import ReviewLogEntry, summarize_missed_cards


def _entry(card_id: int, ease: int, day: int) -> ReviewLogEntry:
    return ReviewLogEntry(
        card_id=card_id,
        ease=ease,
        reviewed_at=datetime(2026, 6, day),
        deck_name="Cardiology",
        card_label=f"Card {card_id}",
    )


class MissedCardAnalyticsTest(unittest.TestCase):
    def test_returns_empty_summary_when_there_are_no_reviews(self) -> None:
        self.assertEqual(summarize_missed_cards([]), [])

    def test_ignores_isolated_misses_by_default(self) -> None:
        summaries = summarize_missed_cards([_entry(1, 1, 1), _entry(2, 3, 2)])

        self.assertEqual(summaries, [])

    def test_summarizes_cards_with_repeated_misses(self) -> None:
        summaries = summarize_missed_cards(
            [
                _entry(1, 1, 1),
                _entry(1, 3, 2),
                _entry(1, 1, 3),
                _entry(2, 1, 4),
            ]
        )

        self.assertEqual(len(summaries), 1)
        self.assertEqual(summaries[0].card_id, 1)
        self.assertEqual(summaries[0].misses, 2)
        self.assertEqual(summaries[0].total_reviews, 3)

    def test_prioritizes_high_miss_rate_then_count(self) -> None:
        summaries = summarize_missed_cards(
            [
                _entry(1, 1, 1),
                _entry(1, 1, 2),
                _entry(1, 3, 3),
                _entry(2, 1, 1),
                _entry(2, 1, 2),
            ]
        )

        self.assertEqual([summary.card_id for summary in summaries], [2, 1])


if __name__ == "__main__":
    unittest.main()
