from __future__ import annotations

import unittest

from anki_browser import browser_search_for_cards, open_browser_search


class AnkiBrowserTest(unittest.TestCase):
    def test_builds_exact_card_search(self) -> None:
        self.assertEqual(browser_search_for_cards((123, 456, 123)), "cid:123 or cid:456")

    def test_opens_browser_with_exact_search(self) -> None:
        calls = []

        def dialog_open(*args, **kwargs):
            calls.append((args, kwargs))
            return "browser"

        browser = open_browser_search("mw", "cid:123", dialog_open=dialog_open)

        self.assertEqual(browser, "browser")
        self.assertEqual(calls, [(("Browser", "mw"), {"search": ("cid:123",)})])


if __name__ == "__main__":
    unittest.main()
