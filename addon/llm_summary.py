from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

try:
    from .analytics import DEFAULT_MISS_EASES, HARD_EASE, ReviewLogEntry, summarize_missed_cards
    from .config import AnkiLensConfig
    from .debrief import LlmDebriefError, LlmDebriefSummary, LlmImprovement
except ImportError:
    from analytics import DEFAULT_MISS_EASES, HARD_EASE, ReviewLogEntry, summarize_missed_cards
    from config import AnkiLensConfig
    from debrief import LlmDebriefError, LlmDebriefSummary, LlmImprovement


_SYSTEM_PROMPT = """You are a friendly study assistant helping someone make their Anki cards easier to improve.
Write short, human, practical "Areas for improvement" bullets from the supplied missed-card evidence.
Use only the supplied missed-card data. Do not infer medical, factual, or scheduling conclusions.
Do not write positive, reassuring, or calibrating bullets. The UI already handles that separately.

The reader should immediately understand:
1. what kind of card is causing trouble,
2. why that card type is hard to answer,
3. what to change in Anki.

Return at most three improvements, ordered from most impactful fix to least impactful fix.
Each improvement has two fields:
- insight: the fixable problem in plain language.
- action: one concrete next step the learner can do in Anki.

Write the insight like this:
- Start with the problem, not a statistic.
- Use stats only when they make the impact obvious.
- Avoid exact ratios like "3 times out of 5 reviews" unless the ratio is the point.
- Mention at most two example cards or topics.
- Avoid long parenthetical lists.

Examples of good vs not good insight writing:
Not good: "3 cards (mast cell, smooth ER role, amino acid components) each missed 3 of 5 reviews."
Good: "Several missed cards ask for long lists of facts, like cell features or organelle roles."

Not good: "Epithelium and connective tissue cards cluster together."
Good: "Similar tissue cards are hard to tell apart because they ask for location, shape, and function in the same answer."

Not good: "A protein card was missed 2 times and is dense."
Good: "One protein-structure card asks about several levels at once, which makes the answer hard to pull apart."

In the good insight examples, notice:
- The sentence starts with the fixable card problem.
- Counts are omitted unless they make the problem clearer.
- Examples are short and only support the main point.
- The wording explains why the card is hard to answer.

Write the action like this:
- Start with a concrete verb: Open, Split, Rewrite, Search, or Put.
- Say exactly what to change, not just "review more" or "study separately."
- Prefer card edits when a card asks for too many facts at once.

Examples of good action writing:
Not good: "Review the tissue cards separately."
Good: "Search for the epithelium cards and put them next to each other before adding connective tissue cards."

Not good: "Inspect the protein card."
Good: "Open the protein-structure card and split it into one card for each structure level."

Not good: "Focus on long lists."
Good: "Open those list cards and split each one so it asks for one fact at a time."

In the good action examples, notice:
- The action says exactly what to open, split, rewrite, search for, or put together.
- The action can be done inside Anki without needing extra context.
- The action avoids vague advice like "study harder" or "review more."

Avoid jargon, metaphors, and model-ish phrasing.
Do not use phrases like "card cluster", "dense overlap", "pacing concerns", "stabilize recognition", "recall spoon", "memory bucket", or "mental model".
Do not say the student understands, forgot, failed, mastered, or retained something.
Do not claim the card content is medically or factually correct.

Return only JSON with this shape:
{
  "improvements": [
    {
      "insight": "short grounded improvement",
      "action": "short concrete way to apply it"
    }
  ]
}"""

_LLM_TEMPERATURE = 0


def build_llm_summary(
    entries: list[ReviewLogEntry],
    config: AnkiLensConfig,
    *,
    miss_eases: tuple[int, ...] = DEFAULT_MISS_EASES,
    api_key_getter: Callable[[str], str | None] = os.environ.get,
    env_file_getter: Callable[[str], str | None] | None = None,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> LlmDebriefSummary | LlmDebriefError | None:
    if not config.llm_summary_enabled:
        return None
    current_env_file_getter = env_file_getter or _env_file_value
    api_key = config.llm_api_key or api_key_getter(config.llm_api_key_env) or current_env_file_getter(config.llm_api_key_env)
    if not api_key:
        return None
    summaries = summarize_missed_cards(entries, minimum_misses=1, limit=config.llm_max_cards, miss_eases=miss_eases)
    if not summaries:
        return None
    user_prompt = _missed_card_prompt(entries, summaries, max_chars=config.llm_max_chars, miss_eases=miss_eases)

    request = urllib.request.Request(
        config.llm_api_url,
        data=_request_body(config.llm_model, user_prompt),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/openai/codex",
            "X-Title": "Missed Card Insights",
        },
        method="POST",
    )
    try:
        with opener(request, timeout=config.llm_timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return LlmDebriefError(_http_error_message(error.code))
    except (urllib.error.URLError, TimeoutError):
        return LlmDebriefError("Could not reach OpenRouter. Check the connection and try again.")
    except Exception:
        return LlmDebriefError("Could not generate insights. Try again in a moment.")
    summary = _parse_response(payload, action_card_ids=tuple(summary.card_id for summary in summaries))
    if summary is None:
        return LlmDebriefError("The model did not return a usable insight. Try again or use a different model.")
    return summary


def _http_error_message(status_code: int) -> str:
    if status_code in (401, 403):
        return "OpenRouter rejected the API key. Check the key and try again."
    if status_code == 429:
        return "OpenRouter rate-limited the request. Try again later."
    return f"OpenRouter request failed with status {status_code}. Try again later."


def _request_body(model: str, user_prompt: str) -> bytes:
    return json.dumps(
        {
            "model": model,
            "messages": (
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ),
            "temperature": _LLM_TEMPERATURE,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "missed_card_insight",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "improvements": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "insight": {"type": "string"},
                                        "action": {"type": "string"},
                                    },
                                    "required": ["insight", "action"],
                                    "additionalProperties": False,
                                },
                                "minItems": 1,
                                "maxItems": 3,
                            },
                        },
                        "required": ["improvements"],
                        "additionalProperties": False,
                    },
                },
            },
        }
    ).encode("utf-8")


def _missed_card_prompt(entries, summaries, *, max_chars: int, miss_eases: tuple[int, ...] = DEFAULT_MISS_EASES) -> str:
    lines = [
        "Write student-facing insights about these missed Anki cards.",
        f"Miss definition: {_miss_definition(miss_eases)}.",
        "Focus on content patterns in the missed-card evidence, not overall review performance.",
        "Include supported counts in the bullets.",
        f"The numbered evidence below includes {len(summaries)} missed-card examples before any prompt character cap.",
        "Do not mention a different analyzed-example count unless it is directly visible in the numbered evidence.",
        "Do not include example card labels in the final answer.",
        "",
        "Missed-card evidence:",
    ]
    used = sum(len(line) + 1 for line in lines)
    for index, summary in enumerate(summaries, start=1):
        text = _compact_text(summary.source_text, 700)
        item = (
            f"{index}. label={summary.card_label!r}; deck={summary.deck_name!r}; "
            f"misses={summary.misses}; review_events_for_card={summary.total_reviews}; tags={list(summary.tags)!r}; "
            f"content_labels={list(summary.content_labels)!r}; early={summary.is_early_exposure}; "
            f"content={text!r}"
        )
        if used + len(item) + 1 > max_chars:
            lines.append(f"... {len(summaries) - index + 1} more missed cards omitted by prompt cap.")
            break
        lines.append(item)
        used += len(item) + 1
    return "\n".join(lines)


def _miss_definition(miss_eases: tuple[int, ...]) -> str:
    if HARD_EASE in miss_eases:
        return "Again and Hard review buttons count as misses"
    return "only Again review buttons count as misses"


def _parse_response(payload: dict[str, Any], *, action_card_ids: tuple[int, ...] = ()) -> LlmDebriefSummary | None:
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
    improvements = tuple(_improvements(data.get("improvements")))
    if not improvements:
        return None
    return LlmDebriefSummary(positives=(), improvements=improvements, action_card_ids=action_card_ids)


def _improvements(value: Any) -> list[LlmImprovement]:
    improvements = []
    for item in _list(value)[:3]:
        if not isinstance(item, dict):
            continue
        insight = _plain_language_string(item.get("insight"), max_length=220)
        action = _plain_language_string(item.get("action"), max_length=180)
        if insight and action:
            improvements.append(LlmImprovement(insight=insight, action=action))
    return improvements


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _clean_string(value: Any, *, max_length: int) -> str:
    if not isinstance(value, str):
        return ""
    cleaned = " ".join(value.split())
    if len(cleaned) <= max_length:
        return cleaned
    truncated = cleaned[:max_length].rsplit(" ", 1)[0].rstrip(".,;:")
    return f"{truncated}..." if truncated else cleaned[:max_length]


def _plain_language_string(value: Any, *, max_length: int) -> str:
    cleaned = _clean_string(value, max_length=max_length)
    replacements = {
        "cue wording": "wording",
        "cue words": "wording",
        "cue word": "wording",
        "cue": "wording",
        "content tag": "topic group",
        "topic tag": "topic group",
        "tag": "topic group",
        "deck artifact": "deck pattern",
        "artifact": "pattern",
        "source text": "card text",
        "rather than understanding concepts": "across related cards",
        "instead of understanding concepts": "across related cards",
        "wording phrasing": "phrasing",
        "causing repeated misses": "with repeated misses",
        "causing misses": "with misses",
        "creating confusion between": "appearing across",
        "so mixing up details is more likely during review": "which can make the cards feel similar during review",
        "reinforce accurate mental models": "make the related cards easier to compare",
        "accurate mental models": "the related ideas",
        "solid retention": "many cards had no misses",
        "retention": "cards with no misses",
        "successful reviews": "reviews without misses",
        "reviews are successful": "reviews had no misses",
        "successful": "with no misses",
        "overload or similarity issues": "too many similar facts on the same cards",
        "overload": "too much at once",
        "dense overlap": "many similar cards in the same area",
        "dense and harder to separate": "hard to tell apart",
        "set feel dense": "set feel crowded",
        "reduce density and interference": "make the groups easier to tell apart",
        "interference": "mix-ups",
        "pacing concerns": "too many similar cards at once",
        "pacing": "card volume",
        "Early review flags": "Early missed cards",
        "early review flags": "early missed cards",
        "labeled 'dense'": "with many details",
        'labeled "dense"': "with many details",
        "labelled 'dense'": "with many details",
        'labelled "dense"': "with many details",
        "weak wording": "a prompt that may need to be clearer",
        "Weak wording": "A prompt that may need to be clearer",
        "Review separately": "Open the card and make the prompt more specific",
        "review separately": "open the card and make the prompt more specific",
        "weak stability": "more misses",
        "Weak stability": "More misses",
        "Delay repeats until stability is seen": "Keep the next review to a smaller set of related cards",
        "delay repeats until stability is seen": "keep the next review to a smaller set of related cards",
        "stability": "fewer misses",
        "distinct review sessions": "separate small review groups",
        "distinct": "separate",
    }
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new).replace(old.title(), new)
    return cleaned


def _compact_text(value: str, max_length: int) -> str:
    cleaned = " ".join(value.split())
    return cleaned[:max_length]


def _env_file_value(name: str) -> str | None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    prefix = f"{name}="
    for line in lines:
        if line.startswith(prefix):
            value = line.removeprefix(prefix).strip()
            return value or None
    return None
