from __future__ import annotations

import unittest
from datetime import datetime, timedelta

from analytics import AGAIN_EASE, filter_review_entries_by_lookback, summarize_missed_cards, summarize_tag_misses
from demo_data import DEMO_DECK_NAME, DEMO_EXPECTED_INSIGHTS, build_demo_review_entries


class DemoDataTest(unittest.TestCase):
    def test_builds_large_recent_demo_review_window(self) -> None:
        now = datetime(2026, 6, 28, 12)

        entries = build_demo_review_entries(now)
        recent_entries = filter_review_entries_by_lookback(entries, lookback_days=7, now=now)
        summaries = summarize_missed_cards(recent_entries, minimum_misses=1, limit=200)

        self.assertGreaterEqual(len(entries), 220)
        self.assertGreaterEqual(len({entry.card_id for entry in entries}), 55)
        self.assertGreaterEqual(len(recent_entries), 60)
        self.assertGreaterEqual(sum(1 for entry in recent_entries if entry.ease == AGAIN_EASE), 30)
        self.assertIn(DEMO_DECK_NAME, {entry.deck_name for entry in entries})
        self.assertNotIn("insights_demo", {tag for entry in entries for tag in entry.tags})
        self.assertTrue(any("Aortic stenosis" in summary.card_label for summary in summaries))
        self.assertTrue(any("Front:" in entry.source_text and "Back:" in entry.source_text for entry in entries))

    def test_demo_expected_insights_are_documented(self) -> None:
        insights_by_key = {insight.key: insight for insight in DEMO_EXPECTED_INSIGHTS}

        self.assertEqual(
            set(insights_by_key),
            {"cardio_hemodynamics", "cardio_drugs", "cardio_arrhythmias"},
        )
        self.assertIn("reviewed cardiology cards", " ".join(insights_by_key["cardio_hemodynamics"].positives))
        hemodynamic_improvements = " ".join(
            part
            for improvement in insights_by_key["cardio_hemodynamics"].improvements
            for part in (improvement.insight, improvement.action)
        )
        drug_improvements = " ".join(
            part
            for improvement in insights_by_key["cardio_drugs"].improvements
            for part in (improvement.insight, improvement.action)
        )
        rhythm_improvements = " ".join(
            part
            for improvement in insights_by_key["cardio_arrhythmias"].improvements
            for part in (improvement.insight, improvement.action)
        )
        self.assertIn("pressure-volume", hemodynamic_improvements)
        self.assertIn("medication safety", drug_improvements.lower())
        self.assertIn("rhythm", rhythm_improvements.lower())

    def test_demo_deck_has_missed_topic_groups_for_each_window(self) -> None:
        now = datetime(2026, 6, 28, 12)
        entries = build_demo_review_entries(now)

        for days in (7, 30, 90):
            scoped_entries = [
                entry
                for entry in filter_review_entries_by_lookback(entries, lookback_days=days, now=now)
                if entry.deck_name == DEMO_DECK_NAME
            ]
            summaries = summarize_missed_cards(scoped_entries, minimum_misses=1, limit=200)
            tags = summarize_tag_misses(summaries, limit=10)

            self.assertTrue(tags, f"expected missed topic group for {days} days")
            self.assertTrue(tags[0].tag.startswith("cardio_"))

    def test_demo_data_spans_thirty_and_ninety_day_windows(self) -> None:
        now = datetime(2026, 6, 28, 12)

        entries = build_demo_review_entries(now)
        thirty_day_entries = filter_review_entries_by_lookback(entries, lookback_days=30, now=now)
        ninety_day_entries = filter_review_entries_by_lookback(entries, lookback_days=90, now=now)

        self.assertGreater(len(thirty_day_entries), len(filter_review_entries_by_lookback(entries, lookback_days=7, now=now)))
        self.assertGreater(len(ninety_day_entries), len(thirty_day_entries))
        self.assertTrue(any(entry.reviewed_at <= now - timedelta(days=35) for entry in ninety_day_entries))

    def test_review_log_backs_expected_insight_windows(self) -> None:
        now = datetime(2026, 6, 28, 12)
        entries = [
            entry
            for entry in build_demo_review_entries(now)
            if entry.deck_name == DEMO_DECK_NAME
        ]

        seven_day_summaries = summarize_missed_cards(
            filter_review_entries_by_lookback(entries, lookback_days=7, now=now),
            minimum_misses=1,
            limit=200,
        )
        thirty_day_summaries = summarize_missed_cards(
            filter_review_entries_by_lookback(entries, lookback_days=30, now=now),
            minimum_misses=1,
            limit=200,
        )
        ninety_day_summaries = summarize_missed_cards(
            filter_review_entries_by_lookback(entries, lookback_days=90, now=now),
            minimum_misses=1,
            limit=200,
        )

        seven_day_tags = {tag.tag: tag for tag in summarize_tag_misses(seven_day_summaries, limit=10)}
        thirty_day_tags = {tag.tag: tag for tag in summarize_tag_misses(thirty_day_summaries, limit=10)}
        ninety_day_tags = {tag.tag: tag for tag in summarize_tag_misses(ninety_day_summaries, limit=10)}

        self.assertGreaterEqual(seven_day_tags["cardio_hemodynamics"].missed_cards, 16)
        self.assertGreaterEqual(thirty_day_tags["cardio_drugs"].missed_cards, 10)
        self.assertGreaterEqual(ninety_day_tags["cardio_arrhythmias"].missed_cards, 8)
        self.assertNotIn("cardio_arrhythmias", seven_day_tags)


if __name__ == "__main__":
    unittest.main()
