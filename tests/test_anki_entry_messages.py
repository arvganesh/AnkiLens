from __future__ import annotations

import unittest
from datetime import datetime

import anki_entry
from analytics import ReviewLogEntry
from config import BonsaiConfig
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

        self.assertEqual(message, "Opened in Browse. Search copied.")

    def test_browse_message_names_exact_missed_examples(self) -> None:
        message = anki_entry._browse_search_message("cid:10 or cid:11", opened=True)

        self.assertEqual(message, "Opened 2 missed examples in Browse. Search copied.")

    def test_browse_message_names_single_exact_card(self) -> None:
        message = anki_entry._browse_search_message("cid:10", opened=True)

        self.assertEqual(message, "Opened card in Browse. Search copied.")

    def test_browse_message_falls_back_to_copy_instructions(self) -> None:
        message = anki_entry._browse_search_message("tag:cardiology", opened=False)

        self.assertIn("Copied search", message)
        self.assertIn("Open Browse and paste", message)

    def test_browse_message_fallback_names_exact_missed_examples(self) -> None:
        message = anki_entry._browse_search_message("cid:10 or cid:11 or cid:12", opened=False)

        self.assertIn("Copied search for 3 missed examples", message)
        self.assertIn("cid:10 or cid:11 or cid:12", message)
        self.assertIn("Open Browse and paste", message)

    def test_browse_message_fallback_names_single_exact_card(self) -> None:
        message = anki_entry._browse_search_message("cid:10", opened=False)

        self.assertIn("Copied search for this card", message)
        self.assertIn("cid:10", message)
        self.assertIn("Open Browse and paste", message)
        self.assertNotIn("Anki Browse", message)

    def test_exact_card_search_count_rejects_mixed_queries(self) -> None:
        self.assertEqual(anki_entry._exact_card_search_count("cid:10 or tag:cardiology"), 0)

    def test_browser_search_loader_returns_current_search_helper(self) -> None:
        search_helper = anki_entry._load_browser_search_for_study_target()

        self.assertEqual(search_helper("tag", "Cardiology", (10, 11)), "cid:10 or cid:11")

    def test_debrief_entries_use_short_recent_window(self) -> None:
        entries = [
            ReviewLogEntry(1, 1, datetime(2026, 6, 25, 8), "Deck", "Old"),
            ReviewLogEntry(2, 1, datetime(2026, 6, 26, 8), "Deck", "Recent"),
        ]

        filtered = anki_entry._debrief_entries(
            entries,
            BonsaiConfig(lookback_days=90, debrief_lookback_days=1),
            now=datetime(2026, 6, 26, 12),
        )

        self.assertEqual([entry.card_label for entry in filtered], ["Recent"])

    def test_debrief_details_can_use_same_short_window_as_debrief(self) -> None:
        entries = [
            ReviewLogEntry(1, 1, datetime(2026, 3, 26, 8), "Deck", "Stale"),
            ReviewLogEntry(2, 1, datetime(2026, 6, 26, 8), "Deck", "Recent"),
        ]

        filtered = anki_entry._analytics_entries(
            entries,
            lookback_days=1,
            now=datetime(2026, 6, 26, 12),
        )

        self.assertEqual([entry.card_label for entry in filtered], ["Recent"])

    def test_debrief_loader_refreshes_dialog_dependencies_first(self) -> None:
        self.assertEqual(
            anki_entry._debrief_dialog_module_names("bonsai"),
            (
                "bonsai.debrief_dialog_copy",
                "bonsai.copy_text",
                "bonsai.session_context",
                "bonsai.ui_helpers",
                "bonsai.dialog_actions",
                "bonsai.debrief_dialog",
            ),
        )

    def test_debrief_loader_refreshes_model_dependencies_first(self) -> None:
        self.assertEqual(
            anki_entry._debrief_model_module_names("bonsai"),
            (
                "bonsai.content_signals",
                "bonsai.terms",
                "bonsai.analytics",
                "bonsai.debrief",
            ),
        )

    def test_deck_button_loader_refreshes_copy_before_button_html(self) -> None:
        self.assertEqual(
            anki_entry._deck_button_module_names("bonsai"),
            (
                "bonsai.debrief_dialog_copy",
                "bonsai.deck_button",
            ),
        )

    def test_broad_analytics_can_still_use_configured_long_window(self) -> None:
        entries = [
            ReviewLogEntry(1, 1, datetime(2026, 4, 26, 8), "Deck", "Stale"),
            ReviewLogEntry(2, 1, datetime(2026, 6, 26, 8), "Deck", "Recent"),
        ]

        filtered = anki_entry._analytics_entries(
            entries,
            lookback_days=90,
            now=datetime(2026, 6, 26, 12),
        )

        self.assertEqual([entry.card_label for entry in filtered], ["Stale", "Recent"])


if __name__ == "__main__":
    unittest.main()
