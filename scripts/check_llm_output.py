from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ADDON_DIR = ROOT / "addon"
sys.path.insert(0, str(ADDON_DIR))

from analytics import AGAIN_EASE, ReviewLogEntry  # noqa: E402
from config import AnkiLensConfig  # noqa: E402
from llm_summary import build_llm_summary  # noqa: E402


SAMPLE_CARDS = {
    "med-lists": [
        {
            "label": "Mast cell morphology",
            "text": "Front: Mast cell morphology. Back: round cell, central nucleus, basophilic granules, histamine release, allergy role.",
            "misses": 3,
            "reviews": 5,
        },
        {
            "label": "Smooth ER role",
            "text": "Front: Smooth ER role. Back: lipid synthesis, steroid synthesis, detoxification, calcium storage, glycogen metabolism.",
            "misses": 3,
            "reviews": 5,
        },
        {
            "label": "Amino acid components",
            "text": "Front: Components of amino acids. Back: amino group, carboxyl group, alpha carbon, hydrogen, variable R group.",
            "misses": 3,
            "reviews": 5,
        },
        {
            "label": "Pseudostratified columnar epithelium",
            "text": "Front: Pseudostratified columnar epithelium. Back: respiratory tract, cilia, goblet cells, mucus movement.",
            "misses": 2,
            "reviews": 4,
        },
        {
            "label": "Protein structure and disease",
            "text": "Front: Protein structure levels and disease links. Back: primary, secondary, tertiary, quaternary, misfolding disease examples.",
            "misses": 2,
            "reviews": 4,
        },
    ],
}

BLOCKED_OUTPUT_PHRASES = (
    "card cluster",
    "clusters",
    "dense overlap",
    "pacing concerns",
    "stabilize recognition",
    "recall spoon",
    "memory bucket",
    "mental model",
    "quality_check",
    "tagged",
    "tags",
    "source text",
    "cue wording",
    "prompt injection",
    "study harder",
    "groupged",
)


def main() -> None:
    args = _parser().parse_args()
    cards = _load_cards(args)
    entries = _entries_for_cards(cards)
    config = AnkiLensConfig(
        llm_summary_enabled=True,
        llm_model=args.model,
        llm_max_cards=args.max_cards,
        llm_max_chars=args.max_chars,
        llm_timeout_seconds=args.timeout,
    )

    result = build_llm_summary(entries, config, api_key_getter=os.environ.get)
    if result is None:
        raise SystemExit(f"No LLM result. Set {config.llm_api_key_env} or pass a valid environment.")
    error = getattr(result, "message", "")
    if error:
        raise SystemExit(error)

    print(f"Model: {config.llm_model}")
    print(f"Cards sent: {min(len(cards), config.llm_max_cards)}")
    print()
    print("Card improvements")
    for index, improvement in enumerate(result.card_improvements, start=1):
        print(f"{index}. {improvement.insight}")
        print(f"   Try: {improvement.action}")
    if result.study_suggestions:
        print()
        print("Study suggestions")
        for index, suggestion in enumerate(result.study_suggestions, start=1):
            print(f"{index}. {suggestion.insight}")
            print(f"   Try: {suggestion.action}")

    warnings = _quality_warnings((*result.card_improvements, *result.study_suggestions))
    print()
    if warnings:
        print("Quality warnings")
        for warning in warnings:
            print(f"- {warning}")
        if args.strict:
            raise SystemExit(2)
    else:
        print("Quality checks: OK")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Query the configured LLM with sample AnkiLens card content and print the generated insights.",
    )
    parser.add_argument(
        "--sample",
        choices=sorted(SAMPLE_CARDS),
        default="med-lists",
        help="Built-in sample content to send.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help='Optional JSON file with cards: [{"label": "...", "text": "...", "misses": 2, "reviews": 4}].',
    )
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash")
    parser.add_argument("--max-cards", type=int, default=30)
    parser.add_argument("--max-chars", type=int, default=10000)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when output quality warnings are found.")
    return parser


def _load_cards(args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.input is None:
        return list(SAMPLE_CARDS[args.sample])
    raw = json.loads(args.input.read_text())
    if not isinstance(raw, list):
        raise SystemExit("Input JSON must be a list of card objects.")
    cards = []
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise SystemExit(f"Card {index} must be an object.")
        label = _required_string(item, "label", index)
        text = _required_string(item, "text", index)
        misses = _positive_int(item.get("misses", 1), "misses", index)
        reviews = _positive_int(item.get("reviews", max(misses, 1)), "reviews", index)
        cards.append({"label": label, "text": text, "misses": misses, "reviews": max(reviews, misses)})
    return cards


def _required_string(item: dict[str, Any], key: str, index: int) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"Card {index} needs a non-empty {key!r}.")
    return value.strip()


def _positive_int(value: Any, key: str, index: int) -> int:
    if not isinstance(value, int) or value < 1:
        raise SystemExit(f"Card {index} needs a positive integer {key!r}.")
    return value


def _entries_for_cards(cards: list[dict[str, Any]]) -> list[ReviewLogEntry]:
    now = datetime.now()
    entries: list[ReviewLogEntry] = []
    for card_index, card in enumerate(cards, start=1):
        reviews = card["reviews"]
        misses = card["misses"]
        passes = max(0, reviews - misses)
        for review_index in range(passes):
            entries.append(_entry(card, card_index, now - timedelta(days=reviews + review_index), ease=3))
        for miss_index in range(misses):
            entries.append(_entry(card, card_index, now - timedelta(days=misses - miss_index), ease=AGAIN_EASE))
    return entries


def _entry(card: dict[str, Any], card_index: int, reviewed_at: datetime, *, ease: int) -> ReviewLogEntry:
    return ReviewLogEntry(
        card_id=700_000 + card_index,
        ease=ease,
        reviewed_at=reviewed_at,
        deck_name="LLM Quality Check",
        card_label=card["label"],
        note_id=800_000 + card_index,
        note_card_count=1,
        tags=("quality_check",),
        source_text=card["text"],
        review_type=2,
        card_reps=card["reviews"],
        card_lapses=card["misses"],
        card_type=2,
        card_queue=2,
    )


def _quality_warnings(improvements: Any) -> list[str]:
    warnings: list[str] = []
    seen: set[str] = set()
    for index, improvement in enumerate(improvements, start=1):
        for field_name, limit in (("insight", 150), ("action", 145)):
            text = getattr(improvement, field_name)
            lowered = text.lower()
            if len(text) > limit:
                warnings.append(f"Bullet {index} {field_name} is {len(text)} chars; limit is {limit}.")
            if "..." in text or text.endswith(("…", "." * 3)):
                warnings.append(f"Bullet {index} {field_name} appears truncated.")
            for phrase in BLOCKED_OUTPUT_PHRASES:
                if phrase in lowered:
                    warnings.append(f"Bullet {index} {field_name} contains blocked phrase: {phrase!r}.")
            normalized = _normalize_for_duplicate_check(text)
            if normalized in seen:
                warnings.append(f"Bullet {index} {field_name} looks redundant with an earlier line.")
            seen.add(normalized)
    return warnings


def _normalize_for_duplicate_check(text: str) -> str:
    words = [word.strip(".,;:()[]'\"").lower() for word in text.split()]
    ignored = {"the", "a", "an", "and", "or", "to", "of", "in", "for", "with", "that", "this", "those"}
    return " ".join(word for word in words if word and word not in ignored)


if __name__ == "__main__":
    main()
