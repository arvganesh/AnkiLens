# AnkiLens

AnkiLens is a read-only Anki add-on for reviewing missed cards.

Pick a deck, choose a time window, and AnkiLens shows a short summary of what
has been going well and which missed cards may be worth checking next. It uses
your recent review history and missed-card text, but it does not change Anki
scheduling or edit any cards.

## What It Does

- Looks at recent reviews for one deck at a time.
- Supports 7, 30, and 90 day windows.
- Summarizes missed cards in plain language.
- Shows what went well and where to focus.
- Opens the relevant missed cards in Anki Browse.
- Stays read-only: no scheduling, card, note, deck, or review-log changes.

## Local Setup

Symlink the add-on into Anki:

```sh
ln -s "$(pwd)/addon" "$HOME/Library/Application Support/Anki2/addons21/ankilens"
```

Restart Anki after Python changes.

## Configuration

Configuration lives in `addon/config.json`.

Useful settings:

- `llm_summary_enabled`: turns generated insights on or off.
- `llm_model`: model name.
- `llm_api_url`: chat-completions compatible API endpoint.
- `llm_api_key_env`: environment variable that contains the API key.
- `llm_max_cards`: maximum missed cards sent for summarization.
- `llm_max_chars`: maximum prompt size.
- `demo_data_enabled`: adds local demo review data.

The default API key environment variable is:

```sh
OPENROUTER_API_KEY
```

Do not commit API keys.

## Development

Run tests with:

```sh
make test
```

The tests do not require a live Anki GUI.

## Code Map

- `addon/anki_entry.py` - Anki menu, toolbar, page loading, and webview messages.
- `addon/anki_gateway.py` - reads Anki review logs and cleans card text.
- `addon/anki_browser.py` - builds Browse searches and opens Anki Browse.
- `addon/analytics.py` - turns review logs into missed-card summaries.
- `addon/debrief.py` - small data models for evidence and generated insights.
- `addon/debrief_page.py` - the Insights page HTML/CSS/JS.
- `addon/llm_summary.py` - prompt, API request, and response parsing.
- `addon/demo_data.py` - local demo review history.
- `tests/` - unit tests for the core behavior.
- `docs/` - notes for verification and future work.
