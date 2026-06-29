from __future__ import annotations

import unittest
from datetime import datetime

from analytics import AGAIN_EASE, HARD_EASE, ReviewLogEntry
from debrief import build_debrief_evidence


def _entry(card_id: int, ease: int) -> ReviewLogEntry:
    return ReviewLogEntry(
        card_id=card_id,
        ease=ease,
        reviewed_at=datetime(2026, 6, 26),
        deck_name="Deck",
        card_label=f"Card {card_id}",
    )


class DebriefEvidenceTest(unittest.TestCase):
    def test_can_count_hard_reviews_as_misses(self) -> None:
        entries = [_entry(1, AGAIN_EASE), _entry(2, HARD_EASE), _entry(3, 3)]

        default = build_debrief_evidence(entries)
        expanded = build_debrief_evidence(entries, miss_eases=(AGAIN_EASE, HARD_EASE))

        self.assertEqual(default.missed_cards, 1)
        self.assertEqual(default.misses, 1)
        self.assertEqual(expanded.missed_cards, 2)
        self.assertEqual(expanded.misses, 2)


if __name__ == "__main__":
    unittest.main()
