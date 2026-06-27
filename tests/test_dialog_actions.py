from __future__ import annotations

import unittest

from dialog_actions import accept_then


class FakeDialog:
    def __init__(self) -> None:
        self.accepted = False

    def accept(self) -> None:
        self.accepted = True


class DialogActionsTest(unittest.TestCase):
    def test_accept_then_closes_dialog_before_callback(self) -> None:
        events = []
        dialog = FakeDialog()

        accept_then(dialog, lambda: events.append(("callback", dialog.accepted)))

        self.assertTrue(dialog.accepted)
        self.assertEqual(events, [("callback", True)])


if __name__ == "__main__":
    unittest.main()
