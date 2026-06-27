from __future__ import annotations

import unittest

from browser_actions import open_card_in_browser


class FakeCollection:
    def get_card(self, card_id: int) -> str:
        return f"card:{card_id}"


class FakeMainWindow:
    def __init__(self) -> None:
        self.col = FakeCollection()


class FakeDialogs:
    def __init__(self) -> None:
        self.calls = []

    def open(self, *args, **kwargs) -> str:
        self.calls.append((args, kwargs))
        return "browser"


class BrowserActionsTest(unittest.TestCase):
    def test_opens_browser_with_card(self) -> None:
        dialogs = FakeDialogs()

        result = open_card_in_browser(FakeMainWindow(), 123, dialogs)

        self.assertEqual(result, "browser")
        self.assertEqual(dialogs.calls[0][0][0], "Browser")
        self.assertEqual(dialogs.calls[0][1]["card"], "card:123")


if __name__ == "__main__":
    unittest.main()
