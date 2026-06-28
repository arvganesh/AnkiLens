from __future__ import annotations

import unittest

from debrief import CardsToFix, Debrief, EarlyLearning, LlmCheck, LlmDebriefSummary, SessionHabits
from debrief_page import debrief_page_html, llm_summary_html, llm_summary_update_js


def _empty_debrief(*, llm_summary: LlmDebriefSummary | None = None) -> Debrief:
    return Debrief(
        study_next=(),
        cards_to_fix=CardsToFix(0, (), ()),
        early_learning=EarlyLearning(0, ()),
        session_habits=SessionHabits(0, 0, 0, "No reviews"),
        missed_cards=(),
        llm_summary=llm_summary,
    )


class DebriefPageTest(unittest.TestCase):
    def test_renders_in_window_page_shell(self) -> None:
        html = debrief_page_html(
            _empty_debrief(),
            lookback_days=90,
            deck_options=("Cardiology", "Renal::Tubules", "Zanki::Biochem::Metabolism"),
            selected_deck="Renal::Tubules",
            deck_label="Renal::Tubules",
        )

        self.assertIn("<main class=\"bonsai-page\">", html)
        self.assertIn("Missed card analytics", html)
        self.assertIn("Renal::Tubules · Last 90 days", html)
        self.assertIn("<select", html)
        self.assertIn("bonsai:deck:", html)
        self.assertIn('<option value="Renal::Tubules" selected title="Renal::Tubules">Renal::Tubules</option>', html)
        self.assertIn(">Biochem / Metabolism</option>", html)
        self.assertIn("No action needed yet", html)
        self.assertIn("Bonsai summary", html)
        self.assertIn("Looking for patterns", html)
        self.assertIn("window.bonsaiSetLlmSummary", html)

    def test_renders_llm_summary_panel(self) -> None:
        summary = LlmDebriefSummary(
            summary="Valve murmur cards share similar wording.",
            check_first=LlmCheck(
                title="Valve wording",
                why="Examples use similar murmur cues.",
                examples=("Card 1", "Card 2"),
            ),
        )

        html = llm_summary_html(summary)

        self.assertIn("Valve murmur cards share similar wording.", html)
        self.assertIn("Suggested check", html)
        self.assertIn("Valve wording", html)
        self.assertIn("Card 1, Card 2", html)

    def test_llm_summary_update_js_escapes_html(self) -> None:
        summary = LlmDebriefSummary(
            summary="<unsafe>",
            check_first=LlmCheck("Format", "Check <tags>.", ("A&B",)),
        )

        js = llm_summary_update_js(summary)

        self.assertIn("window.bonsaiSetLlmSummary", js)
        self.assertIn("&lt;unsafe&gt;", js)
        self.assertNotIn("<unsafe>", js)


if __name__ == "__main__":
    unittest.main()
