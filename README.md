# Bonsai for Anki

A small Anki add-on for understanding missed cards without changing scheduling.

This repo is separate from the Bonsai Flutter app while that work is frozen. The
first goal is to iterate quickly inside Anki on read-only analytics for cards
that repeatedly need attention.

## Scope

- Read Anki review history.
- Highlight cards with repeated misses.
- Keep copy calm and non-shaming.
- Do not change scheduling.
- Do not mutate notes, cards, decks, or revlog data.

## Local Development

Install the add-on by symlinking or copying `addon/` into Anki's add-ons folder.
During local development, symlinking is easiest:

```sh
ln -s "$(pwd)/addon" "$ANKI_ADDONS_DIR/bonsai"
```

On macOS, Anki add-ons usually live under:

```txt
~/Library/Application Support/Anki2/addons21
```

Run pure Python tests without Anki:

```sh
make test
```

The Anki UI layer is intentionally thin. Most logic should live in
`addon/analytics.py` so it can be tested outside Anki.

## Testing Strategy

Tests do not require a live Anki GUI. `tests/fake_anki.py` provides the small
collection surface the add-on currently needs:

- `mw.col.db.all(...)`
- `mw.col.decks.name(deck_id)`

If new Anki APIs are needed, add the smallest matching fake and cover it with an
integration-style test before using it in product logic.
