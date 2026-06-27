from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BonsaiConfig:
    minimum_misses: int = 2
    result_limit: int = 20


def load_config(raw_config: dict[str, Any] | None) -> BonsaiConfig:
    raw = raw_config or {}
    return BonsaiConfig(
        minimum_misses=_bounded_int(raw.get("minimum_misses"), default=2, low=1, high=25),
        result_limit=_bounded_int(raw.get("result_limit"), default=20, low=1, high=200),
    )


def _bounded_int(value: Any, *, default: int, low: int, high: int) -> int:
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return min(max(parsed, low), high)
