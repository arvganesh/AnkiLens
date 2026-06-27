from __future__ import annotations

import unittest

from anki_gateway import load_review_entries
from fake_anki import FakeMainWindow


class AnkiGatewayTest(unittest.TestCase):
    def test_loads_review_entries_from_fake_collection(self) -> None:
        mw = FakeMainWindow(
            rows=[
                (101, 1, 1782432000000, 7, "Aortic regurgitation", "cardiology murmurs"),
                (101, 3, 1782518400000, 7, "Aortic regurgitation", "cardiology murmurs"),
            ],
            deck_names={7: "Cardiology"},
        )

        entries = load_review_entries(mw)

        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].card_id, 101)
        self.assertEqual(entries[0].deck_name, "Cardiology")
        self.assertEqual(entries[0].card_label, "Aortic regurgitation")
        self.assertEqual(entries[0].tags, ("cardiology", "murmurs"))

    def test_uses_calm_unknown_deck_fallback(self) -> None:
        mw = FakeMainWindow(rows=[(202, 1, 1782432000000, 99, "Renal clue", "")], deck_names={})

        entries = load_review_entries(mw)

        self.assertEqual(entries[0].deck_name, "Unknown deck")


if __name__ == "__main__":
    unittest.main()
