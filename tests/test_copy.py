from __future__ import annotations

import unittest

from copy_text import analytics_caption


class AnalyticsCopyTest(unittest.TestCase):
    def test_empty_caption_mentions_threshold(self) -> None:
        caption = analytics_caption(shown_count=0, minimum_misses=3, result_limit=20)

        self.assertIn("No repeated misses found yet", caption)
        self.assertIn("at least 3 times", caption)

    def test_result_caption_mentions_count_threshold_and_limit(self) -> None:
        caption = analytics_caption(shown_count=2, minimum_misses=2, result_limit=10)

        self.assertIn("Showing 2 cards", caption)
        self.assertIn("at least 2 times", caption)
        self.assertIn("Limit: 10", caption)


if __name__ == "__main__":
    unittest.main()
