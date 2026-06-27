from __future__ import annotations

import unittest
from datetime import datetime

from analytics import ReviewLogEntry, summarize_missed_cards, summarize_terms
from terms import frequent_terms


class TermsTest(unittest.TestCase):
    def test_extracts_frequent_terms_without_stopwords(self) -> None:
        terms = frequent_terms(["Mitral regurgitation murmur", "mitral valve murmur"])

        self.assertEqual(terms[:2], [("mitral", 2), ("murmur", 2)])

    def test_ignores_terms_seen_on_only_one_card(self) -> None:
        terms = frequent_terms(["Mitral regurgitation murmur", "aortic stenosis"])

        self.assertEqual(terms, [])

    def test_ignores_short_scaffolding_terms_but_keeps_acronyms(self) -> None:
        terms = frequent_terms(["Bro test card ACE", "Bro front deck ACE"])

        self.assertEqual(terms, [("ace", 2)])

    def test_summarizes_terms_from_missed_cards(self) -> None:
        summaries = summarize_missed_cards(
            [
                ReviewLogEntry(1, 1, datetime(2026, 6, 1), "Deck", "Card", source_text="mitral murmur"),
                ReviewLogEntry(1, 1, datetime(2026, 6, 2), "Deck", "Card", source_text="mitral murmur"),
                ReviewLogEntry(2, 1, datetime(2026, 6, 1), "Deck", "Card", source_text="mitral valve"),
                ReviewLogEntry(2, 1, datetime(2026, 6, 2), "Deck", "Card", source_text="mitral valve"),
            ]
        )

        self.assertIn(("mitral", 2), summarize_terms(summaries))


if __name__ == "__main__":
    unittest.main()
