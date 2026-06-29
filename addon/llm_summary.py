from __future__ import annotations

import json
import os
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

try:
    from .analytics import AGAIN_EASE, ReviewLogEntry, summarize_missed_cards
    from .config import AnkiLensConfig
    from .debrief import LlmDebriefSummary, LlmImprovement
except ImportError:
    from analytics import AGAIN_EASE, ReviewLogEntry, summarize_missed_cards
    from config import AnkiLensConfig
    from debrief import LlmDebriefSummary, LlmImprovement


_SYSTEM_PROMPT = """You are a concise missed-card analytics assistant.
Write a short, useful insight card about the supplied Anki missed-card labels and card text.
Analyze the data through a memory-and-learning lens: look for cards with repeated misses, content that appears often in errors, and review-method signals such as overload, very similar cards, or many early-review misses.
Use the review-order stats to check whether misses are concentrated early, middle, or late in the review events.
Use only the supplied missed-card data. Do not infer medical, factual, or scheduling conclusions.
Use a number in each bullet when the supplied stats support it, such as cards with misses, repeated misses, total misses, or reviewed cards without misses.
Use "review events" for total review counts and "cards" for unique-card counts. Never call a unique-card count a review count.
Include positive or calibrating insights when supported by the stats, such as material that did not appear in the missed-card set or the share of reviewed cards without misses.
Each positive bullet must make a distinct point. Do not write two positives that both mean "most reviews went well."
If two stats support the same point, combine them into one bullet instead of making separate bullets.
Do not say what the student understands, forgot, failed to process, retained, mastered, or should study for a specific duration.
Do not address the student as "you".
Avoid implementation terms like tag, cue wording, source text, prompt pattern, JSON, deck artifact, content_labels, early review flags, stability, retention, interference, pacing, and successful.
Never use the words "cue", "tag", "artifact", "source text", "retention", "interference", "stability", or "successful" in the output.
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
When suggesting a card edit, say what to check, such as "one card asking for three toxicities."
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


def build_llm_summary(
    entries: list[ReviewLogEntry],
    config: AnkiLensConfig,
    *,
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
    summaries = summarize_missed_cards(entries, minimum_misses=1, limit=config.llm_max_cards)
    if not summaries:
        return None

    request = urllib.request.Request(
        config.llm_api_url,
        data=_request_body(config.llm_model, _missed_card_prompt(entries, summaries, max_chars=config.llm_max_chars)),
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
    return _parse_response(payload, action_card_ids=tuple(summary.card_id for summary in summaries))


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


def _missed_card_prompt(entries, summaries, *, max_chars: int) -> str:
    lines = [
        "Write student-facing insights about these missed Anki cards.",
        "Focus on practical study moves, not implementation details.",
        "Include supported counts in the bullets.",
        "Use review events for total review counts and cards for unique-card counts.",
        "Include positives only when the stats support them.",
        "Do not repeat the same positive in different words; combine overlapping stats into one bullet.",
        "Do not include example card labels in the final answer.",
        "",
        "Window stats:",
        *_review_stats_lines(entries, summaries),
        "",
        "Review-order stats:",
        *_review_order_stats_lines(entries),
        "",
        "Missed-card evidence:",
    ]
    used = sum(len(line) + 1 for line in lines)
    for index, summary in enumerate(summaries, start=1):
        text = _compact_text(summary.source_text, 700)
        item = (
            f"{index}. label={summary.card_label!r}; deck={summary.deck_name!r}; "
            f"misses={summary.misses}; reviews={summary.total_reviews}; tags={list(summary.tags)!r}; "
            f"content_labels={list(summary.content_labels)!r}; early={summary.is_early_exposure}; "
            f"content={text!r}"
        )
        if used + len(item) + 1 > max_chars:
            lines.append(f"... {len(summaries) - index + 1} more missed cards omitted by prompt cap.")
            break
        lines.append(item)
        used += len(item) + 1
    return "\n".join(lines)


def _review_stats_lines(entries, summaries) -> list[str]:
    reviewed_cards = len({entry.card_id for entry in entries})
    cards_with_misses = len({entry.card_id for entry in entries if entry.ease == AGAIN_EASE})
    missed_card_context = len({summary.card_id for summary in summaries})
    misses = sum(1 for entry in entries if entry.ease == AGAIN_EASE)
    reviews = len(entries)
    cards_without_misses = max(reviewed_cards - cards_with_misses, 0)
    return [
        f"- Review events: {reviews}.",
        f"- Unique cards reviewed: {reviewed_cards}.",
        f"- Unique cards with at least one miss: {cards_with_misses}.",
        f"- Unique cards with no misses: {cards_without_misses}.",
        f"- Misses: {misses} across {reviews} review {_plural(reviews, 'event')}.",
        f"- Missed cards included below for content analysis: {missed_card_context}.",
    ]


def _review_order_stats_lines(entries) -> list[str]:
    ordered = sorted(entries, key=lambda entry: entry.reviewed_at)
    if not ordered:
        return ["- No review events in this window."]
    lines = []
    first = ordered[:15]
    last = ordered[-15:] if len(ordered) > 15 else []
    lines.append(_event_group_line("First 15 review events", first))
    if last:
        lines.append(_event_group_line("Last 15 review events", last))
    if len(ordered) >= 9:
        third = max(len(ordered) // 3, 1)
        lines.extend(
            [
                _event_group_line("First third of review events", ordered[:third]),
                _event_group_line("Middle third of review events", ordered[third : third * 2]),
                _event_group_line("Last third of review events", ordered[third * 2 :]),
            ]
        )
    return lines


def _event_group_line(label: str, entries) -> str:
    misses = sum(1 for entry in entries if entry.ease == AGAIN_EASE)
    cards = len({entry.card_id for entry in entries})
    return f"- {label}: {misses} {_plural(misses, 'miss')} across {len(entries)} review {_plural(len(entries), 'event')} and {cards} unique {_plural(cards, 'card')}."


def _plural(count: int, word: str) -> str:
    if count == 1:
        return word
    if word == "miss":
        return "misses"
    if word == "event":
        return "events"
    return f"{word}s"


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
