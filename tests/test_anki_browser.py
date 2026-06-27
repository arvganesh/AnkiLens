from __future__ import annotations

import unittest

from anki_browser import open_browser_search


class AnkiBrowserTest(unittest.TestCase):
    def test_opens_browser_with_exact_search(self) -> None:
        calls = []
        browser = FakeBrowser(calls)

        def dialog_open(*args, **kwargs):
            calls.append((args, kwargs))
            return browser

        open_browser_search("mw", "cid:123", dialog_open=dialog_open)

        self.assertEqual(calls, [(("Browser", "mw"), {})])
        self.assertEqual(browser.searches, ["cid:123"])
        self.assertTrue(browser.raised)
        self.assertTrue(browser.activated)


class FakeBrowser:
    def __init__(self, calls) -> None:
        self.calls = calls
        self.searches = []
        self.raised = False
        self.activated = False

    def search_for(self, query: str) -> None:
        self.searches.append(query)

    def raise_(self) -> None:
        self.raised = True

    def activateWindow(self) -> None:
        self.activated = True


if __name__ == "__main__":
    unittest.main()
