from __future__ import annotations


def browser_search_for_card(card_id: int) -> str:
    return f"cid:{card_id}"


def browser_search_for_study_target(kind: str, label: str, card_ids: tuple[int, ...] = ()) -> str:
    if card_ids:
        return " or ".join(f"cid:{card_id}" for card_id in card_ids)
    if kind == "tag":
        return f"tag:{_search_value(label)} -is:suspended"
    if kind == "deck":
        return f"deck:{_quoted(label)}"
    if kind == "term":
        return f"w:{_search_value(label)}"
    return _search_value(label)


def _search_value(value: str) -> str:
    if value and value[0] != "-" and all(character.isalnum() or character in "_:#./-" for character in value):
        return value
    return _quoted(value)


def _quoted(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
