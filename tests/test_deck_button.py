from __future__ import annotations

import unittest

from deck_button import BUTTON_MESSAGE, deck_button_html


class DeckButtonTest(unittest.TestCase):
    def test_button_sends_bonsai_open_message(self) -> None:
        html = deck_button_html()

        self.assertIn(BUTTON_MESSAGE, html)
        self.assertIn("Open Bonsai", html)

    def test_summary_shows_repeated_miss_count(self) -> None:
        html = deck_button_html(missed_cards=2, lookback_days=90)

        self.assertIn("2 cards needing another pass", html)
        self.assertIn("last 90 days", html)

    def test_summary_handles_zero_repeated_misses(self) -> None:
        html = deck_button_html(missed_cards=0, lookback_days=90)

        self.assertIn("No repeated misses found", html)


if __name__ == "__main__":
    unittest.main()
