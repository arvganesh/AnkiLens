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
    card_reps: int | None = None,
    card_lapses: int | None = None,
    review_type: int | None = None,
    card_queue: int | None = None,
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
        card_reps=card_reps,
        card_lapses=card_lapses,
        review_type=review_type,
        card_queue=card_queue,
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
                _entry(3, 3, 4, text="mitral regurgitation"),
                _entry(4, 3, 5, text="mitral stenosis"),
            ]
        )

        self.assertEqual(debrief.study_next[0].label, "mitral")
        self.assertEqual(debrief.study_next[0].kind, "term")
        self.assertEqual(debrief.study_next[0].count, 2)
        self.assertEqual(debrief.study_next[0].reviewed_count, 4)
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

    def test_study_targets_use_repeated_tags_instead_of_raw_terms_when_available(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="aortic stenosis", tags=("AnKing_Cardiology_Valves",)),
                _entry(1, 1, 1, text="aortic stenosis", tags=("AnKing_Cardiology_Valves",)),
                _entry(2, 1, 2, text="aortic murmur", tags=("AnKing_Cardiology_Valves",)),
                _entry(2, 1, 3, text="aortic murmur", tags=("AnKing_Cardiology_Valves",)),
                _entry(3, 3, 4, text="mitral regurgitation", tags=("AnKing_Cardiology_Valves",)),
                _entry(4, 3, 5, text="mitral stenosis", tags=("AnKing_Cardiology_Valves",)),
                _entry(5, 3, 6, text="tricuspid regurgitation", tags=("AnKing_Cardiology_Valves",)),
            ]
        )

        self.assertEqual(len(debrief.study_next), 1)
        self.assertEqual(debrief.study_next[0].kind, "tag")
        self.assertEqual(debrief.study_next[0].label, "AnKing_Cardiology_Valves")
        self.assertEqual(debrief.study_next[0].reviewed_count, 5)
        self.assertAlmostEqual(debrief.study_next[0].miss_rate, 2 / 5)

    def test_study_targets_ignore_broad_anking_tags_when_topic_tag_exists(self) -> None:
        broad = ("AnKing", "AnKing::Decks", "AK_Step1_v12")
        topic = "AnKing::Cardiology::Valves"
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="aortic stenosis", tags=broad + (topic,)),
                _entry(1, 1, 1, text="aortic stenosis", tags=broad + (topic,)),
                _entry(2, 1, 2, text="aortic murmur", tags=broad + (topic,)),
                _entry(2, 1, 3, text="aortic murmur", tags=broad + (topic,)),
                _entry(3, 3, 4, text="mitral regurgitation", tags=broad + (topic,)),
                _entry(4, 3, 5, text="mitral stenosis", tags=broad + (topic,)),
                _entry(5, 3, 6, text="tricuspid regurgitation", tags=broad + (topic,)),
            ]
        )

        self.assertEqual(debrief.study_next[0].label, topic)
        self.assertEqual(debrief.study_next[0].related_cards, ("Card 2", "Card 1"))

    def test_tag_study_targets_use_active_unsuspended_cards(self) -> None:
        tag = "AnKing::Cardiology::Valves"
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="aortic stenosis", tags=(tag,), card_queue=-1, label="Suspended AS"),
                _entry(1, 1, 1, text="aortic stenosis", tags=(tag,), card_queue=-1, label="Suspended AS"),
                _entry(2, 1, 2, text="aortic murmur", tags=(tag,), card_queue=2, label="Active AS"),
                _entry(2, 1, 3, text="aortic murmur", tags=(tag,), card_queue=2, label="Active AS"),
                _entry(3, 1, 4, text="mitral regurgitation", tags=(tag,), card_queue=2, label="Active MR"),
                _entry(3, 1, 5, text="mitral regurgitation", tags=(tag,), card_queue=2, label="Active MR"),
                _entry(4, 3, 6, text="mitral stenosis", tags=(tag,), card_queue=2),
                _entry(5, 3, 7, text="tricuspid regurgitation", tags=(tag,), card_queue=2),
                _entry(6, 3, 8, text="pulmonic stenosis", tags=(tag,), card_queue=2),
            ]
        )

        self.assertEqual(debrief.study_next[0].label, tag)
        self.assertEqual(debrief.study_next[0].count, 2)
        self.assertEqual(debrief.study_next[0].reviewed_count, 5)
        self.assertEqual(debrief.study_next[0].related_cards, ("Active MR", "Active AS"))

    def test_suspended_only_tag_misses_do_not_create_study_target(self) -> None:
        tag = "AnKing::Cardiology::Valves"
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="aortic stenosis", tags=(tag,), card_queue=-1),
                _entry(1, 1, 1, text="aortic stenosis", tags=(tag,), card_queue=-1),
                _entry(2, 1, 2, text="aortic murmur", tags=(tag,), card_queue=-1),
                _entry(2, 1, 3, text="aortic murmur", tags=(tag,), card_queue=-1),
                _entry(3, 3, 4, text="mitral regurgitation", tags=(tag,), card_queue=-1),
                _entry(4, 3, 5, text="mitral stenosis", tags=(tag,), card_queue=-1),
                _entry(5, 3, 6, text="tricuspid regurgitation", tags=(tag,), card_queue=-1),
            ]
        )

        self.assertNotEqual(debrief.study_next[0].kind, "tag")

    def test_study_targets_require_enough_denominator_support(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="aortic stenosis", tags=("AnKing_Cardiology_Valves",)),
                _entry(1, 1, 1, text="aortic stenosis", tags=("AnKing_Cardiology_Valves",)),
                _entry(2, 1, 2, text="aortic murmur", tags=("AnKing_Cardiology_Valves",)),
                _entry(2, 1, 3, text="aortic murmur", tags=("AnKing_Cardiology_Valves",)),
            ]
        )

        self.assertEqual(debrief.study_next, ())

    def test_study_targets_prefer_concentrated_tags_over_broad_volume(self) -> None:
        entries = [
            _entry(1, 1, 0, tags=("broad", "focused")),
            _entry(1, 1, 1, tags=("broad", "focused")),
            _entry(2, 1, 2, tags=("broad", "focused")),
            _entry(2, 1, 3, tags=("broad", "focused")),
            _entry(3, 1, 4, tags=("broad", "focused")),
            _entry(3, 1, 5, tags=("broad", "focused")),
            _entry(4, 3, 6, tags=("broad", "focused")),
            _entry(5, 3, 7, tags=("broad", "focused")),
        ]
        entries.extend(_entry(card_id, 3, card_id + 10, tags=("broad",)) for card_id in range(6, 21))

        debrief = build_debrief(entries, study_limit=5)

        self.assertEqual(debrief.study_next[0].label, "focused")
        self.assertEqual(debrief.study_next[0].reviewed_count, 5)

    def test_study_targets_use_all_repeated_misses_not_display_cap(self) -> None:
        entries = [
            _entry(1, 1, 0, text="renal sodium transport", tags=("renal_sodium",), label="Renal 1"),
            _entry(1, 1, 1, text="renal sodium transport", tags=("renal_sodium",), label="Renal 1"),
            _entry(2, 1, 2, text="renal potassium handling", tags=("renal_sodium",), label="Renal 2"),
            _entry(2, 1, 3, text="renal potassium handling", tags=("renal_sodium",), label="Renal 2"),
            _entry(3, 1, 4, text="renal chloride handling", tags=("renal_sodium",), label="Renal 3"),
            _entry(3, 1, 5, text="renal chloride handling", tags=("renal_sodium",), label="Renal 3"),
            _entry(4, 3, 6, text="renal physiology", tags=("renal_sodium",)),
            _entry(5, 3, 7, text="renal physiology", tags=("renal_sodium",)),
            _entry(20, 1, 20, text="isolated miss", tags=("random_a",), label="Random A"),
            _entry(20, 1, 21, text="isolated miss", tags=("random_a",), label="Random A"),
            _entry(21, 1, 22, text="isolated miss", tags=("random_b",), label="Random B"),
            _entry(21, 1, 23, text="isolated miss", tags=("random_b",), label="Random B"),
        ]

        debrief = build_debrief(entries, result_limit=2)

        self.assertEqual([summary.card_label for summary in debrief.missed_cards], ["Random B", "Random A"])
        self.assertEqual(debrief.study_next[0].label, "renal_sodium")
        self.assertEqual(debrief.study_next[0].related_cards, ("Renal 3", "Renal 2", "Renal 1"))

    def test_study_targets_prefer_repeated_tags_over_deck_fallback(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, deck="AnKing", text="alpha beta", tags=("cardiology", "murmurs")),
                _entry(1, 1, 1, deck="AnKing", text="alpha beta", tags=("cardiology", "murmurs")),
                _entry(2, 1, 2, deck="AnKing", text="gamma delta", tags=("cardiology",)),
                _entry(2, 1, 3, deck="AnKing", text="gamma delta", tags=("cardiology",)),
                _entry(3, 3, 4, deck="AnKing", text="epsilon zeta", tags=("cardiology",)),
                _entry(4, 3, 5, deck="AnKing", text="eta theta", tags=("cardiology",)),
                _entry(5, 3, 6, deck="AnKing", text="iota kappa", tags=("cardiology",)),
            ],
            study_limit=5,
        )

        by_kind_label = {(target.kind, target.label): target for target in debrief.study_next}
        self.assertNotIn(("deck", "AnKing"), by_kind_label)
        self.assertEqual(by_kind_label[("tag", "cardiology")].related_cards, ("Card 2", "Card 1"))

    def test_study_targets_fall_back_to_deck_when_no_content_pattern_exists(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, deck="Cardiology", text="alpha beta", tags=("murmurs",)),
                _entry(1, 1, 1, deck="Cardiology", text="alpha beta", tags=("murmurs",)),
                _entry(2, 1, 2, deck="Cardiology", text="gamma delta", tags=("valves",)),
                _entry(2, 1, 3, deck="Cardiology", text="gamma delta", tags=("valves",)),
                _entry(3, 3, 4, deck="Cardiology", text="epsilon zeta", tags=("arrhythmias",)),
                _entry(4, 3, 5, deck="Cardiology", text="eta theta", tags=("ischemia",)),
                _entry(5, 3, 6, deck="Cardiology", text="iota kappa", tags=("congenital",)),
            ],
            study_limit=5,
        )

        self.assertEqual(debrief.study_next[0].kind, "deck")
        self.assertEqual(debrief.study_next[0].label, "Cardiology")
        self.assertEqual(debrief.study_next[0].reviewed_count, 5)
        self.assertEqual(debrief.study_next[0].related_cards, ("Card 2", "Card 1"))

    def test_cards_to_fix_ignores_weak_cue_alone(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="weak cue", card_reps=8),
                _entry(1, 1, 1, text="weak cue", card_reps=8),
                _entry(1, 3, 2, text="weak cue", card_reps=8),
                _entry(2, 1, 2, text="one clear focused prompt"),
                _entry(2, 1, 3, text="one clear focused prompt"),
            ]
        )

        self.assertEqual(debrief.cards_to_fix.count, 0)
        self.assertEqual(debrief.cards_to_fix.clues, ())

    def test_cards_to_fix_counts_strong_repair_clue(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="word " * 80, card_reps=8),
                _entry(1, 1, 1, text="word " * 80, card_reps=8),
                _entry(1, 3, 2, text="word " * 80, card_reps=8),
            ]
        )

        self.assertEqual(debrief.cards_to_fix.count, 1)
        self.assertEqual(debrief.cards_to_fix.clues, (("Long card", 1), ("Dense card", 1)))

    def test_cloze_heavy_alone_is_not_a_repair_signal(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="Aortic stenosis causes a {{c1::crescendo decrescendo}} systolic murmur.", card_reps=8),
                _entry(1, 1, 1, text="Aortic stenosis causes a {{c1::crescendo decrescendo}} systolic murmur.", card_reps=8),
                _entry(1, 3, 2, text="Aortic stenosis causes a {{c1::crescendo decrescendo}} systolic murmur.", card_reps=8),
            ]
        )

        self.assertEqual(debrief.cards_to_fix.count, 0)
        self.assertEqual(debrief.cards_to_fix.clues, ())

    def test_cards_to_fix_counts_multiple_weaker_clues(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="AS vs MR", card_reps=8),
                _entry(1, 1, 1, text="AS vs MR", card_reps=8),
                _entry(1, 3, 2, text="AS vs MR", card_reps=8),
            ]
        )

        self.assertEqual(debrief.cards_to_fix.count, 1)
        self.assertEqual(debrief.cards_to_fix.clues, (("Weak cue", 1), ("Comparison", 1)))

    def test_repair_does_not_preempt_broader_study_pattern(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="word " * 80, tags=("cardiology",), card_reps=8),
                _entry(1, 1, 1, text="word " * 80, tags=("cardiology",), card_reps=8),
                _entry(2, 1, 2, text="focused aortic stenosis prompt", tags=("cardiology",), card_reps=8),
                _entry(2, 1, 3, text="focused aortic stenosis prompt", tags=("cardiology",), card_reps=8),
                _entry(3, 1, 4, text="focused mitral regurgitation prompt", tags=("cardiology",), card_reps=8),
                _entry(3, 1, 5, text="focused mitral regurgitation prompt", tags=("cardiology",), card_reps=8),
                _entry(4, 3, 6, text="focused tricuspid regurgitation prompt", tags=("cardiology",), card_reps=8),
                _entry(5, 3, 7, text="focused pulmonic stenosis prompt", tags=("cardiology",), card_reps=8),
            ]
        )

        self.assertEqual(debrief.cards_to_fix.count, 1)
        self.assertEqual(debrief.study_next[0].label, "cardiology")
        self.assertFalse(debrief.repair_is_top_check)

    def test_strong_repair_leads_over_weak_broad_study_pattern(self) -> None:
        entries = [
            _entry(1, 1, 0, text="word " * 80, tags=("cardiology",), card_reps=8),
            _entry(1, 1, 1, text="word " * 80, tags=("cardiology",), card_reps=8),
            _entry(2, 1, 2, text="focused aortic stenosis prompt", tags=("cardiology",), card_reps=8),
            _entry(2, 1, 3, text="focused aortic stenosis prompt", tags=("cardiology",), card_reps=8),
            _entry(3, 1, 4, text="focused mitral regurgitation prompt", tags=("cardiology",), card_reps=8),
            _entry(3, 1, 5, text="focused mitral regurgitation prompt", tags=("cardiology",), card_reps=8),
        ]
        entries.extend(
            _entry(card_id, 3, card_id + 10, text="stable cardiology prompt", tags=("cardiology",), card_reps=8)
            for card_id in range(4, 13)
        )

        debrief = build_debrief(entries)

        self.assertEqual(debrief.study_next[0].label, "cardiology")
        self.assertAlmostEqual(debrief.study_next[0].miss_rate, 3 / 12)
        self.assertTrue(debrief.repair_is_top_check)

    def test_repair_leads_when_no_supported_study_pattern_exists(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="word " * 80, card_reps=8),
                _entry(1, 1, 1, text="word " * 80, card_reps=8),
                _entry(1, 3, 2, text="word " * 80, card_reps=8),
            ]
        )

        self.assertTrue(debrief.repair_is_top_check)

    def test_cards_to_fix_excludes_early_exposure_cards(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="word " * 80, tags=("AnKing_Cardiology_Valves",), card_reps=2),
                _entry(1, 1, 1, text="word " * 80, tags=("AnKing_Cardiology_Valves",), card_reps=2),
                _entry(2, 1, 2, text="focused aortic stenosis murmur prompt", tags=("AnKing_Cardiology_Valves",), card_reps=8),
                _entry(2, 1, 3, text="focused aortic stenosis murmur prompt", tags=("AnKing_Cardiology_Valves",), card_reps=8),
                _entry(3, 3, 4, text="focused mitral stenosis prompt", tags=("AnKing_Cardiology_Valves",), card_reps=8),
                _entry(4, 3, 5, text="focused tricuspid regurgitation prompt", tags=("AnKing_Cardiology_Valves",), card_reps=8),
                _entry(5, 3, 6, text="focused pulmonic stenosis prompt", tags=("AnKing_Cardiology_Valves",), card_reps=8),
            ]
        )

        self.assertEqual(debrief.cards_to_fix.count, 0)
        self.assertEqual(debrief.early_learning.count, 1)
        self.assertEqual(debrief.study_next[0].label, "AnKing_Cardiology_Valves")
        self.assertEqual(debrief.study_next[0].reviewed_count, 5)

    def test_early_learning_is_first_class_for_low_rep_misses(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="aortic stenosis murmur", tags=("AnKing_Cardiology_Valves",), card_reps=3, card_lapses=0),
                _entry(1, 1, 1, text="aortic stenosis murmur", tags=("AnKing_Cardiology_Valves",), card_reps=3, card_lapses=0),
                _entry(2, 3, 2, text="mitral regurgitation murmur", tags=("AnKing_Cardiology_Valves",), card_reps=8),
                _entry(3, 3, 3, text="mitral stenosis murmur", tags=("AnKing_Cardiology_Valves",), card_reps=8),
                _entry(4, 3, 4, text="tricuspid regurgitation murmur", tags=("AnKing_Cardiology_Valves",), card_reps=8),
                _entry(5, 3, 5, text="pulmonic stenosis murmur", tags=("AnKing_Cardiology_Valves",), card_reps=8),
            ]
        )

        self.assertEqual(debrief.early_learning.count, 1)
        self.assertEqual(debrief.early_learning.cards[0].card_id, 1)
        self.assertEqual(debrief.cards_to_fix.count, 0)
        self.assertFalse(debrief.early_learning_is_dominant)

    def test_early_learning_includes_single_miss_new_material(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="aortic stenosis murmur", tags=("AnKing_Cardiology_Valves",), card_reps=1, card_lapses=0),
                _entry(2, 1, 1, text="mitral regurgitation murmur", tags=("AnKing_Cardiology_Valves",), card_reps=1, card_lapses=0),
                _entry(3, 1, 2, text="tricuspid regurgitation murmur", tags=("AnKing_Cardiology_Valves",), card_reps=1, card_lapses=0),
                _entry(4, 3, 3, text="pulmonic stenosis murmur", tags=("AnKing_Cardiology_Valves",), card_reps=1, card_lapses=0),
                _entry(5, 3, 4, text="mitral stenosis murmur", tags=("AnKing_Cardiology_Valves",), card_reps=1, card_lapses=0),
            ]
        )

        self.assertEqual(debrief.missed_cards, ())
        self.assertEqual(debrief.early_learning.count, 3)
        self.assertTrue(debrief.early_learning_is_dominant)
        self.assertEqual(debrief.study_next[0].label, "AnKing_Cardiology_Valves")
        self.assertEqual(debrief.study_next[0].related_cards, ("Card 3", "Card 2", "Card 1"))

    def test_early_learning_dominates_only_when_all_repeated_misses_are_early(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="aortic stenosis murmur", tags=("AnKing_Cardiology_Valves",), card_reps=3, card_lapses=0),
                _entry(1, 1, 1, text="aortic stenosis murmur", tags=("AnKing_Cardiology_Valves",), card_reps=3, card_lapses=0),
                _entry(2, 1, 2, text="mitral regurgitation murmur", tags=("AnKing_Cardiology_Valves",), card_reps=4, card_lapses=0),
                _entry(2, 1, 3, text="mitral regurgitation murmur", tags=("AnKing_Cardiology_Valves",), card_reps=4, card_lapses=0),
                _entry(3, 3, 4, text="tricuspid regurgitation murmur", tags=("AnKing_Cardiology_Valves",), card_reps=3, card_lapses=0),
                _entry(4, 3, 5, text="pulmonic stenosis murmur", tags=("AnKing_Cardiology_Valves",), card_reps=3, card_lapses=0),
                _entry(5, 3, 6, text="mitral stenosis murmur", tags=("AnKing_Cardiology_Valves",), card_reps=3, card_lapses=0),
            ]
        )

        self.assertEqual(debrief.early_learning.count, 2)
        self.assertTrue(debrief.early_learning_is_dominant)
        self.assertEqual(debrief.study_next[0].label, "AnKing_Cardiology_Valves")

    def test_lapsed_cards_are_not_treated_as_new_material(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="aortic stenosis murmur", card_reps=3, card_lapses=1),
                _entry(1, 1, 1, text="aortic stenosis murmur", card_reps=3, card_lapses=1),
            ]
        )

        self.assertEqual(debrief.early_learning.count, 0)

    def test_limited_recent_history_alone_is_not_early_learning(self) -> None:
        debrief = build_debrief(
            [
                _entry(1, 1, 0, text="aortic stenosis murmur"),
                _entry(1, 1, 1, text="aortic stenosis murmur"),
            ]
        )

        self.assertEqual(debrief.early_learning.count, 0)

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
