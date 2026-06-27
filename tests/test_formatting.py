from __future__ import annotations

import unittest
from datetime import datetime

from formatting import format_review_date


class FormattingTest(unittest.TestCase):
    def test_formats_review_date(self) -> None:
        self.assertEqual(format_review_date(datetime(2026, 6, 26, 15, 4)), "2026-06-26")

    def test_formats_missing_review_date(self) -> None:
        self.assertEqual(format_review_date(None), "Not yet")


if __name__ == "__main__":
    unittest.main()
