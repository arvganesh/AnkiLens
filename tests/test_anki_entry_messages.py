from __future__ import annotations

import unittest

import anki_entry
from deck_button import BUTTON_MESSAGE, DEBRIEF_MESSAGE


class AnkiEntryMessagesTest(unittest.TestCase):
    def test_handles_bonsai_open_message(self) -> None:
        calls = []
        original = anki_entry.show_missed_card_analytics
        anki_entry.show_missed_card_analytics = lambda: calls.append("analytics")
        try:
            handled = anki_entry._handle_js_message((False, None), BUTTON_MESSAGE, None)
        finally:
            anki_entry.show_missed_card_analytics = original

        self.assertEqual(handled, (True, None))
        self.assertEqual(calls, ["analytics"])

    def test_handles_debrief_message(self) -> None:
        calls = []
        original = anki_entry.show_session_debrief
        anki_entry.show_session_debrief = lambda: calls.append("debrief")
        try:
            handled = anki_entry._handle_js_message((False, None), DEBRIEF_MESSAGE, None)
        finally:
            anki_entry.show_session_debrief = original

        self.assertEqual(handled, (True, None))
        self.assertEqual(calls, ["debrief"])

    def test_ignores_other_messages(self) -> None:
        self.assertEqual(anki_entry._handle_js_message((False, None), "other", None), (False, None))

    def test_browse_message_reflects_opened_search(self) -> None:
        message = anki_entry._browse_search_message("tag:cardiology", opened=True)

        self.assertIn("Opened Anki Browse", message)
        self.assertIn("tag:cardiology", message)
        self.assertIn("also copied", message)

    def test_browse_message_falls_back_to_copy_instructions(self) -> None:
        message = anki_entry._browse_search_message("tag:cardiology", opened=False)

        self.assertIn("Copied search", message)
        self.assertIn("Open Browse and paste", message)


if __name__ == "__main__":
    unittest.main()
