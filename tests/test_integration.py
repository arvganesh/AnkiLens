from __future__ import annotations

import unittest

from analytics import summarize_missed_cards
from anki_gateway import load_review_entries
from fake_anki import FakeMainWindow


class GatewayAnalyticsIntegrationTest(unittest.TestCase):
    def test_fake_collection_flows_into_missed_card_summary(self) -> None:
        mw = FakeMainWindow(
            rows=[
                (1, 1, 1782432000000, 1200, 1, 10, 100, 2, 8, 1, 2, 2, "Mitral regurgitation", "cardiology", "Mitral regurgitation"),
                (1, 1, 1782518400000, 1300, 1, 10, 100, 2, 8, 1, 2, 2, "Mitral regurgitation", "cardiology", "Mitral regurgitation"),
                (2, 1, 1782604800000, 900, 1, 11, 200, 1, 2, 0, 1, 1, "Loop diuretics", "renal", "Loop diuretics"),
            ],
            deck_names={10: "Cardiology", 11: "Renal"},
        )

        summaries = summarize_missed_cards(load_review_entries(mw))

        self.assertEqual(len(summaries), 1)
        self.assertEqual(summaries[0].card_label, "Mitral regurgitation")
        self.assertEqual(summaries[0].deck_name, "Cardiology")
        self.assertEqual(summaries[0].note_card_count, 2)
        self.assertEqual(summaries[0].note_repeated_miss_count, 1)


if __name__ == "__main__":
    unittest.main()
