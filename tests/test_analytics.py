from __future__ import annotations

import unittest
from datetime import datetime

from analytics import (
    ReviewLogEntry,
    filter_review_entries_by_lookback,
    summarize_missed_cards,
    summarize_tag_misses,
)


def _entry(card_id: int, ease: int, day: int) -> ReviewLogEntry:
    return ReviewLogEntry(
        card_id=card_id,
        ease=ease,
        reviewed_at=datetime(2026, 6, day),
        deck_name="Cardiology",
        card_label=f"Card {card_id}",
    )


def _note_entry(card_id: int, note_id: int, ease: int, day: int, *, note_card_count: int = 3) -> ReviewLogEntry:
    return ReviewLogEntry(
        card_id=card_id,
        ease=ease,
        reviewed_at=datetime(2026, 6, day),
        deck_name="Cardiology",
        card_label=f"Card {card_id}",
        note_id=note_id,
        note_card_count=note_card_count,
    )


def _lifecycle_entry(
    card_id: int,
    ease: int,
    day: int,
    *,
    card_reps: int | None,
    card_lapses: int | None = None,
    review_type: int = 1,
) -> ReviewLogEntry:
    return ReviewLogEntry(
        card_id=card_id,
        ease=ease,
        reviewed_at=datetime(2026, 6, day),
        deck_name="Cardiology",
        card_label=f"Card {card_id}",
        review_type=review_type,
        card_reps=card_reps,
        card_lapses=card_lapses,
        source_text="weak cue",
    )


def _tagged_entry(card_id: int, ease: int, day: int, *tags: str) -> ReviewLogEntry:
    return ReviewLogEntry(
        card_id=card_id,
        ease=ease,
        reviewed_at=datetime(2026, 6, day),
        deck_name="Cardiology",
        card_label=f"Card {card_id}",
        tags=tags,
    )


class MissedCardAnalyticsTest(unittest.TestCase):
    def test_ignores_isolated_misses_by_default(self) -> None:
        summaries = summarize_missed_cards([_entry(1, 1, 1), _entry(2, 3, 2)])

        self.assertEqual(summaries, [])

    def test_summarizes_cards_with_repeated_misses(self) -> None:
        summaries = summarize_missed_cards(
            [
                _entry(1, 1, 1),
                _entry(1, 3, 2),
                _entry(1, 1, 3),
                _entry(2, 1, 4),
            ]
        )

        self.assertEqual(len(summaries), 1)
        self.assertEqual(summaries[0].card_id, 1)
        self.assertEqual(summaries[0].misses, 2)
        self.assertEqual(summaries[0].total_reviews, 3)

    def test_prioritizes_high_miss_rate_and_applies_limit(self) -> None:
        summaries = summarize_missed_cards(
            [
                _entry(1, 1, 1),
                _entry(1, 1, 2),
                _entry(1, 3, 3),
                _entry(2, 1, 1),
                _entry(2, 1, 2),
            ],
            limit=1,
        )

        self.assertEqual([summary.card_id for summary in summaries], [2])

    def test_allows_lower_miss_threshold(self) -> None:
        summaries = summarize_missed_cards([_entry(1, 1, 1)], minimum_misses=1)

        self.assertEqual(len(summaries), 1)

    def test_counts_repeated_miss_siblings_from_same_note(self) -> None:
        summaries = summarize_missed_cards(
            [
                _note_entry(1, 500, 1, 1),
                _note_entry(1, 500, 1, 2),
                _note_entry(2, 500, 1, 3),
                _note_entry(2, 500, 1, 4),
                _note_entry(3, 500, 3, 5),
            ]
        )

        self.assertEqual({summary.card_id: summary.note_repeated_miss_count for summary in summaries}, {1: 2, 2: 2})
        self.assertEqual(summaries[0].note_card_count, 3)

    def test_marks_low_repetition_all_again_cards_as_early_exposure(self) -> None:
        summaries = summarize_missed_cards(
            [
                _lifecycle_entry(1, 1, 1, card_reps=2),
                _lifecycle_entry(1, 1, 2, card_reps=2),
            ]
        )

        self.assertTrue(summaries[0].is_early_exposure)
        self.assertEqual(summaries[0].card_reps, 2)
        self.assertEqual(summaries[0].first_reviewed_at, datetime(2026, 6, 1))
        self.assertEqual(summaries[0].learning_review_count, 2)

    def test_lapsed_or_mature_cards_are_not_early_exposure(self) -> None:
        summaries = summarize_missed_cards(
            [
                _lifecycle_entry(1, 1, 1, card_reps=2, card_lapses=1),
                _lifecycle_entry(1, 1, 2, card_reps=2, card_lapses=1),
                _lifecycle_entry(2, 1, 1, card_reps=20),
                _lifecycle_entry(2, 1, 2, card_reps=20),
            ]
        )

        self.assertFalse(any(summary.is_early_exposure for summary in summaries))

    def test_filters_reviews_by_recent_window(self) -> None:
        entries = [_entry(1, 1, 1), _entry(2, 1, 20)]

        filtered = filter_review_entries_by_lookback(
            entries,
            lookback_days=7,
            now=datetime(2026, 6, 21),
        )

        self.assertEqual([entry.card_id for entry in filtered], [2])

    def test_summarizes_tag_miss_concentration(self) -> None:
        missed_cards = summarize_missed_cards(
            [
                _tagged_entry(1, 1, 1, "cardiology", "murmurs"),
                _tagged_entry(1, 1, 2, "cardiology", "murmurs"),
                _tagged_entry(2, 1, 3, "cardiology"),
                _tagged_entry(2, 1, 4, "cardiology"),
            ]
        )

        tags = summarize_tag_misses(missed_cards)

        self.assertEqual(tags[0].tag, "cardiology")
        self.assertEqual(tags[0].missed_cards, 2)
        self.assertEqual(tags[0].misses, 4)


if __name__ == "__main__":
    unittest.main()
