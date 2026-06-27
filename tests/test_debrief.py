from __future__ import annotations

import unittest
from datetime import datetime

from analytics import ReviewLogEntry
from debrief import build_debrief


def _entry(
    card_id: int,
    ease: int,
    minute: int,
    *,
    deck: str = "Cardiology",
    text: str = "mitral murmur",
    tags: tuple[str, ...] = (),
    duration_ms: int | None = None,
    label: str | None = None,
) -> ReviewLogEntry:
    return ReviewLogEntry(
        card_id=card_id,
        ease=ease,
        reviewed_at=datetime(2026, 6, 26, 9, minute),
        deck_name=deck,
        card_label=label or f"Card {card_id}",
        tags=tags,
        source_text=text,
        duration_ms=duration_ms,
    )


class DebriefTest(unittest.TestCase):
    def test_empty_debrief_is_descriptive(self) -> None:
        debrief = build_debrief([])

        self.assertEqual(debrief.study_next, ())
        self.assertEqual(debrief.cards_to_fix.count, 0)
        self.assertEqual(debrief.session_habits.review_count, 0)
        self.assertEqual(debrief.session_habits.time_of_day, "No reviews")

    def test_study_next_ranks_terms_before_decks_when_counts_match(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="mitral murmur"),
                _entry(1, 1, 1, text="mitral murmur"),
                _entry(2, 1, 2, text="mitral valve"),
                _entry(2, 1, 3, text="mitral valve"),
            ]
        )

        self.assertEqual(debrief.study_next[0].label, "mitral")
        self.assertEqual(debrief.study_next[0].kind, "term")
        self.assertEqual(debrief.study_next[0].count, 2)
        self.assertEqual(debrief.study_next[0].related_cards, ("Card 2", "Card 1"))

    def test_study_targets_include_capped_deterministic_examples(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="renal sodium", label="Duplicate"),
                _entry(1, 1, 1, text="renal sodium", label="Duplicate"),
                _entry(2, 1, 2, text="renal sodium", label="Duplicate"),
                _entry(2, 1, 3, text="renal sodium", label="Duplicate"),
                _entry(3, 1, 4, text="renal sodium", label="Third"),
                _entry(3, 1, 5, text="renal sodium", label="Third"),
                _entry(4, 1, 6, text="renal sodium", label="Fourth"),
                _entry(4, 1, 7, text="renal sodium", label="Fourth"),
            ]
        )

        self.assertEqual(debrief.study_next[0].related_cards, ("Fourth", "Third", "Duplicate"))

    def test_deck_and_tag_targets_include_matching_examples(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, deck="Cardiology", text="alpha beta", tags=("murmurs",)),
                _entry(1, 1, 1, deck="Cardiology", text="alpha beta", tags=("murmurs",)),
                _entry(2, 1, 2, deck="Renal", text="gamma delta", tags=("electrolytes",)),
                _entry(2, 1, 3, deck="Renal", text="gamma delta", tags=("electrolytes",)),
            ],
            study_limit=5,
        )

        by_kind_label = {(target.kind, target.label): target for target in debrief.study_next}
        self.assertEqual(by_kind_label[("deck", "Cardiology")].related_cards, ("Card 1",))
        self.assertEqual(by_kind_label[("tag", "murmurs")].related_cards, ("Card 1",))

    def test_cards_to_fix_only_counts_cards_with_content_clues(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="weak cue"),
                _entry(1, 1, 1, text="weak cue"),
                _entry(2, 1, 2, text="one clear focused prompt"),
                _entry(2, 1, 3, text="one clear focused prompt"),
            ]
        )

        self.assertEqual(debrief.cards_to_fix.count, 1)
        self.assertEqual(debrief.cards_to_fix.clues, (("Weak cue", 1),))

    def test_session_habits_report_observed_facts(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0),
                _entry(2, 3, 1),
                _entry(3, 1, 2),
            ],
            minimum_misses=1,
        )

        self.assertEqual(debrief.session_habits.review_count, 3)
        self.assertEqual(debrief.session_habits.again_count, 2)
        self.assertAlmostEqual(debrief.session_habits.again_rate, 2 / 3)
        self.assertEqual(debrief.session_habits.time_of_day, "Morning")

    def test_session_habits_use_recorded_answer_time_when_available(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, duration_ms=1000),
                _entry(2, 3, 1, duration_ms=2500),
            ],
            minimum_misses=1,
        )

        self.assertEqual(debrief.session_habits.timed_review_count, 2)
        self.assertEqual(debrief.session_habits.recorded_answer_seconds, 3.5)
        self.assertEqual(debrief.session_habits.seconds_per_timed_card, 1.75)

    def test_session_habits_skip_missing_and_negative_durations(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, duration_ms=None),
                _entry(2, 3, 1, duration_ms=-50),
                _entry(3, 3, 2, duration_ms=500),
            ],
            minimum_misses=1,
        )

        self.assertEqual(debrief.session_habits.review_count, 3)
        self.assertEqual(debrief.session_habits.timed_review_count, 1)
        self.assertEqual(debrief.session_habits.recorded_answer_seconds, 0.5)


if __name__ == "__main__":
    unittest.main()
