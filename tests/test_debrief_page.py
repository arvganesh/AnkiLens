from __future__ import annotations

import unittest

from debrief import Debrief, DebriefEvidence, LlmDebriefSummary, LlmImprovement
from debrief_page import debrief_page_html, llm_summary_html, llm_summary_status_update_js, llm_summary_update_js


def _empty_debrief(*, llm_summary: LlmDebriefSummary | None = None) -> Debrief:
    return Debrief(
        evidence=DebriefEvidence(12, 3, 20, 5),
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

        self.assertIn("<main class=\"ankilens-page\">", html)
        self.assertNotIn("ankilens-brand", html)
        self.assertNotIn("ankilens-brand-mark", html)
        self.assertIn("<h1>Insights</h1>", html)
        self.assertNotIn("Last 90 days", html)
        self.assertNotIn("Renal::Tubules · Last 90 days", html)
        self.assertNotIn("read-only", html)
        self.assertNotIn("scheduling is unchanged", html)
        self.assertIn("<select", html)
        self.assertIn("ankilens:deck:", html)
        self.assertIn("ankilens:lookback:", html)
        self.assertNotIn("All decks", html)
        self.assertNotIn('value=""', html)
        self.assertIn('<option value="Renal::Tubules" selected title="Renal::Tubules">Renal::Tubules</option>', html)
        self.assertIn('<option value="7">7 days</option>', html)
        self.assertIn('<option value="30">30 days</option>', html)
        self.assertIn('<option value="90" selected>90 days</option>', html)
        self.assertIn(">Biochem / Metabolism</option>", html)
        self.assertNotIn("Review pattern", html)
        self.assertNotIn("cards with misses", html)
        self.assertNotIn("again rate", html)
        self.assertNotIn("Based on Renal::Tubules, last 90 days.", html)
        self.assertIn("Looking for patterns", html)
        self.assertIn("window.ankilensSetLlmSummary", html)
        self.assertIn("data-ankilens-browse-query", html)
        self.assertIn("ankilens:browse:", html)
        self.assertNotIn("Check first", html)
        self.assertNotIn("No action needed yet", html)

    def test_page_shows_llm_disabled_state_without_deterministic_fallback(self) -> None:
        html = debrief_page_html(
            _empty_debrief(),
            lookback_days=30,
            deck_options=("Cardiology",),
            selected_deck="Cardiology",
            llm_enabled=False,
        )

        self.assertIn("LLM insights are not enabled", html)
        self.assertNotIn("Looking for patterns", html)
        self.assertNotIn("Check first", html)

    def test_renders_llm_summary_panel(self) -> None:
        summary = LlmDebriefSummary(
            positives=("32 reviewed cards had no misses in this window.",),
            improvements=(
                LlmImprovement(
                    insight="12 missed valve cards cluster around maneuver and physiology wording.",
                    action="Search for murmur cards and review those before drug cards.",
                ),
                LlmImprovement(
                    insight="Repeated valve misses may be easier to separate in a smaller set.",
                    action="Put murmur changes first, then pressure-volume loop cards.",
                ),
            ),
            action_card_ids=(20, 10, 20),
        )

        html = llm_summary_html(
            summary,
            DebriefEvidence(12, 3, 20, 5),
            grounding="Based on Cardiology, last 30 days. Uses review logs and missed-card text only.",
        )

        self.assertNotIn("Review pattern", html)
        self.assertIn("Based on analysis of the last 20 reviews:", html)
        self.assertIn("What you&#x27;re doing well", html)
        self.assertIn("Areas for improvement", html)
        self.assertIn("ankilens-recommendations", html)
        self.assertIn("32 reviewed cards had no misses", html)
        self.assertIn("12 missed valve cards", html)
        self.assertIn("Try: Search for murmur cards", html)
        self.assertIn("ankilens-action", html)
        self.assertIn("Cards to inspect", html)
        self.assertIn("Open 2 missed cards in Browse", html)
        self.assertIn("data-ankilens-browse-query", html)
        self.assertIn("cid:20 or cid:10", html)
        self.assertNotIn("25%", html)
        self.assertNotIn("Based on Cardiology, last 30 days.", html)
        self.assertNotIn("Pattern", html)
        self.assertNotIn("Focus", html)
        self.assertNotIn("Why this came up", html)
        self.assertNotIn("Suggested check", html)

    def test_llm_summary_update_js_escapes_html(self) -> None:
        summary = LlmDebriefSummary(
            positives=("<unsafe>",),
            improvements=(LlmImprovement(insight="Check <tags>.", action="Open <unsafe>."),),
        )

        js = llm_summary_update_js(summary)

        self.assertIn("window.ankilensSetLlmSummary", js)
        self.assertIn("&lt;unsafe&gt;", js)
        self.assertNotIn("<unsafe>", js)

    def test_llm_status_update_js_escapes_message(self) -> None:
        js = llm_summary_status_update_js("<missing key>")

        self.assertIn("window.ankilensSetLlmSummary", js)
        self.assertIn("&lt;missing key&gt;", js)
        self.assertNotIn("<missing key>", js)


if __name__ == "__main__":
    unittest.main()
