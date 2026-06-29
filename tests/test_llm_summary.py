from __future__ import annotations

import json
import unittest
from datetime import datetime

from analytics import ReviewLogEntry
from config import AnkiLensConfig
from llm_summary import build_llm_summary


def _entry(card_id: int, ease: int, minute: int, *, text: str = "aortic stenosis murmur") -> ReviewLogEntry:
    return ReviewLogEntry(
        card_id=card_id,
        ease=ease,
        reviewed_at=datetime(2026, 6, 26, 9, minute),
        deck_name="Cardiology",
        card_label=f"Card {card_id}",
        tags=("valves",),
        source_text=text,
    )


class _FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class LlmSummaryTest(unittest.TestCase):
    def test_disabled_summary_does_not_call_api(self) -> None:
        calls = []

        result = build_llm_summary(
            [_entry(1, 1, 0)],
            AnkiLensConfig(llm_summary_enabled=False),
            api_key_getter=lambda _name: "key",
            env_file_getter=lambda _name: None,
            opener=lambda *args, **kwargs: calls.append((args, kwargs)),
        )

        self.assertIsNone(result)
        self.assertEqual(calls, [])

    def test_missing_api_key_does_not_call_api(self) -> None:
        calls = []

        result = build_llm_summary(
            [_entry(1, 1, 0)],
            AnkiLensConfig(llm_summary_enabled=True),
            api_key_getter=lambda _name: None,
            env_file_getter=lambda _name: None,
            opener=lambda *args, **kwargs: calls.append((args, kwargs)),
        )

        self.assertIsNone(result)
        self.assertEqual(calls, [])

    def test_sends_capped_missed_card_context_and_parses_json(self) -> None:
        requests = []
        payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "positives": [
                                    "1 reviewed card had no misses in this window.",
                                ],
                                "improvements": [
                                    {
                                        "insight": "2 missed valve cards cluster around nearby murmur physiology.",
                                        "action": "Search for murmur cards and review those before drug cards.",
                                    },
                                    {
                                        "insight": "The repeated valve cards may be easier to separate in a smaller set.",
                                        "action": "Put murmur changes first, then pressure-volume loop cards.",
                                    },
                                ],
                            }
                        )
                    }
                }
            ]
        }

        def opener(request, *, timeout):
            requests.append((request, timeout))
            return _FakeResponse(payload)

        result = build_llm_summary(
            [
                _entry(1, 1, 0),
                _entry(2, 1, 1, text="mitral murmur"),
                _entry(3, 3, 2, text="stable valve card"),
            ],
            AnkiLensConfig(llm_summary_enabled=True, llm_max_chars=2000, llm_timeout_seconds=7),
            api_key_getter=lambda name: "test-key" if name == "OPENROUTER_API_KEY" else None,
            env_file_getter=lambda _name: None,
            opener=opener,
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.positives, ("1 reviewed card had no misses in this window.",))
        self.assertEqual(result.improvements[0].insight, "2 missed valve cards cluster around nearby murmur physiology.")
        self.assertEqual(result.improvements[0].action, "Search for murmur cards and review those before drug cards.")
        self.assertEqual(result.improvements[1].insight, "The repeated valve cards may be easier to separate in a smaller set.")
        self.assertEqual(result.improvements[1].action, "Put murmur changes first, then pressure-volume loop cards.")
        self.assertEqual(result.action_card_ids, (2, 1))
        self.assertEqual(requests[0][1], 7)
        request = requests[0][0]
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
        self.assertEqual(request.get_header("X-title"), "Missed Card Insights")
        body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(body["model"], "inclusionai/ling-2.6-flash")
        self.assertEqual(body["response_format"]["type"], "json_schema")
        schema = body["response_format"]["json_schema"]["schema"]
        self.assertEqual(schema["required"], ["positives", "improvements"])
        self.assertEqual(schema["properties"]["positives"]["maxItems"], 3)
        self.assertEqual(schema["properties"]["improvements"]["maxItems"], 4)
        self.assertEqual(schema["properties"]["improvements"]["items"]["required"], ["insight", "action"])
        self.assertNotIn("$defs", schema)
        system_prompt = body["messages"][0]["content"]
        self.assertIn("two sections", system_prompt)
        self.assertIn("memory-and-learning lens", system_prompt)
        self.assertIn("cards with repeated misses", system_prompt)
        self.assertIn("content that appears often in errors", system_prompt)
        self.assertIn("misses are concentrated early, middle, or late", system_prompt)
        self.assertIn("Use a number in each bullet", system_prompt)
        self.assertIn("Use \"review events\" for total review counts", system_prompt)
        self.assertIn("Never call a unique-card count a review count", system_prompt)
        self.assertIn("positive or calibrating insight", system_prompt)
        self.assertIn("Each positive bullet must make a distinct point", system_prompt)
        self.assertIn("combine them into one bullet", system_prompt)
        self.assertIn("review-method signals", system_prompt)
        self.assertIn("leech-like repeated trouble", system_prompt)
        self.assertIn("too much similar material at once", system_prompt)
        self.assertIn("The insight should name one observation from the evidence", system_prompt)
        self.assertIn("The action should be concrete enough to do immediately", system_prompt)
        self.assertIn("Keep each bullet under 28 words", system_prompt)
        self.assertIn("Avoid generic openings", system_prompt)
        self.assertIn("Use varied sentence structure", system_prompt)
        self.assertIn("directly usable action", system_prompt)
        self.assertIn("Use plain classroom language", system_prompt)
        self.assertIn("Avoid vague phrases", system_prompt)
        self.assertIn("early review flags", system_prompt)
        self.assertIn("retention", system_prompt)
        self.assertIn("interference", system_prompt)
        self.assertIn("murmur cards first, then drug side effects", system_prompt)
        self.assertIn("Do not say what the student understands", system_prompt)
        self.assertIn("retained, mastered", system_prompt)
        self.assertIn("do not recommend changing Anki scheduling", system_prompt)
        self.assertIn("Avoid implementation terms", system_prompt)
        self.assertIn("Window stats", body["messages"][1]["content"])
        self.assertIn("Review-order stats", body["messages"][1]["content"])
        self.assertIn("Use review events for total review counts", body["messages"][1]["content"])
        self.assertIn("Do not repeat the same positive in different words", body["messages"][1]["content"])
        self.assertIn("- Review events: 3.", body["messages"][1]["content"])
        self.assertIn("- Unique cards reviewed: 3.", body["messages"][1]["content"])
        self.assertIn("- Unique cards with at least one miss: 2.", body["messages"][1]["content"])
        self.assertIn("- Unique cards with no misses: 1.", body["messages"][1]["content"])
        self.assertIn("- Misses: 2 across 3 review events.", body["messages"][1]["content"])
        self.assertIn("- First 15 review events: 2 misses across 3 review events and 3 unique cards.", body["messages"][1]["content"])
        self.assertIn("Card 1", body["messages"][1]["content"])
        self.assertIn("aortic stenosis murmur", body["messages"][1]["content"])
        self.assertIn("content_labels=", body["messages"][1]["content"])

    def test_missing_required_model_fields_drop_summary(self) -> None:
        payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "positives": ["A valid positive."],
                                "improvements": [],
                            }
                        )
                    }
                }
            ]
        }

        result = build_llm_summary(
            [_entry(1, 1, 0)],
            AnkiLensConfig(llm_summary_enabled=True),
            api_key_getter=lambda _name: "test-key",
            env_file_getter=lambda _name: None,
            opener=lambda *_args, **_kwargs: _FakeResponse(payload),
        )

        self.assertIsNone(result)

    def test_parser_rewrites_known_jargon(self) -> None:
        payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "positives": [
                                    "1 reviewed card had no misses outside this cue wording cluster, showing solid retention.",
                                ],
                                "improvements": [
                                    {
                                        "insight": "Multiple drug cards show repeated misses, suggesting overload or similarity issues.",
                                        "action": "Search the topic tag and review only that small set first.",
                                    },
                                    {
                                        "insight": "Early review flags point to pacing concerns and weak stability.",
                                        "action": "Delay repeats until stability is seen.",
                                    },
                                ],
                            }
                        )
                    }
                }
            ]
        }

        result = build_llm_summary(
            [_entry(1, 1, 0)],
            AnkiLensConfig(llm_summary_enabled=True),
            api_key_getter=lambda _name: "test-key",
            env_file_getter=lambda _name: None,
            opener=lambda *_args, **_kwargs: _FakeResponse(payload),
        )

        self.assertIsNotNone(result)
        rendered = " ".join(
            result.positives + tuple(part for item in result.improvements for part in (item.insight, item.action))
        ).lower()
        self.assertNotIn("cue", rendered)
        self.assertNotIn("tag", rendered)
        self.assertNotIn("source text", rendered)
        self.assertNotIn("retention", rendered)
        self.assertNotIn("overload", rendered)
        self.assertNotIn("similarity issues", rendered)
        self.assertNotIn("early review flags", rendered)
        self.assertNotIn("pacing", rendered)
        self.assertNotIn("stability", rendered)
        self.assertNotIn("understanding concepts", rendered)
        self.assertNotIn("causing", rendered)
        self.assertNotIn("creating confusion", rendered)

    def test_parser_truncates_long_recommendations_at_word_boundary(self) -> None:
        long_text = (
            "Hemodynamic misses account for 14 of the cards with misses, and the practical adjustment is to keep "
            "pressure-volume loops, preload changes, afterload changes, contractility changes, and murmur effects "
            "inside one smaller pass before adding the drug mechanism cards that make the session feel overloaded."
        )
        payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "positives": [],
                                "improvements": [
                                    {
                                        "insight": long_text,
                                        "action": "Search hemodynamic cards and review that set before adding drug cards.",
                                    }
                                ],
                            }
                        )
                    }
                }
            ]
        }

        result = build_llm_summary(
            [_entry(1, 1, 0)],
            AnkiLensConfig(llm_summary_enabled=True),
            api_key_getter=lambda _name: "test-key",
            env_file_getter=lambda _name: None,
            opener=lambda *_args, **_kwargs: _FakeResponse(payload),
        )

        self.assertIsNotNone(result)
        recommendation = result.improvements[0].insight
        self.assertLessEqual(len(recommendation), 263)
        self.assertTrue(recommendation.endswith("..."))
        self.assertNotIn("overloa...", recommendation)

    def test_prompt_includes_review_order_buckets(self) -> None:
        requests = []
        payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "positives": [],
                                "improvements": [
                                    {
                                        "insight": "3 misses appear later in the review events.",
                                        "action": "Check the later missed cards before adding more kinetics cards.",
                                    }
                                ],
                            }
                        )
                    }
                }
            ]
        }

        def opener(request, *, timeout):
            requests.append(request)
            return _FakeResponse(payload)

        entries = [_entry(card_id=index, ease=3, minute=index) for index in range(1, 13)]
        entries[0] = _entry(1, 1, 1)
        entries[8] = _entry(9, 1, 9)
        entries[9] = _entry(10, 1, 10)

        build_llm_summary(
            entries,
            AnkiLensConfig(llm_summary_enabled=True, llm_max_chars=4000),
            api_key_getter=lambda _name: "test-key",
            env_file_getter=lambda _name: None,
            opener=opener,
        )

        prompt = json.loads(requests[0].data.decode("utf-8"))["messages"][1]["content"]
        self.assertIn("- First 15 review events: 3 misses across 12 review events and 12 unique cards.", prompt)
        self.assertIn("- First third of review events: 1 miss across 4 review events and 4 unique cards.", prompt)
        self.assertIn("- Middle third of review events: 0 misses across 4 review events and 4 unique cards.", prompt)
        self.assertIn("- Last third of review events: 2 misses across 4 review events and 4 unique cards.", prompt)


if __name__ == "__main__":
    unittest.main()
