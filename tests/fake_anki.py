from __future__ import annotations


ReviewRow = tuple[int, int, int, int, str, str, int]


class FakeDb:
    def __init__(self, rows: list[ReviewRow]) -> None:
        self.rows = rows
        self.queries: list[str] = []

    def all(self, query: str) -> list[ReviewRow]:
        self.queries.append(query)
        return self.rows


class FakeDecks:
    def __init__(self, names: dict[int, str]) -> None:
        self.names = names

    def name(self, deck_id: int) -> str | None:
        return self.names.get(deck_id)


class FakeModels:
    def __init__(self, names: dict[int, str]) -> None:
        self.names = names

    def get(self, note_type_id: int) -> dict[str, str] | None:
        name = self.names.get(note_type_id)
        return {"name": name} if name else None


class FakeCollection:
    def __init__(
        self,
        rows: list[ReviewRow],
        deck_names: dict[int, str],
        note_type_names: dict[int, str] | None = None,
    ) -> None:
        self.db = FakeDb(rows)
        self.decks = FakeDecks(deck_names)
        self.models = FakeModels(note_type_names or {})


class FakeMainWindow:
    def __init__(
        self,
        rows: list[ReviewRow],
        deck_names: dict[int, str],
        note_type_names: dict[int, str] | None = None,
    ) -> None:
        self.col = FakeCollection(rows, deck_names, note_type_names)
