from __future__ import annotations


ReviewRow = tuple[int, int, int, int, int, int, int, int, int, int, str, str, str]


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


class FakeCollection:
    def __init__(
        self,
        rows: list[ReviewRow],
        deck_names: dict[int, str],
    ) -> None:
        self.db = FakeDb(rows)
        self.decks = FakeDecks(deck_names)


class FakeMainWindow:
    def __init__(
        self,
        rows: list[ReviewRow],
        deck_names: dict[int, str],
    ) -> None:
        self.col = FakeCollection(rows, deck_names)
