from __future__ import annotations

import unittest
from datetime import datetime

from analytics import MissedCardSummary
from debrief import SessionHabits
from debrief_dialog_copy import (
    card_search_button_text,
    debrief_intro_text,
    debrief_title,
    debrief_window_title,
    deck_debrief_button_text,
    early_learning_evidence,
    early_learning_check_text,
    early_learning_next_step,
    early_learning_title,
    evidence_confidence_text,
    missed_examples_button_text,
    mixed_repair_signal_text,
    no_pattern_evidence,
    no_pattern_confidence_text,
    no_pattern_check_text,
    no_pattern_next_step,
    no_pattern_title,
    no_repair_signal_text,
    related_search_button_text,
    repair_action_summary,
    repair_evidence,
    repair_next_step,
    repair_title,
    same_note_cluster_check_text,
    same_note_cluster_evidence,
    same_note_cluster_next_step,
    same_note_cluster_title,
    short_label,
    scoped_early_learning_evidence,
    scoped_early_learning_title,
    study_target_title,
    study_next_step,
    supporting_cards_button_text,
    target_detail_text,
    target_display_label,
    target_evidence_text,
    target_signal_text,
)
from session_context import session_context_text


class DebriefDialogTest(unittest.TestCase):
    def test_study_target_title_uses_review_language(self) -> None:
        self.assertEqual(
            study_target_title("Cardiology Valves"),
            "Check related material: Cardiology Valves",
        )
        self.assertEqual(
            study_target_title(
                "Cardiology Valves",
                kind="tag",
                mostly_early=True,
                early_count=3,
            ),
            "New material to keep reviewing: Cardiology Valves",
        )
        self.assertEqual(
            study_target_title(
                "Cardiology Valves",
                kind="tag",
                mature_count=2,
            ),
            "Revisit this material: Cardiology Valves",
        )
        self.assertEqual(
            study_target_title(
                "Cardiology Valves",
                kind="tag",
                early_count=1,
                lapsed_count=2,
            ),
            "Worth checking: Cardiology Valves",
        )

    def test_tag_targets_are_readable_concepts_with_examples(self) -> None:
        self.assertEqual(
            target_display_label("AnKing::Cardiology::Valves", "tag"),
            "Cardiology Valves",
        )
        self.assertEqual(
            target_display_label("AnKing_Cardiology_Valves", "tag"),
            "Cardiology Valves",
        )
        self.assertEqual(
            target_evidence_text(2, 5, "Cardiology Valves", ("Murmur?", "Aortic stenosis murmur"), active_cards=True),
            (
                "In this window, 2 of 5 cards from Cardiology Valves needed another pass. "
                "Examples: Murmur?, Aortic stenosis murmur."
            ),
        )
        self.assertEqual(
            target_evidence_text(
                4,
                8,
                "Cardiology Valves",
                ("Murmur?",),
                active_cards=True,
                early_count=2,
                mature_count=1,
                lapsed_count=1,
            ),
            (
                "In this window, 4 of 8 cards from Cardiology Valves needed another pass. "
                "Examples: Murmur?. Breakdown: 2 early/new, 1 mature, 1 previously learned."
            ),
        )
        self.assertNotIn("In this window", target_evidence_text(4, 12, "Cardiology Valves", active_cards=True))
        self.assertEqual(
            target_signal_text(2, 5, active_cards=True),
            "2 of 5 cards in this group needed another pass.",
        )
        self.assertEqual(
            target_signal_text(4, 10),
            "4 of 10 cards needed another pass.",
        )
        self.assertEqual(
            target_signal_text(2, 5, mixed_signals=True),
            "2 of 5 cards needed another pass; check both causes.",
        )
        self.assertEqual(
            target_detail_text(("Murmur?",), early_count=2, mature_count=1, lapsed_count=1),
            "Examples: Murmur?. Breakdown: 2 early/new, 1 mature, 1 previously learned.",
        )
        self.assertEqual(
            target_detail_text(),
            "Bonsai saw this pattern in the current review window.",
        )

    def test_debrief_surface_copy_focuses_on_review_check(self) -> None:
        self.assertEqual(debrief_window_title(), "Bonsai Missed Cards")
        self.assertEqual(debrief_title(), "Cards to check")
        self.assertEqual(deck_debrief_button_text(), "Analyze missed cards")

    def test_debrief_intro_names_short_recent_window(self) -> None:
        self.assertEqual(debrief_intro_text(1), "Last 24 hours · read-only · Bonsai does not change scheduling.")
        self.assertIn("Last 2 days", debrief_intro_text(2))

    def test_debrief_action_copy_is_clear_and_cautious(self) -> None:
        self.assertEqual(early_learning_title(), "Early cards need a light check")
        self.assertEqual(card_search_button_text(), "Show card in Browse")
        self.assertEqual(related_search_button_text(), "Show cards to check")
        self.assertEqual(missed_examples_button_text(), "Show missed examples")
        self.assertEqual(supporting_cards_button_text(), "See supporting cards")
        self.assertEqual(
            no_repair_signal_text(),
            "No obvious card-format issue stood out, so inspect the cards before deciding to study more.",
        )
        self.assertEqual(
            mixed_repair_signal_text(),
            "One card may also need editing; check the card before choosing edit vs study.",
        )

    def test_featured_recommendation_copy_separates_evidence_from_action(self) -> None:
        summary = MissedCardSummary(
            1,
            "Cardiology",
            "Aortic stenosis murmur",
            3,
            5,
            datetime(2026, 6, 26),
            content_labels=("Long card", "Dense card"),
        )

        self.assertEqual(repair_title("Aortic stenosis murmur"), "Card to inspect: Aortic stenosis murmur")
        self.assertEqual(
            repair_evidence(summary),
            "Needed another pass on 3/5 recent reviews; possible card issue: Long card, Dense card.",
        )
        self.assertIn("Open the card and read the prompt", repair_next_step())
        self.assertIn("Edit only if it asks too much", repair_next_step())
        self.assertIn("leave it alone", repair_next_step())
        self.assertNotIn("split or simplify", repair_next_step())
        self.assertEqual(
            study_next_step("tag"),
            (
                "Look at a few cards first. If the prompts are clear and the examples still feel unfamiliar, "
                "revisit nearby material for this tag."
            ),
        )
        self.assertIn("Look at a few cards", study_next_step("tag"))
        self.assertIn("prompts are clear", study_next_step("tag"))
        self.assertNotIn("class material", study_next_step("tag"))
        self.assertNotIn("evidence", study_target_title("Cardiology Valves").lower())
        self.assertNotIn("sample", study_target_title("Cardiology Valves").lower())
        self.assertNotIn("surface clues", repair_evidence(summary).lower())
        self.assertIn("newly encountered material", study_next_step("tag", mostly_early=True))
        self.assertIn("Keep reviewing", study_next_step("tag", mostly_early=True))

    def test_study_next_step_adapts_to_maturity_mix(self) -> None:
        mature_step = study_next_step("tag", mature_count=2)
        lapsed_step = study_next_step("tag", early_count=1, lapsed_count=2)

        self.assertIn("revisit the surrounding concept", mature_step)
        self.assertIn("clear and still feel unfamiliar", mature_step)
        self.assertIn("Check the cards first", lapsed_step)
        self.assertIn("may just need another pass", lapsed_step)
        self.assertIn("inspect the card before studying more", lapsed_step)

    def test_same_note_cluster_copy_names_limited_scope(self) -> None:
        summary = MissedCardSummary(
            1,
            "AnKing",
            "Aortic stenosis cloze",
            2,
            3,
            datetime(2026, 6, 26),
            note_id=50,
            note_card_count=4,
            note_repeated_miss_count=3,
        )

        self.assertEqual(same_note_cluster_title("Aortic stenosis cloze"), "One note to inspect: Aortic stenosis cloze")
        self.assertIn("3 cards from the same note", same_note_cluster_evidence(summary))
        self.assertIn("not proof the whole topic is weak", same_note_cluster_evidence(summary))
        self.assertIn("inspect the note", same_note_cluster_next_step())
        self.assertIn("keep reviewing normally", same_note_cluster_check_text())

    def test_evidence_confidence_copy_does_not_overclaim_thin_signals(self) -> None:
        self.assertEqual(evidence_confidence_text(2, 5), "Worth a quick check")
        self.assertEqual(evidence_confidence_text(3, 8), "Worth a quick check")
        self.assertEqual(evidence_confidence_text(4, 10), "Worth checking first")
        self.assertEqual(evidence_confidence_text(4, 10, mixed_signals=True), "Check both causes")
        self.assertEqual(evidence_confidence_text(3, 0, early_learning=True), "Early learning")
        self.assertNotIn("weak", evidence_confidence_text(2, 5).lower())

    def test_study_next_step_matches_target_kind(self) -> None:
        self.assertIn("repeated wording", study_next_step("term"))
        self.assertIn("still feel unfamiliar", study_next_step("term"))
        self.assertIn("broad deck context", study_next_step("deck"))
        self.assertNotIn("signal", study_next_step("deck"))
        self.assertIn("Review the cards", study_next_step("unknown"))
        self.assertNotIn("source", study_next_step("tag").lower())
        self.assertNotIn("source", no_repair_signal_text().lower())

    def test_no_pattern_copy_stays_actionable_without_overclaiming(self) -> None:
        self.assertEqual(no_pattern_title(), "No clear action yet")
        self.assertEqual(no_pattern_confidence_text(), "Not enough signal")
        self.assertIn("do not yet point clearly", no_pattern_evidence())
        self.assertIn("broad study target", no_pattern_evidence())
        self.assertIn("Do not edit or cram from this alone", no_pattern_next_step())
        self.assertIn("inspect that card from Browse", no_pattern_next_step())
        self.assertIn("intentionally staying quiet", no_pattern_check_text())
        self.assertIn("pattern points", no_pattern_check_text())
        self.assertNotIn("review evidence cards", no_pattern_next_step())
        self.assertNotIn("details", no_pattern_next_step().lower())
        self.assertNotIn("weak", no_pattern_confidence_text().lower())

    def test_no_pattern_copy_handles_no_repeated_misses(self) -> None:
        self.assertEqual(no_pattern_title(has_repeated_misses=False), "No action needed yet")
        self.assertEqual(no_pattern_confidence_text(has_repeated_misses=False), "No signal")
        self.assertIn("No card crossed the repeated-miss threshold", no_pattern_evidence(has_repeated_misses=False))
        self.assertIn("Keep reviewing normally", no_pattern_next_step(has_repeated_misses=False))
        self.assertIn("No card needs attention", no_pattern_check_text(has_repeated_misses=False))

    def test_repair_action_summary_names_evidence_and_uncertainty(self) -> None:
        summary = MissedCardSummary(
            1,
            "Cardiology",
            "Aortic stenosis murmur",
            3,
            5,
            datetime(2026, 6, 26),
            content_labels=("Long card", "Dense card"),
        )

        body = repair_action_summary(summary)

        self.assertIn("Needed another pass on 3/5 recent reviews", body)
        self.assertIn("surface clues: Long card, Dense card", body)
        self.assertIn("Open it first and read the prompt", body)
        self.assertIn("Edit only if it asks too much", body)
        self.assertIn("leave it alone and study nearby material", body)

    def test_short_label_truncates_long_card_names(self) -> None:
        self.assertEqual(short_label("A" * 70), "A" * 61 + "...")

    def test_early_learning_copy_frames_normal_first_pass_learning(self) -> None:
        self.assertEqual(
            early_learning_evidence(2),
            "2 early cards are new enough that misses may be first-pass learning, not mature lapses.",
        )
        self.assertEqual(
            early_learning_next_step(),
            "Keep reviewing normally. Study extra only if these felt unfamiliar or cluster around the same concept.",
        )
        self.assertIn("normal early learning", early_learning_check_text())
        self.assertIn("after a few more reps", early_learning_check_text())
        self.assertNotIn("revisit", early_learning_next_step().lower())
        self.assertNotIn("weak", early_learning_check_text().lower())

    def test_scoped_early_learning_copy_names_the_sampled_material(self) -> None:
        self.assertEqual(
            scoped_early_learning_title("Cardiology Valves"),
            "Early cards in Cardiology Valves need a light check",
        )
        self.assertEqual(
            scoped_early_learning_evidence(3, "Cardiology Valves"),
            (
                "3 early cards are in Cardiology Valves. Treat this as first-pass learning, "
                "not proof the whole topic is weak."
            ),
        )
        self.assertNotIn("unlearned", scoped_early_learning_evidence(3, "Cardiology Valves").lower())

    def test_session_context_is_hidden_for_tiny_windows(self) -> None:
        context = session_context_text(SessionHabits(4, 1, 0.25, "Evening"))

        self.assertEqual(context, "")

    def test_session_context_hides_normal_observed_stats(self) -> None:
        context = session_context_text(SessionHabits(10, 2, 0.2, "Evening", 1, 7.0, 7.0))

        self.assertEqual(context, "")

    def test_session_context_hides_high_again_rate_without_actionable_context(self) -> None:
        context = session_context_text(SessionHabits(10, 4, 0.4, "Evening", 1, 7.0, 7.0))

        self.assertEqual(context, "")

    def test_session_context_warns_when_reviewing_unusually_fast(self) -> None:
        context = session_context_text(SessionHabits(10, 2, 0.2, "Evening", 8, 60.0, 7.5))

        self.assertEqual(context, "")

        fast_context = session_context_text(SessionHabits(10, 2, 0.2, "Evening", 8, 20.0, 2.5))

        self.assertNotIn("Session note:", fast_context)
        self.assertIn("2.5s/card", fast_context)
        self.assertIn("slow down before editing cards", fast_context)
        self.assertIn("deciding the material is unlearned", fast_context)
        self.assertNotIn("weaker evidence", fast_context)


if __name__ == "__main__":
    unittest.main()
