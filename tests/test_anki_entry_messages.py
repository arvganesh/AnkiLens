from __future__ import annotations

import sys
import types
import unittest
from datetime import datetime

import anki_entry
from analytics import ReviewLogEntry
from config import AnkiLensConfig


class AnkiEntryMessagesTest(unittest.TestCase):
    def test_adds_insights_top_toolbar_tab(self) -> None:
        links = []
        calls = []

        class FakeToolbar:
            def create_link(self, cmd, label, func, tip=None, id=None):
                calls.append((cmd, label, func, tip, id))
                return f"link:{label}"

        anki_entry._add_top_toolbar_link(links, FakeToolbar())

        self.assertEqual(links, ["link:Insights"])
        self.assertEqual(calls[0][0], "ankilens")
        self.assertEqual(calls[0][1], "Insights")
        self.assertIs(calls[0][2], anki_entry.show_ankilens_page)
        self.assertEqual(calls[0][3], "Analyze missed cards")
        self.assertEqual(calls[0][4], "ankilens-top-tab")

    def test_handles_deck_scope_message(self) -> None:
        original_deck = anki_entry._selected_deck_name
        original_show_ankilens_page = anki_entry.show_ankilens_page
        calls = []
        anki_entry.show_ankilens_page = lambda: calls.append("page")
        try:
            handled = anki_entry._handle_js_message(
                (False, None),
                f"{anki_entry.DECK_SCOPE_MESSAGE_PREFIX}Cardiology%20Deck",
                None,
            )

            self.assertEqual(handled, (True, None))
            self.assertEqual(anki_entry._selected_deck_name, "Cardiology Deck")
            self.assertEqual(calls, ["page"])
        finally:
            anki_entry._selected_deck_name = original_deck
            anki_entry.show_ankilens_page = original_show_ankilens_page

    def test_handles_lookback_scope_message(self) -> None:
        original_lookback = anki_entry._selected_lookback_days
        original_show_ankilens_page = anki_entry.show_ankilens_page
        calls = []
        anki_entry.show_ankilens_page = lambda: calls.append("page")
        try:
            handled = anki_entry._handle_js_message(
                (False, None),
                f"{anki_entry.LOOKBACK_SCOPE_MESSAGE_PREFIX}30",
                None,
            )

            self.assertEqual(handled, (True, None))
            self.assertEqual(anki_entry._selected_lookback_days, 30)
            self.assertEqual(calls, ["page"])
        finally:
            anki_entry._selected_lookback_days = original_lookback
            anki_entry.show_ankilens_page = original_show_ankilens_page

    def test_handles_browse_search_message(self) -> None:
        original_open_search = anki_entry._open_search_from_debrief
        calls = []
        anki_entry._open_search_from_debrief = lambda query: calls.append(query)
        try:
            handled = anki_entry._handle_js_message(
                (False, None),
                f"{anki_entry.BROWSE_SEARCH_MESSAGE_PREFIX}cid%3A10%20or%20cid%3A11",
                None,
            )
        finally:
            anki_entry._open_search_from_debrief = original_open_search

        self.assertEqual(handled, (True, None))
        self.assertEqual(calls, ["cid:10 or cid:11"])

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
            AnkiLensConfig(lookback_days=90, debrief_lookback_days=1),
            now=datetime(2026, 6, 26, 12),
        )

        self.assertEqual([entry.card_label for entry in filtered], ["Recent"])

    def test_llm_summary_attach_is_skipped_when_disabled(self) -> None:
        calls = []
        dialog = types.SimpleNamespace(set_llm_summary=lambda summary: calls.append(summary))

        anki_entry._attach_llm_summary(dialog, [], AnkiLensConfig(llm_summary_enabled=False))

        self.assertEqual(calls, [])
        self.assertFalse(hasattr(dialog, "_ankilens_llm_thread"))

    def test_llm_summary_attach_starts_background_worker(self) -> None:
        original_loader = anki_entry._load_llm_summary_builder
        original_aqt = sys.modules.get("aqt")
        original_aqt_qt = sys.modules.get("aqt.qt")
        calls = []
        threads = []

        class FakeSignal:
            def __init__(self) -> None:
                self.callback = None

            def connect(self, callback) -> None:
                self.callback = callback

            def emit(self, value) -> None:
                self.callback(value)

        class FakeNotifier:
            summary_ready = None

            def __init__(self, _parent) -> None:
                self.summary_ready = FakeSignal()

        class FakeThread:
            def __init__(self, *, target, daemon) -> None:
                self.target = target
                self.daemon = daemon
                threads.append(self)

            def start(self) -> None:
                self.target()

        sys.modules["aqt"] = types.ModuleType("aqt")
        sys.modules["aqt.qt"] = types.SimpleNamespace(QObject=FakeNotifier, pyqtSignal=lambda _type: FakeSignal())
        anki_entry._load_llm_summary_builder = lambda: (lambda _entries, _config: "summary")
        original_thread = anki_entry.threading.Thread
        anki_entry.threading.Thread = FakeThread
        dialog = types.SimpleNamespace(set_llm_summary=lambda summary: calls.append(summary))
        try:
            anki_entry._attach_llm_summary(dialog, [], AnkiLensConfig(llm_summary_enabled=True))
        finally:
            anki_entry._load_llm_summary_builder = original_loader
            anki_entry.threading.Thread = original_thread
            if original_aqt is None:
                sys.modules.pop("aqt", None)
            else:
                sys.modules["aqt"] = original_aqt
            if original_aqt_qt is None:
                sys.modules.pop("aqt.qt", None)
            else:
                sys.modules["aqt.qt"] = original_aqt_qt

        self.assertEqual(calls, ["summary"])
        self.assertEqual(len(threads), 1)
        self.assertTrue(threads[0].daemon)

    def test_page_llm_summary_ignores_stale_worker_result(self) -> None:
        original_page_loader = anki_entry._load_debrief_page_module
        original_worker = anki_entry._start_llm_summary_worker
        callbacks = []
        evals = []

        class FakePage:
            @staticmethod
            def llm_summary_update_js(summary, _evidence=None, *, grounding=""):
                return f"summary:{summary}:{grounding}"

            @staticmethod
            def llm_summary_status_update_js(message, _evidence=None, *, grounding=""):
                return f"status:{message}"

        web = types.SimpleNamespace(eval=lambda js: evals.append(js))

        def fake_worker(_web, _entries, _config, callback) -> None:
            callbacks.append(callback)

        anki_entry._load_debrief_page_module = lambda: FakePage
        anki_entry._start_llm_summary_worker = fake_worker
        try:
            anki_entry._attach_llm_summary_to_page(web, ["old"], AnkiLensConfig(llm_summary_enabled=True))
            anki_entry._attach_llm_summary_to_page(
                web,
                ["current"],
                AnkiLensConfig(llm_summary_enabled=True),
                grounding="current scope",
            )

            callbacks[0]("old result")
            callbacks[1]("current result")
        finally:
            anki_entry._load_debrief_page_module = original_page_loader
            anki_entry._start_llm_summary_worker = original_worker

        self.assertEqual(evals, ["summary:current result:current scope"])

    def test_deck_panel_count_uses_all_repeated_misses_not_display_cap(self) -> None:
        entries = []
        for card_id in range(1, 26):
            entries.extend(
                (
                    ReviewLogEntry(card_id, 1, datetime(2026, 6, 26, 8), "Deck", f"Card {card_id}"),
                    ReviewLogEntry(card_id, 1, datetime(2026, 6, 26, 9), "Deck", f"Card {card_id}"),
                )
            )

        missed_count = anki_entry._missed_card_count(
            entries,
            AnkiLensConfig(minimum_misses=2, result_limit=20),
        )

        self.assertEqual(missed_count, 25)

    def test_loader_appends_demo_entries_only_when_enabled(self) -> None:
        original_loader = anki_entry.load_review_entries
        original_demo_builder = anki_entry.build_demo_review_entries
        real_entry = ReviewLogEntry(1, 3, datetime(2026, 6, 26, 8), "Real", "Real card")
        demo_entry = ReviewLogEntry(2, 1, datetime(2026, 6, 26, 9), "Demo", "Demo card")
        try:
            anki_entry.load_review_entries = lambda _mw: [real_entry]
            anki_entry.build_demo_review_entries = lambda _now: [demo_entry]

            without_demo = anki_entry._load_review_entries(
                object(),
                AnkiLensConfig(demo_data_enabled=False),
                now=datetime(2026, 6, 26, 12),
            )
            with_demo = anki_entry._load_review_entries(
                object(),
                AnkiLensConfig(demo_data_enabled=True),
                now=datetime(2026, 6, 26, 12),
            )
        finally:
            anki_entry.load_review_entries = original_loader
            anki_entry.build_demo_review_entries = original_demo_builder

        self.assertEqual(without_demo, [real_entry])
        self.assertEqual(with_demo, [real_entry, demo_entry])

    def test_filters_entries_by_selected_deck(self) -> None:
        entries = [
            ReviewLogEntry(1, 1, datetime(2026, 6, 26, 8), "Cardiology", "Cardiology card"),
            ReviewLogEntry(2, 1, datetime(2026, 6, 26, 9), "Renal", "Renal card"),
        ]

        filtered = anki_entry._filter_entries_by_deck(entries, "Renal")

        self.assertEqual([entry.card_label for entry in filtered], ["Renal card"])

    def test_deck_options_are_sorted_unique_deck_names(self) -> None:
        entries = [
            ReviewLogEntry(1, 1, datetime(2026, 6, 26, 8), "Renal", "Renal one"),
            ReviewLogEntry(2, 1, datetime(2026, 6, 26, 9), "Cardiology", "Cardiology"),
            ReviewLogEntry(3, 1, datetime(2026, 6, 26, 10), "Renal", "Renal two"),
        ]

        self.assertEqual(anki_entry._deck_options(entries), ("Cardiology", "Renal"))

    def test_invalid_selected_deck_falls_back_to_first_deck(self) -> None:
        original_deck = anki_entry._selected_deck_name
        try:
            anki_entry._selected_deck_name = "Missing"

            self.assertEqual(anki_entry._valid_selected_deck(("Cardiology", "Renal")), "Cardiology")
        finally:
            anki_entry._selected_deck_name = original_deck

    def test_missing_deck_options_have_no_selected_deck(self) -> None:
        self.assertIsNone(anki_entry._valid_selected_deck(()))

    def test_selected_lookback_falls_back_to_config_or_thirty_days(self) -> None:
        original_lookback = anki_entry._selected_lookback_days
        try:
            anki_entry._selected_lookback_days = 7
            self.assertEqual(anki_entry._valid_selected_lookback(90), 7)

            anki_entry._selected_lookback_days = None
            self.assertEqual(anki_entry._valid_selected_lookback(90), 90)
            self.assertEqual(anki_entry._valid_selected_lookback(14), 30)
        finally:
            anki_entry._selected_lookback_days = original_lookback

    def test_deck_display_label_shortens_nested_decks(self) -> None:
        self.assertEqual(
            anki_entry._deck_display_label("Zanki Step Decks::Zanki Biochemistry::Metabolism"),
            "Zanki Biochemistry / Metabolism",
        )

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
            anki_entry._debrief_dialog_module_names("ankilens"),
            (
                "ankilens.debrief_dialog_copy",
                "ankilens.copy_text",
                "ankilens.session_context",
                "ankilens.ui_helpers",
                "ankilens.dialog_actions",
                "ankilens.debrief_dialog",
            ),
        )

    def test_debrief_loader_refreshes_model_dependencies_first(self) -> None:
        self.assertEqual(
            anki_entry._debrief_model_module_names("ankilens"),
            (
                "ankilens.content_signals",
                "ankilens.terms",
                "ankilens.analytics",
                "ankilens.debrief",
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
