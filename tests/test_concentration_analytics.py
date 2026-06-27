from __future__ import annotations

import unittest
from datetime import datetime

from analytics import (
    ReviewLogEntry,
    summarize_deck_misses,
    summarize_missed_cards,
    summarize_note_type_misses,
    summarize_tag_misses,
)


def _entry(card_id: int, ease: int, day: int, deck_name: str = "Cardiology") -> ReviewLogEntry:
    return ReviewLogEntry(card_id, ease, datetime(2026, 6, day), deck_name, f"Card {card_id}")


class ConcentrationAnalyticsTest(unittest.TestCase):
    def test_summarizes_deck_miss_concentration(self) -> None:
        missed_cards = summarize_missed_cards(
            [
                _entry(1, 1, 1),
                _entry(1, 1, 2),
                _entry(2, 1, 3),
                _entry(2, 1, 4),
                _entry(3, 1, 5, "Renal"),
                _entry(3, 1, 6, "Renal"),
                _entry(3, 1, 7, "Renal"),
            ]
        )

        decks = summarize_deck_misses(missed_cards)

        self.assertEqual(decks[0].deck_name, "Cardiology")
        self.assertEqual(decks[0].missed_cards, 2)
        self.assertEqual(decks[0].misses, 4)

    def test_summarizes_tag_miss_concentration(self) -> None:
        missed_cards = summarize_missed_cards(
            [
                ReviewLogEntry(1, 1, datetime(2026, 6, 1), "Deck", "Card 1", ("cardiology", "murmurs")),
                ReviewLogEntry(1, 1, datetime(2026, 6, 2), "Deck", "Card 1", ("cardiology", "murmurs")),
                ReviewLogEntry(2, 1, datetime(2026, 6, 3), "Deck", "Card 2", ("cardiology",)),
                ReviewLogEntry(2, 1, datetime(2026, 6, 4), "Deck", "Card 2", ("cardiology",)),
            ]
        )

        tags = summarize_tag_misses(missed_cards)

        self.assertEqual(tags[0].tag, "cardiology")
        self.assertEqual(tags[0].missed_cards, 2)
        self.assertEqual(tags[0].misses, 4)

    def test_summarizes_note_type_miss_concentration(self) -> None:
        missed_cards = summarize_missed_cards(
            [
                ReviewLogEntry(1, 1, datetime(2026, 6, 1), "Deck", "Card 1", note_type="Cloze"),
                ReviewLogEntry(1, 1, datetime(2026, 6, 2), "Deck", "Card 1", note_type="Cloze"),
                ReviewLogEntry(2, 1, datetime(2026, 6, 3), "Deck", "Card 2", note_type="Basic"),
                ReviewLogEntry(2, 1, datetime(2026, 6, 4), "Deck", "Card 2", note_type="Basic"),
                ReviewLogEntry(2, 1, datetime(2026, 6, 5), "Deck", "Card 2", note_type="Basic"),
            ]
        )

        note_types = summarize_note_type_misses(missed_cards)

        self.assertEqual(note_types[0].note_type, "Basic")
        self.assertEqual(note_types[0].misses, 3)


if __name__ == "__main__":
    unittest.main()
