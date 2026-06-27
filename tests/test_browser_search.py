from __future__ import annotations

import unittest

from browser_search import browser_search_for_card


class BrowserSearchTest(unittest.TestCase):
    def test_builds_card_search_query(self) -> None:
        self.assertEqual(browser_search_for_card(123), "cid:123")


if __name__ == "__main__":
    unittest.main()
