from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BonsaiConfig:
    minimum_misses: int = 2
    result_limit: int = 20
    lookback_days: int = 90
    debrief_lookback_days: int = 1
    llm_summary_enabled: bool = False
    llm_model: str = "openrouter/free"
    llm_api_url: str = "https://openrouter.ai/api/v1/chat/completions"
    llm_api_key_env: str = "OPENROUTER_API_KEY"
    llm_max_cards: int = 40
    llm_max_chars: int = 12000
    llm_timeout_seconds: int = 20


def load_config(raw_config: dict[str, Any] | None) -> BonsaiConfig:
    raw = raw_config or {}
    return BonsaiConfig(
        minimum_misses=_bounded_int(raw.get("minimum_misses"), default=2, low=1, high=25),
        result_limit=_bounded_int(raw.get("result_limit"), default=20, low=1, high=200),
        lookback_days=_bounded_int(raw.get("lookback_days"), default=90, low=0, high=3650),
        debrief_lookback_days=_bounded_int(raw.get("debrief_lookback_days"), default=1, low=0, high=30),
        llm_summary_enabled=_bool(raw.get("llm_summary_enabled"), default=False),
        llm_model=_string(raw.get("llm_model"), default="openrouter/free", max_length=120),
        llm_api_url=_string(
            raw.get("llm_api_url"),
            default="https://openrouter.ai/api/v1/chat/completions",
            max_length=300,
        ),
        llm_api_key_env=_string(raw.get("llm_api_key_env"), default="OPENROUTER_API_KEY", max_length=80),
        llm_max_cards=_bounded_int(raw.get("llm_max_cards"), default=40, low=1, high=200),
        llm_max_chars=_bounded_int(raw.get("llm_max_chars"), default=12000, low=1000, high=60000),
        llm_timeout_seconds=_bounded_int(raw.get("llm_timeout_seconds"), default=20, low=3, high=90),
    )


def _bounded_int(value: Any, *, default: int, low: int, high: int) -> int:
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return min(max(parsed, low), high)


def _bool(value: Any, *, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    return default


def _string(value: Any, *, default: str, max_length: int) -> str:
    if not isinstance(value, str):
        return default
    stripped = value.strip()
    if not stripped:
        return default
    return stripped[:max_length]
