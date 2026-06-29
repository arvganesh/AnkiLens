from __future__ import annotations

import json
import unittest
import urllib.error
from datetime import datetime

from analytics import ReviewLogEntry
from config import AnkiLensConfig
from debrief import LlmDebriefError
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

    def test_bad_api_key_returns_user_safe_error(self) -> None:
        def opener(_request, *, timeout):
            raise urllib.error.HTTPError(
                url="https://openrouter.ai/api/v1/chat/completions",
                code=401,
                msg="Unauthorized",
                hdrs={},
                fp=None,
            )

        result = build_llm_summary(
            [_entry(1, 1, 0)],
            AnkiLensConfig(llm_summary_enabled=True, llm_api_key="bad-key"),
            api_key_getter=lambda _name: None,
            env_file_getter=lambda _name: None,
            opener=opener,
        )

        self.assertEqual(result, LlmDebriefError("OpenRouter rejected the API key. Check the key and try again."))

    def test_unusable_model_response_returns_user_safe_error(self) -> None:
        payload = {"choices": [{"message": {"content": "{}"}}]}

        result = build_llm_summary(
            [_entry(1, 1, 0)],
            AnkiLensConfig(llm_summary_enabled=True, llm_api_key="local-key"),
            api_key_getter=lambda _name: None,
            env_file_getter=lambda _name: None,
            opener=lambda *_args, **_kwargs: _FakeResponse(payload),
        )

        self.assertEqual(
            result,
            LlmDebriefError("The model did not return a usable insight. Try again or use a different model."),
        )

    def test_uses_local_config_api_key_before_environment(self) -> None:
        requests = []
        payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "improvements": [
                                    {
                                        "insight": "1 enzyme card appears in the missed-card evidence.",
                                        "action": "Open the enzyme card and check whether it asks for several facts.",
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

        result = build_llm_summary(
            [_entry(1, 1, 0)],
            AnkiLensConfig(llm_summary_enabled=True, llm_api_key="local-key"),
            api_key_getter=lambda _name: "env-key",
            env_file_getter=lambda _name: None,
            opener=opener,
        )

        self.assertIsNotNone(result)
        self.assertEqual(requests[0].get_header("Authorization"), "Bearer local-key")

    def test_sends_capped_missed_card_context_and_parses_json(self) -> None:
        requests = []
        payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
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
        self.assertEqual(result.positives, ())
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
        self.assertEqual(body["model"], "deepseek/deepseek-v4-flash")
        self.assertEqual(body["temperature"], 0)
        self.assertEqual(body["response_format"]["type"], "json_schema")
        schema = body["response_format"]["json_schema"]["schema"]
        self.assertEqual(schema["required"], ["improvements"])
        self.assertNotIn("positives", schema["properties"])
        self.assertEqual(schema["properties"]["improvements"]["maxItems"], 3)
        self.assertEqual(schema["properties"]["improvements"]["items"]["required"], ["insight", "action"])
        self.assertNotIn("$defs", schema)
        system_prompt = body["messages"][0]["content"]
        self.assertIn("friendly study assistant", system_prompt)
        self.assertIn("Areas for improvement", system_prompt)
        self.assertIn("what kind of card is causing trouble", system_prompt)
        self.assertIn("what to change in Anki", system_prompt)
        self.assertIn("ordered from most impactful fix to least impactful fix", system_prompt)
        self.assertIn("Start with the problem, not a statistic", system_prompt)
        self.assertIn("Use stats only when they make the impact obvious", system_prompt)
        self.assertIn("Avoid exact ratios", system_prompt)
        self.assertIn("Mention at most two example cards or topics", system_prompt)
        self.assertIn("Avoid long parenthetical lists", system_prompt)
        self.assertIn("Several missed cards ask for long lists of facts", system_prompt)
        self.assertIn("Similar tissue cards are hard to tell apart", system_prompt)
        self.assertIn("One protein-structure card asks about several levels at once", system_prompt)
        self.assertIn("In the good insight examples, notice", system_prompt)
        self.assertIn("Counts are omitted unless they make the problem clearer", system_prompt)
        self.assertIn("The wording explains why the card is hard to answer", system_prompt)
        self.assertIn("Start with a concrete verb", system_prompt)
        self.assertIn("Open, Split, Rewrite, Search, or Put", system_prompt)
        self.assertIn('not just "review more"', system_prompt)
        self.assertIn("Review the tissue cards separately", system_prompt)
        self.assertIn("Open the protein-structure card and split it", system_prompt)
        self.assertIn("In the good action examples, notice", system_prompt)
        self.assertIn("can be done inside Anki", system_prompt)
        self.assertIn("avoids vague advice", system_prompt)
        self.assertIn("card cluster", system_prompt)
        self.assertIn("recall spoon", system_prompt)
        self.assertIn("Do not say the student understands", system_prompt)
        self.assertIn("Do not claim the card content is medically or factually correct", system_prompt)
        self.assertIn("Miss definition: only Again review buttons count as misses.", body["messages"][1]["content"])
        self.assertIn("Focus on content patterns in the missed-card evidence", body["messages"][1]["content"])
        self.assertIn("numbered evidence below includes 2 missed-card examples", body["messages"][1]["content"])
        self.assertIn("Do not mention a different analyzed-example count", body["messages"][1]["content"])
        self.assertNotIn("Window stats", body["messages"][1]["content"])
        self.assertNotIn("Review-order stats", body["messages"][1]["content"])
        self.assertNotIn("Unique cards reviewed", body["messages"][1]["content"])
        self.assertIn("Card 1", body["messages"][1]["content"])
        self.assertIn("aortic stenosis murmur", body["messages"][1]["content"])
        self.assertIn("review_events_for_card=", body["messages"][1]["content"])
        self.assertIn("content_labels=", body["messages"][1]["content"])

    def test_missing_required_model_fields_return_error(self) -> None:
        payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
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

        self.assertEqual(
            result,
            LlmDebriefError("The model did not return a usable insight. Try again or use a different model."),
        )

    def test_parser_caps_improvements_at_three(self) -> None:
        payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "improvements": [
                                    {"insight": "First card has a long list.", "action": "Split the first card."},
                                    {"insight": "Second card overlaps with the first.", "action": "Search both cards side by side."},
                                    {"insight": "Third card mixes two concepts.", "action": "Rewrite it as two prompts."},
                                    {"insight": "Fourth card should not render.", "action": "Do not show this."},
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
        self.assertEqual(len(result.improvements), 3)
        self.assertNotIn("Fourth card", " ".join(item.insight for item in result.improvements))

    def test_parser_rewrites_known_jargon(self) -> None:
        payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
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
        rendered = " ".join(tuple(part for item in result.improvements for part in (item.insight, item.action))).lower()
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

    def test_parser_rewrites_card_edit_slop(self) -> None:
        payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "improvements": [
                                    {
                                        "insight": "The protein card was labeled 'dense' and has weak wording.",
                                        "action": "Review separately.",
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
        rendered = " ".join((result.improvements[0].insight, result.improvements[0].action))
        self.assertNotIn("labeled", rendered)
        self.assertNotIn("dense", rendered)
        self.assertNotIn("weak wording", rendered)
        self.assertNotIn("Review separately", rendered)
        self.assertIn("many details", rendered)
        self.assertIn("clearer", rendered)

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

    def test_prompt_can_count_hard_reviews_as_misses(self) -> None:
        requests = []
        payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "improvements": [
                                    {
                                        "insight": "1 enzyme card appears in the missed-card evidence.",
                                        "action": "Open the enzyme card and check whether it asks for several facts.",
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

        result = build_llm_summary(
            [_entry(1, 2, 0, text="enzyme kinetics hard card")],
            AnkiLensConfig(llm_summary_enabled=True),
            miss_eases=(1, 2),
            api_key_getter=lambda _name: "test-key",
            env_file_getter=lambda _name: None,
            opener=opener,
        )

        self.assertIsNotNone(result)
        prompt = json.loads(requests[0].data.decode("utf-8"))["messages"][1]["content"]
        self.assertIn("Miss definition: Again and Hard review buttons count as misses.", prompt)
        self.assertIn("enzyme kinetics hard card", prompt)

if __name__ == "__main__":
    unittest.main()
