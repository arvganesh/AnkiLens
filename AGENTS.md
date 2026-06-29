# AGENTS.md instructions for /Users/arvgan/Documents/Projects/anki-missed-card-analytics

## Product Direction

- This is an AnkiLens product direction: an Anki insights add-on, not a generic
  "missed card checker."
- The working product idea is: turn recent missed-card review history for one
  selected deck into trustworthy, readable study insights.
- The main user loop should be:
  1. Select a deck.
  2. Select a time window.
  3. See visible evidence from real review logs.
  4. Read concise LLM-generated insight grounded in that evidence.
  5. Decide what to review, inspect, edit, or ignore.
- Prioritize trust and usefulness over AI novelty. The LLM should interpret
  visible facts, not feel like it is inventing advice from nowhere.
- Keep the product calm, fast, direct, and low-friction.
- Do not shame the learner. Avoid language implying laziness, failure, or that
  the student must simply "study harder."

## Product Naming

- Use "AnkiLens" for repository, package, and product naming.
- User-facing interface copy can use "Insights" or "Missed Card Insights" where
  that is clearer or shorter than repeating the product name.

## Scope And Safety

- The add-on is read-only.
- Do not change Anki scheduling.
- Do not mutate notes, cards, decks, or revlog data.
- Do not add advanced Anki features unless explicitly requested.
- Do not infer medical, factual, or scheduling conclusions from card content.
  The add-on can say what missed cards appear to have in common; it should not
  tell the user that a medical statement is true, that they know or do not know
  a fact, or that Anki scheduling should be changed.
- Do not hardcode secrets. API keys belong in local ignored env/config files,
  not committed source or docs.

## UX Principles

- The primary screen should feel like analytics with interpretation, not a chat
  response or a free-form AI essay.
- Always ground LLM output with visible data: counts, miss rate, deck, and time
  window.
- Prefer structured-but-readable output. Current preferred shape:
  - `Based on analysis of the last X reviews:`
  - `What you're doing well`
  - `Areas for improvement`
  - concrete `Try:` actions
- Avoid examples lists unless the user asks for them. Long example lists make
  the UI unreadable as card volume grows.
- Avoid implementation jargon in UI and LLM output, including "cue wording,"
  "source text," "tag artifact," and "prompt injection."
- Avoid generic AI phrasing. Be specific to the selected deck/window and use
  plain student-facing language.
- Do not show cross-deck summaries unless explicitly requested. The current
  product should focus on one selected deck at a time.
- Use native Anki/page styling where practical. The UI should integrate with
  Anki rather than feel like a separate branded app.

## LLM Pipeline Expectations

- Input should come from real review history scoped to the selected deck and
  selected time window.
- The LLM input should include enough card content to identify patterns, but
  respect configured card and character limits.
- The prompt should ask for grounded pattern recognition, not medical advice,
  factual verification, or scheduling recommendations.
- Prefer strict structured output from the model, then render it as polished
  interface copy. Do not expose JSON-like labels directly to the user.
- Handle async LLM requests carefully:
  - show a loading state,
  - ignore stale responses when deck/window changes,
  - show a clear failure or empty state if no insight is returned.
- Cheapest paid models are acceptable for prototyping, but keep model choice in
  config so it can be changed without code edits.

## Demo And Test Data

- Demo decks should use realistic card text, not placeholder names such as
  "demo card 6."
- Demo review logs should intentionally support expected insights so the UI can
  be tested end to end.
- When demo data is enabled, it should make the feature understandable even if
  the user's real Anki profile has no recent misses.
- Keep expected demo insights documented in code/tests so future agents know
  what the LLM should plausibly pick up.

## Architecture

- Keep Anki UI code thin.
- Put testable product logic in plain Python modules outside Anki-specific UI
  glue.
- If new Anki APIs are needed, add the smallest fake API surface in tests before
  relying on it in product logic.
- Prefer simple modules and direct data models over premature abstractions.
- Maintain agent legibility: names should make product behavior obvious to a
  future agent with little context.

## Repository Map

- `addon/` - Anki add-on source.
- `addon/anki_entry.py` - Anki hook/page entrypoint and webview message bridge.
- `addon/anki_gateway.py` - Anki review-log adapter and card text cleanup.
- `addon/anki_browser.py` - Browse search construction and Browser opening.
- `addon/debrief.py` - Small evidence and LLM insight data models.
- `addon/debrief_page.py` - Main Insights page HTML/CSS/JS rendering.
- `addon/llm_summary.py` - LLM prompt, request, parsing, and cleanup logic.
- `addon/demo_data.py` - Realistic demo card and review-log generation.
- `addon/config.py` and `addon/config.json` - Local add-on configuration.
- `tests/` - Pure Python tests that should not require a live Anki GUI.
- `tests/fake_anki.py` - Minimal fake Anki collection surface for tests.
- `docs/anki_ui_verification.md` - Current Anki visual QA notes and limitations.
- `docs/post_session_debrief.md` - Historical and future-direction notes. Treat
  as planning context; the current direction is LLM-grounded deck insights.

## Local Development

- The add-on can be symlinked into Anki:

```sh
ln -s "$(pwd)/addon" "$HOME/Library/Application Support/Anki2/addons21/ankilens"
```

- Existing local symlink expected during development:

```text
~/Library/Application Support/Anki2/addons21/ankilens -> /Users/arvgan/Documents/Projects/anki-missed-card-analytics/addon
```

- Anki usually needs to be restarted after Python hook/callback changes.
- Web/page copy and CSS changes may still require reload/reopen depending on
  how the page is mounted.

## Verification

- Run tests before finishing code changes:

```sh
make test
```

- For larger docs-only edits, at least run:

```sh
git diff --check
```

- For UI work, verify in the actual Anki app when possible. Use
  `docs/anki_ui_verification.md` for current visual QA constraints.
- If visual capture fails, state the gap clearly and report the process/symlink
  evidence instead of claiming visual verification.

## Git And Change Hygiene

- The worktree may be dirty. Do not revert user changes unless explicitly
  requested.
- Keep edits scoped to the requested product slice.
- Do not commit `.env`, API keys, generated caches, or local Anki profile data.
- If making many changes, prefer small, legible commits that preserve the story
  of the product iteration.
