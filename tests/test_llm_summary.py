from __future__ import annotations

import json
import unittest
from datetime import datetime

from analytics import ReviewLogEntry
from config import BonsaiConfig
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
            BonsaiConfig(llm_summary_enabled=False),
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
            BonsaiConfig(llm_summary_enabled=True),
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
                                "summary": "Several missed cards cluster around valve murmurs.",
                                "check_first": {
                                    "title": "Valve murmur examples",
                                    "why": "Multiple missed cards mention murmurs.",
                                    "examples": ["Card 1", "Card 2", "Card 3", "Card 4"],
                                    "action": "inspect_examples",
                                },
                                "other_checks": [
                                    {
                                        "title": "Ignore brand-new cards",
                                        "why": "Some examples may be early exposure.",
                                        "examples": ["Card 2"],
                                        "action": "ignore_for_now",
                                    }
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
            [_entry(1, 1, 0), _entry(2, 1, 1, text="mitral murmur")],
            BonsaiConfig(llm_summary_enabled=True, llm_max_chars=1000, llm_timeout_seconds=7),
            api_key_getter=lambda name: "test-key" if name == "OPENROUTER_API_KEY" else None,
            env_file_getter=lambda _name: None,
            opener=opener,
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.summary, "Several missed cards cluster around valve murmurs.")
        self.assertEqual(result.check_first.title, "Valve murmur examples")
        self.assertEqual(result.check_first.examples, ("Card 1", "Card 2", "Card 3"))
        self.assertEqual(result.other_checks[0].action, "ignore_for_now")
        self.assertEqual(requests[0][1], 7)
        request = requests[0][0]
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
        self.assertEqual(request.get_header("X-title"), "Bonsai Missed Card Analytics")
        body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(body["model"], "openrouter/free")
        self.assertEqual(body["response_format"]["type"], "json_schema")
        self.assertIn("Card 1", body["messages"][1]["content"])
        self.assertIn("aortic stenosis murmur", body["messages"][1]["content"])

    def test_invalid_model_action_drops_check(self) -> None:
        payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "summary": "A valid summary.",
                                "check_first": {
                                    "title": "Bad action",
                                    "why": "Grounded reason.",
                                    "examples": ["Card 1"],
                                    "action": "reschedule_cards",
                                },
                            }
                        )
                    }
                }
            ]
        }

        result = build_llm_summary(
            [_entry(1, 1, 0)],
            BonsaiConfig(llm_summary_enabled=True),
            api_key_getter=lambda _name: "test-key",
            env_file_getter=lambda _name: None,
            opener=lambda *_args, **_kwargs: _FakeResponse(payload),
        )

        self.assertIsNotNone(result)
        self.assertIsNone(result.check_first)


if __name__ == "__main__":
    unittest.main()
