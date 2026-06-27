from __future__ import annotations

import unittest

from deck_button import BUTTON_MESSAGE, DEBRIEF_MESSAGE, DECK_SCOPE_MESSAGE_PREFIX, deck_button_html


class DeckButtonTest(unittest.TestCase):
    def test_panel_prioritizes_next_check_only(self) -> None:
        html = deck_button_html()

        self.assertNotIn(BUTTON_MESSAGE, html)
        self.assertNotIn("See supporting cards", html)
        self.assertNotIn("Review evidence", html)
        self.assertIn(DEBRIEF_MESSAGE, html)
        self.assertIn("Analyze missed cards", html)
        self.assertIn("background: #2f6f3e", html)
        self.assertIn("Read-only: decide whether a missed card needs editing or more review", html)
        self.assertIn("Analyze missed cards for possible edits or study follow-up", html)
        self.assertNotIn("content patterns", html)
        self.assertNotIn("Review Check", html)
        self.assertNotIn("Recent Debrief", html)

    def test_summary_shows_repeated_miss_count(self) -> None:
        html = deck_button_html(missed_cards=2, lookback_days=90)

        self.assertIn("2 cards needed another pass", html)
        self.assertIn("last 90 days", html)

    def test_panel_can_select_deck_scope(self) -> None:
        html = deck_button_html(
            missed_cards=2,
            lookback_days=90,
            deck_options=("Cardiology", "Renal"),
            selected_deck="Renal",
        )

        self.assertIn("<select", html)
        self.assertIn(DECK_SCOPE_MESSAGE_PREFIX, html)
        self.assertIn("All decks", html)
        self.assertIn('<option value="Renal" selected title="Renal">Renal</option>', html)
        self.assertIn("2 cards needed another pass in Renal", html)

    def test_panel_shortens_long_subdeck_labels(self) -> None:
        html = deck_button_html(
            missed_cards=0,
            lookback_days=90,
            deck_options=("Zanki Step Decks::Zanki Biochemistry::Metabolism",),
            selected_deck="Zanki Step Decks::Zanki Biochemistry::Metabolism",
        )

        self.assertIn("No repeated misses found in Zanki Biochemistry / Metabolism", html)
        self.assertIn('value="Zanki Step Decks::Zanki Biochemistry::Metabolism"', html)
        self.assertIn(">Zanki Biochemistry / Metabolism</option>", html)

    def test_summary_handles_zero_repeated_misses(self) -> None:
        html = deck_button_html(missed_cards=0, lookback_days=90)

        self.assertIn("No repeated misses found", html)


if __name__ == "__main__":
    unittest.main()
