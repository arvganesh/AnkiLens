# AnkiLens

AnkiLens is a read-only Anki add-on that turns recent missed-card review history
into grounded study insights.

The goal is simple: select a deck and time window, see evidence from real review
logs, and get concise recommendations about what to inspect or study next.
AnkiLens does not change scheduling, notes, cards, decks, or review history.

## What It Does

- Shows missed-card insights for one selected deck at a time.
- Supports time windows such as 7, 30, and 90 days.
- Uses review logs to count misses, reviewed cards, and repeated trouble spots.
- Sends capped missed-card evidence to an LLM when enabled.
- Renders calm, student-facing recommendations:
  - what is going well
  - areas for improvement
  - concrete `Try:` actions
- Opens the relevant missed cards in Anki Browse for inspection.
- Includes demo data for profiles without recent misses.

## Current Product Shape

The main page is designed around a low-friction loop:

1. Select a deck.
2. Select a time window.
3. Read recent missed-card insights.
4. Open the relevant missed cards in Browse.
5. Decide what to inspect, edit mentally, study, or ignore.

The LLM output is grounded in visible review-history facts. It should not make
medical claims, factual claims about card content, or scheduling recommendations.

## Safety And Scope

AnkiLens is intentionally read-only.

- It does not change Anki scheduling.
- It does not mutate notes, cards, decks, or revlog data.
- It does not suspend, bury, reschedule, or edit cards.
- It does not infer that the learner is lazy, failing, or should simply study
  harder.
- API keys should live in ignored local environment/config files, not committed
  source.

## Local Development

Install the add-on by symlinking or copying `addon/` into Anki's add-ons folder.
During local development, symlinking is easiest:

```sh
ln -s "$(pwd)/addon" "$HOME/Library/Application Support/Anki2/addons21/ankilens"
```

Anki usually needs to be restarted after Python hook or callback changes.

## Configuration

Local add-on configuration lives in `addon/config.json`.

Important options:

- `llm_summary_enabled`: enables LLM-generated insights.
- `llm_model`: model name sent to the configured API.
- `llm_api_url`: chat-completions compatible endpoint.
- `llm_api_key_env`: environment variable used for the API key.
- `llm_max_cards`: maximum missed-card summaries sent to the LLM.
- `llm_max_chars`: maximum prompt character budget.
- `demo_data_enabled`: adds realistic demo review logs for local testing.

The default API key environment variable is:

```sh
OPENROUTER_API_KEY
```

## Testing

Run pure Python tests without a live Anki GUI:

```sh
make test
```

The tests cover analytics, prompt construction, page rendering, fake Anki
integration surfaces, and page message handling.

## Repository Layout

- `addon/` - Anki add-on source.
- `addon/anki_entry.py` - Anki hook/page entrypoint and webview message bridge.
- `addon/debrief.py` - Pure insight/debrief data model and construction logic.
- `addon/debrief_page.py` - Main Insights page HTML/CSS/JS rendering.
- `addon/llm_summary.py` - LLM prompt, request, parsing, and cleanup logic.
- `addon/demo_data.py` - Realistic demo card and review-log generation.
- `tests/` - Pure Python tests that do not require a live Anki GUI.
- `docs/` - Verification notes and future product directions.

## Future Directions

For med-school scale use, AnkiLens should eventually summarize full review
windows with aggregate stats before the LLM sees representative examples. This
would help with 30-day windows containing thousands of review events and
hundreds of missed cards.

Future work is tracked in `docs/post_session_debrief.md`, including:

- review-event stats as visible evidence
- deterministic topic grouping before the LLM
- better cloze-note normalization for sibling cloze cards
- richer read-only Browse actions
