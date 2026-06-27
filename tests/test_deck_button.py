from __future__ import annotations

import unittest

from deck_button import BUTTON_MESSAGE, deck_button_html


class DeckButtonTest(unittest.TestCase):
    def test_button_sends_bonsai_open_message(self) -> None:
        html = deck_button_html()

        self.assertIn(BUTTON_MESSAGE, html)
        self.assertIn("Open Bonsai", html)


if __name__ == "__main__":
    unittest.main()
