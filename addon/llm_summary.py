from __future__ import annotations

import json
import os
import urllib.request
from collections.abc import Callable
from typing import Any

try:
    from .analytics import ReviewLogEntry, summarize_missed_cards
    from .config import BonsaiConfig
    from .debrief import LlmCheck, LlmDebriefSummary
except ImportError:
    from analytics import ReviewLogEntry, summarize_missed_cards
    from config import BonsaiConfig
    from debrief import LlmCheck, LlmDebriefSummary


_SYSTEM_PROMPT = """You help a student interpret Anki cards they missed.
Use only the supplied missed-card data. Do not infer medical, factual, or scheduling conclusions.
Recommend checks the student can do, not diagnoses of why they failed.
Return only JSON with this shape:
{
  "summary": "one short sentence",
  "check_first": {
    "title": "short label",
    "why": "one sentence grounded in the supplied cards",
    "examples": ["card label", "card label"],
    "action": "inspect_examples"
  },
  "other_checks": [
    {
      "title": "short label",
      "why": "one sentence",
      "examples": ["card label"],
      "action": "review_material"
    }
  ]
}
Valid actions: inspect_examples, inspect_card, review_material, ignore_for_now.
Return at most two other_checks and at most three examples per check."""

_VALID_ACTIONS = frozenset({"inspect_examples", "inspect_card", "review_material", "ignore_for_now"})


def build_llm_summary(
    entries: list[ReviewLogEntry],
    config: BonsaiConfig,
    *,
    api_key_getter: Callable[[str], str | None] = os.environ.get,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> LlmDebriefSummary | None:
    if not config.llm_summary_enabled:
        return None
    api_key = api_key_getter(config.llm_api_key_env)
    if not api_key:
        return None
    summaries = summarize_missed_cards(entries, minimum_misses=1, limit=config.llm_max_cards)
    if not summaries:
        return None

    request = urllib.request.Request(
        config.llm_api_url,
        data=_request_body(config.llm_model, _missed_card_prompt(summaries, max_chars=config.llm_max_chars)),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/openai/codex",
            "X-Title": "Bonsai Missed Card Analytics",
        },
        method="POST",
    )
    try:
        with opener(request, timeout=config.llm_timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None
    return _parse_response(payload)


def _request_body(model: str, user_prompt: str) -> bytes:
    return json.dumps(
        {
            "model": model,
            "messages": (
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ),
            "temperature": 0.2,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "missed_card_summary",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "summary": {"type": "string"},
                            "check_first": {"$ref": "#/$defs/check"},
                            "other_checks": {
                                "type": "array",
                                "items": {"$ref": "#/$defs/check"},
                                "maxItems": 2,
                            },
                        },
                        "required": ["summary", "check_first", "other_checks"],
                        "additionalProperties": False,
                        "$defs": {
                            "check": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "why": {"type": "string"},
                                    "examples": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "maxItems": 3,
                                    },
                                    "action": {
                                        "type": "string",
                                        "enum": [
                                            "inspect_examples",
                                            "inspect_card",
                                            "review_material",
                                            "ignore_for_now",
                                        ],
                                    },
                                },
                                "required": ["title", "why", "examples", "action"],
                                "additionalProperties": False,
                            }
                        },
                    },
                },
            },
        }
    ).encode("utf-8")


def _missed_card_prompt(summaries, *, max_chars: int) -> str:
    lines = [
        "Summarize these missed Anki cards for a student.",
        "Focus on useful next checks across the card content and labels.",
        "",
    ]
    used = sum(len(line) + 1 for line in lines)
    for index, summary in enumerate(summaries, start=1):
        text = _compact_text(summary.source_text, 700)
        item = (
            f"{index}. label={summary.card_label!r}; deck={summary.deck_name!r}; "
            f"misses={summary.misses}; reviews={summary.total_reviews}; tags={list(summary.tags)!r}; "
            f"content={text!r}"
        )
        if used + len(item) + 1 > max_chars:
            lines.append(f"... {len(summaries) - index + 1} more missed cards omitted by prompt cap.")
            break
        lines.append(item)
        used += len(item) + 1
    return "\n".join(lines)


def _parse_response(payload: dict[str, Any]) -> LlmDebriefSummary | None:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    content = choices[0].get("message", {}).get("content")
    if not isinstance(content, str):
        return None
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return None
    summary = _clean_string(data.get("summary"), max_length=240)
    if not summary:
        return None
    return LlmDebriefSummary(
        summary=summary,
        check_first=_parse_check(data.get("check_first")),
        other_checks=tuple(
            check
            for check in (_parse_check(raw_check) for raw_check in _list(data.get("other_checks"))[:2])
            if check is not None
        ),
    )


def _parse_check(value: Any) -> LlmCheck | None:
    if not isinstance(value, dict):
        return None
    title = _clean_string(value.get("title"), max_length=80)
    why = _clean_string(value.get("why"), max_length=240)
    action = _clean_string(value.get("action"), max_length=40) or "inspect_examples"
    if not title or not why or action not in _VALID_ACTIONS:
        return None
    return LlmCheck(
        title=title,
        why=why,
        examples=tuple(
            example
            for example in (_clean_string(raw, max_length=80) for raw in _list(value.get("examples"))[:3])
            if example
        ),
        action=action,
    )


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _clean_string(value: Any, *, max_length: int) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())[:max_length]


def _compact_text(value: str, max_length: int) -> str:
    cleaned = " ".join(value.split())
    return cleaned[:max_length]
