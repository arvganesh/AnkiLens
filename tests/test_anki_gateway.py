from __future__ import annotations

import unittest

from anki_gateway import load_review_entries
from fake_anki import FakeMainWindow


class AnkiGatewayTest(unittest.TestCase):
    def test_loads_review_entries_from_fake_collection(self) -> None:
        mw = FakeMainWindow(
            rows=[
                (
                    101,
                    1,
                    1782432000000,
                    3200,
                    1,
                    7,
                    12,
                    2,
                    2,
                    2,
                    "Aortic regurgitation",
                    "cardiology murmurs",
                    "Aortic<br>regurgitation\x1fWide pulse pressure",
                ),
                (
                    101,
                    3,
                    1782518400000,
                    2100,
                    1,
                    7,
                    12,
                    2,
                    2,
                    2,
                    "Aortic regurgitation",
                    "cardiology murmurs",
                    "Aortic<br>regurgitation\x1fWide pulse pressure",
                ),
            ],
            deck_names={7: "Cardiology"},
        )

        entries = load_review_entries(mw)

        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].card_id, 101)
        self.assertEqual(entries[0].deck_name, "Cardiology")
        self.assertEqual(entries[0].card_label, "Aortic regurgitation")
        self.assertEqual(entries[0].tags, ("cardiology", "murmurs"))
        self.assertEqual(entries[0].source_text, "Aortic regurgitation Wide pulse pressure")
        self.assertEqual(entries[0].duration_ms, 3200)
        self.assertEqual(entries[0].review_type, 1)
        self.assertEqual(entries[0].card_reps, 12)
        self.assertEqual(entries[0].card_lapses, 2)
        self.assertEqual(entries[0].card_type, 2)
        self.assertEqual(entries[0].card_queue, 2)

    def test_uses_calm_unknown_deck_fallback(self) -> None:
        mw = FakeMainWindow(
            rows=[(202, 1, 1782432000000, 1500, 1, 99, 2, 0, 1, 1, "Renal clue", "", "Renal clue")],
            deck_names={},
        )

        entries = load_review_entries(mw)

        self.assertEqual(entries[0].deck_name, "Unknown deck")


if __name__ == "__main__":
    unittest.main()
