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
    short_label,
    scoped_early_learning_evidence,
    scoped_early_learning_title,
    study_target_title,
    study_next_step,
    supporting_cards_button_text,
    target_display_label,
    target_evidence_text,
)
from session_context import session_context_text


class DebriefDialogTest(unittest.TestCase):
    def test_study_target_title_uses_review_language(self) -> None:
        self.assertEqual(
            study_target_title("Cardiology Valves"),
            "Material evidence to sample: Cardiology Valves",
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
            "2 of 5 active cards reviewed in Cardiology Valves needed another pass. Examples: Murmur?, Aortic stenosis murmur.",
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
                "4 of 8 active cards reviewed in Cardiology Valves needed another pass. "
                "Breakdown: 2 early/new, 1 mature, 1 lapsed. Examples: Murmur?."
            ),
        )

    def test_debrief_surface_copy_focuses_on_review_check(self) -> None:
        self.assertEqual(debrief_window_title(), "Bonsai Next Check")
        self.assertEqual(debrief_title(), "Next Check")
        self.assertEqual(deck_debrief_button_text(), "What should I check?")

    def test_debrief_intro_names_short_recent_window(self) -> None:
        self.assertEqual(debrief_intro_text(1), "Last 24 hours · read-only · Bonsai does not change scheduling.")
        self.assertIn("Last 2 days", debrief_intro_text(2))

    def test_debrief_action_copy_is_clear_and_cautious(self) -> None:
        self.assertEqual(early_learning_title(), "Early cards need a light check")
        self.assertEqual(card_search_button_text(), "Open card in Browse")
        self.assertEqual(related_search_button_text(), "Find related cards in Browse")
        self.assertEqual(supporting_cards_button_text(), "See supporting evidence")
        self.assertEqual(
            no_repair_signal_text(),
            "No obvious card-format issue stood out, so check related cards before editing.",
        )
        self.assertEqual(
            mixed_repair_signal_text(),
            "One card also has format clues; sample evidence before choosing edit vs study.",
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
            "Needed another pass on 3/5 recent reviews; format clues: Long card, Dense card.",
        )
        self.assertIn("Open the card and read the prompt", repair_next_step())
        self.assertIn("Edit only if it asks too much", repair_next_step())
        self.assertIn("leave it alone", repair_next_step())
        self.assertNotIn("split or simplify", repair_next_step())
        self.assertEqual(
            study_next_step("tag"),
            (
                "Open the active related cards first. If the prompts are clear and the examples still feel unfamiliar, "
                "revisit nearby material for this tag."
            ),
        )
        self.assertIn("active related cards", study_next_step("tag"))
        self.assertIn("prompts are clear", study_next_step("tag"))
        self.assertNotIn("class material", study_next_step("tag"))
        self.assertIn("newly encountered material", study_next_step("tag", mostly_early=True))
        self.assertIn("Keep reviewing", study_next_step("tag", mostly_early=True))

    def test_evidence_confidence_copy_does_not_overclaim_thin_signals(self) -> None:
        self.assertEqual(evidence_confidence_text(2, 5), "Limited evidence")
        self.assertEqual(evidence_confidence_text(3, 8), "Limited evidence")
        self.assertEqual(evidence_confidence_text(4, 10), "Stronger evidence")
        self.assertEqual(evidence_confidence_text(4, 10, mixed_signals=True), "Check both causes")
        self.assertEqual(evidence_confidence_text(3, 0, early_learning=True), "Early learning")

    def test_study_next_step_matches_target_kind(self) -> None:
        self.assertIn("repeated wording", study_next_step("term"))
        self.assertIn("still feel unfamiliar", study_next_step("term"))
        self.assertIn("broad deck evidence", study_next_step("deck"))
        self.assertNotIn("signal", study_next_step("deck"))
        self.assertIn("related cards", study_next_step("unknown"))
        self.assertNotIn("source", study_next_step("tag").lower())
        self.assertNotIn("source", no_repair_signal_text().lower())

    def test_no_pattern_copy_stays_actionable_without_overclaiming(self) -> None:
        self.assertEqual(no_pattern_title(), "No clear action yet")
        self.assertEqual(no_pattern_confidence_text(), "Not enough signal")
        self.assertIn("do not cluster enough", no_pattern_evidence())
        self.assertIn("Do not edit or cram from this alone", no_pattern_next_step())
        self.assertIn("supporting evidence", no_pattern_next_step())
        self.assertIn("intentionally staying quiet", no_pattern_check_text())
        self.assertNotIn("review evidence cards", no_pattern_next_step())
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
        self.assertIn("format clues: Long card, Dense card", body)
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
            "If these felt unfamiliar, revisit the material briefly. Do not edit these cards yet.",
        )
        self.assertIn("normal early learning", early_learning_check_text())
        self.assertIn("after a few more reps", early_learning_check_text())
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

    def test_session_context_warns_when_again_rate_is_high(self) -> None:
        context = session_context_text(SessionHabits(10, 4, 0.4, "Evening", 1, 7.0, 7.0))

        self.assertNotIn("Session note:", context)
        self.assertIn("40% of reviews needed another pass", context)
        self.assertIn("revisit the material before treating one card as the problem", context)

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
