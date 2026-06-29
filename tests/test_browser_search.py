from __future__ import annotations

import unittest

from browser_search import browser_search_for_card, browser_search_for_study_target


class BrowserSearchTest(unittest.TestCase):
    def test_builds_card_search_query(self) -> None:
        self.assertEqual(browser_search_for_card(123), "cid:123")

    def test_builds_representative_target_queries(self) -> None:
        self.assertEqual(
            browser_search_for_study_target("tag", "AnKing_Cardiology_Valves"),
            "tag:AnKing_Cardiology_Valves -is:suspended",
        )
        self.assertEqual(browser_search_for_study_target("deck", "Test Deck"), 'deck:"Test Deck"')
        self.assertEqual(browser_search_for_study_target("term", "mitral"), "w:mitral")
        self.assertEqual(browser_search_for_study_target("tag", '-needs "work"'), 'tag:"-needs \\"work\\"" -is:suspended')

    def test_prefers_missed_example_card_ids_when_available(self) -> None:
        self.assertEqual(
            browser_search_for_study_target("tag", "AnKing_Cardiology_Valves", (123, 456)),
            "cid:123 or cid:456",
        )

if __name__ == "__main__":
    unittest.main()
