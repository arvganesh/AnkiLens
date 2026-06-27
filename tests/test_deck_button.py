from __future__ import annotations

import unittest

from deck_button import BUTTON_MESSAGE, DEBRIEF_MESSAGE, deck_button_html


class DeckButtonTest(unittest.TestCase):
    def test_button_sends_bonsai_open_message(self) -> None:
        html = deck_button_html()

        self.assertIn(BUTTON_MESSAGE, html)
        self.assertIn("See supporting evidence", html)
        self.assertNotIn("Review evidence", html)
        self.assertIn(DEBRIEF_MESSAGE, html)
        self.assertIn("What should I check?", html)
        self.assertLess(html.index(DEBRIEF_MESSAGE), html.index(BUTTON_MESSAGE))
        self.assertIn("background: #2f6f3e", html)
        self.assertIn("Read-only: decide whether to inspect a card or revisit the material", html)
        self.assertIn("Check whether missed cards point to an edit or a study pass", html)
        self.assertNotIn("content patterns", html)
        self.assertNotIn("Review Check", html)
        self.assertNotIn("Recent Debrief", html)

    def test_summary_shows_repeated_miss_count(self) -> None:
        html = deck_button_html(missed_cards=2, lookback_days=90)

        self.assertIn("2 cards needing another pass", html)
        self.assertIn("last 90 days", html)

    def test_summary_handles_zero_repeated_misses(self) -> None:
        html = deck_button_html(missed_cards=0, lookback_days=90)

        self.assertIn("No repeated misses found", html)


if __name__ == "__main__":
    unittest.main()
