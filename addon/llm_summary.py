from __future__ import annotations

from hashlib import sha256
import json
import os
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

try:
    from .analytics import DEFAULT_MISS_EASES, HARD_EASE, ReviewLogEntry, summarize_missed_cards
    from .config import AnkiLensConfig
    from .debrief import LlmDebriefSummary, LlmImprovement
except ImportError:
    from analytics import DEFAULT_MISS_EASES, HARD_EASE, ReviewLogEntry, summarize_missed_cards
    from config import AnkiLensConfig
    from debrief import LlmDebriefSummary, LlmImprovement


_SYSTEM_PROMPT = """You are a concise missed-card analytics assistant.
Write a short, useful insight card about the supplied Anki missed-card labels and card text.
Analyze the data through a memory-and-learning lens: look for cards with repeated misses, content that appears often in errors, and review-method signals such as overload, very similar cards, or many early-review misses.
Use only the supplied missed-card data. Do not infer medical, factual, or scheduling conclusions.
Use a number in each bullet when the supplied stats support it, such as cards with misses, repeated misses, total misses, or reviewed cards without misses.
Focus on content-driven insights from the missed-card evidence, not overall review volume.
Include positive or calibrating insights when supported by the stats, such as material that did not appear in the missed-card set or the share of reviewed cards without misses.
When only a capped missed-card subset is supplied, do not write positives like "out of 30 reviewed cards"; say "missed-card examples analyzed" or skip that positive.
Each positive bullet must make a distinct point. Do not write two positives that both mean "most reviews went well."
If two stats support the same point, combine them into one bullet instead of making separate bullets.
Do not say what the student understands, forgot, failed to process, retained, mastered, or should study for a specific duration.
Do not address the student as "you".
Avoid implementation terms like tag, cue wording, source text, prompt pattern, JSON, deck artifact, content_labels, early review flags, stability, retention, interference, pacing, dense label, and successful.
Never use the words "cue", "tag", "artifact", "source text", "retention", "interference", "stability", "successful", "labeled", "labelled", or "weak wording" in the output.
Do not say the student is relying on phrases instead of understanding concepts.
Do not claim the pattern caused the misses or created confusion.
If the data suggests leech-like repeated trouble, mention the number of repeated misses and that the card may ask for too much at once; do not recommend changing Anki scheduling.
If the data suggests too much similar material at once, name the similar cards and suggest reviewing one small group before another; do not prescribe a review duration.
For content difficulty, name the specific relationship among the cards that is likely making the set hard to separate, without claiming the underlying facts are true.
Do not list examples.
Prefer plain study language over analytics language.
Explain what the cluster means in practical terms.
Write compact UI copy for a single card with two sections: what is going well and areas for improvement.
Keep each bullet under 28 words.
Each improvement must have an insight and a directly usable action.
The insight should name one observation from the evidence.
The action should be concrete enough to do immediately, such as "Search for murmur cards and review only those first" or "Open the repeated card and split the drug list if it has several facts."
Use plain classroom language that a tired learner can act on quickly.
Avoid vague phrases like "next pass", "subtopics", "dense overlap", "overload", "optimize pacing", "pacing concerns", "stabilize recognition", "retention", "interference", "stability", or "mental model".
When suggesting bucketing, name the actual bucket examples, such as "murmur cards first, then drug side effects."
When suggesting a card edit, say exactly what to check, such as "one card asking for three toxicities" or "a prompt that asks for spelling, sound, and example at once."
Do not say only "review separately"; turn it into an immediate action, such as opening the card, rewriting the prompt, splitting a list, or searching two named cards side by side.
If wording seems unclear, say "may need a clearer prompt" instead of "weak wording."
Avoid generic openings like "Review", "Compare", "Inspect", "Focus on", or "Group" unless there is no clearer wording.
Use varied sentence structure so the bullets do not feel templated.
Return only JSON with this shape:
{
  "positives": [
    "short grounded positive or calibrating insight"
  ],
  "improvements": [
    {
      "insight": "short grounded improvement",
      "action": "short concrete way to apply it"
    }
  ]
}"""

_LLM_TEMPERATURE = 0
_SUMMARY_CACHE: dict[str, LlmDebriefSummary] = {}


def build_llm_summary(
    entries: list[ReviewLogEntry],
    config: AnkiLensConfig,
    *,
    miss_eases: tuple[int, ...] = DEFAULT_MISS_EASES,
    api_key_getter: Callable[[str], str | None] = os.environ.get,
    env_file_getter: Callable[[str], str | None] | None = None,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> LlmDebriefSummary | None:
    if not config.llm_summary_enabled:
        return None
    current_env_file_getter = env_file_getter or _env_file_value
    api_key = api_key_getter(config.llm_api_key_env) or current_env_file_getter(config.llm_api_key_env)
    if not api_key:
        return None
    summaries = summarize_missed_cards(entries, minimum_misses=1, limit=config.llm_max_cards, miss_eases=miss_eases)
    if not summaries:
        return None
    user_prompt = _missed_card_prompt(entries, summaries, max_chars=config.llm_max_chars, miss_eases=miss_eases)
    cache_key = _summary_cache_key(config.llm_model, user_prompt, entries, miss_eases=miss_eases)
    cached_summary = _SUMMARY_CACHE.get(cache_key)
    if cached_summary is not None:
        return cached_summary

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
    except Exception:
        return None
    summary = _parse_response(payload, action_card_ids=tuple(summary.card_id for summary in summaries))
    if summary is not None:
        _SUMMARY_CACHE[cache_key] = summary
    return summary


def clear_llm_summary_cache() -> None:
    _SUMMARY_CACHE.clear()


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
                            "positives": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 0,
                                "maxItems": 3,
                            },
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
                                "maxItems": 4,
                            },
                        },
                        "required": ["positives", "improvements"],
                        "additionalProperties": False,
                    },
                },
            },
        }
    ).encode("utf-8")


def _summary_cache_key(
    model: str,
    user_prompt: str,
    entries: list[ReviewLogEntry],
    *,
    miss_eases: tuple[int, ...],
) -> str:
    event_fingerprint = tuple(
        sorted(
            (
                entry.card_id,
                entry.ease,
                entry.reviewed_at.isoformat(),
                entry.deck_name,
                entry.card_label,
            )
            for entry in entries
        )
    )
    payload = {
        "model": model,
        "temperature": _LLM_TEMPERATURE,
        "miss_eases": miss_eases,
        "system_prompt": _SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "events": event_fingerprint,
    }
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _missed_card_prompt(entries, summaries, *, max_chars: int, miss_eases: tuple[int, ...] = DEFAULT_MISS_EASES) -> str:
    lines = [
        "Write student-facing insights about these missed Anki cards.",
        f"Miss definition: {_miss_definition(miss_eases)}.",
        "Focus on content patterns in the missed-card evidence, not overall review performance.",
        "Include supported counts in the bullets.",
        "Include positives only when the stats support them.",
        "Do not repeat the same positive in different words; combine overlapping stats into one bullet.",
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
    positives = tuple(
        item
        for item in (
            _plain_language_string(item, max_length=260)
            for item in _list(data.get("positives"))[:3]
        )
        if item
    )
    improvements = tuple(_improvements(data.get("improvements")))
    if not improvements:
        return None
    return LlmDebriefSummary(positives=positives, improvements=improvements, action_card_ids=action_card_ids)


def _improvements(value: Any) -> list[LlmImprovement]:
    improvements = []
    for item in _list(value)[:4]:
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
