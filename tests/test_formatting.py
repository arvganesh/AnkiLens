from __future__ import annotations

import unittest
from datetime import datetime

from analytics import MissedCardSummary
from formatting import format_review_date
from formatting import priority_label


class FormattingTest(unittest.TestCase):
    def test_formats_review_date(self) -> None:
        self.assertEqual(format_review_date(datetime(2026, 6, 26, 15, 4)), "2026-06-26")

    def test_formats_missing_review_date(self) -> None:
        self.assertEqual(format_review_date(None), "Not yet")

    def test_labels_high_rate_repeated_misses(self) -> None:
        summary = MissedCardSummary(1, "Deck", "Card", 3, 4, datetime(2026, 6, 26))

        self.assertEqual(priority_label(summary), "Start here")

    def test_labels_high_count_lower_rate_misses(self) -> None:
        summary = MissedCardSummary(1, "Deck", "Card", 3, 10, datetime(2026, 6, 26))

        self.assertEqual(priority_label(summary), "Check soon")

    def test_labels_lower_count_repeated_misses(self) -> None:
        summary = MissedCardSummary(1, "Deck", "Card", 2, 3, datetime(2026, 6, 26))

        self.assertEqual(priority_label(summary), "Watch next review")


if __name__ == "__main__":
    unittest.main()
