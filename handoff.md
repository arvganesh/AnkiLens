# Bonsai Anki Extension Handoff

## Goal For The Next Agent

Continue iterating on the Bonsai Anki add-on as a calm, trustworthy post-study
assistant. Optimize for a small ranked set of genuinely useful actions after
missed cards, not for a broad analytics dashboard.

Primary product questions:

- Is this a bad card the user should inspect/edit?
- Is this normal early learning/newly encountered material?
- Is this genuinely unlearned, lapsed, or relearning material worth revisiting?

Product bar:

- Clear hierarchy.
- Minimal cognitive load.
- No generic stats unless they directly change what the user should do next.
- Prefer removing distracting UI over adding explanatory UI.
- Keep copy cautious: Bonsai suggests checks; it should not overclaim causality.

## Useful Skills And Process

Use these Codex skills/processes when available:

- `ux-adversarial-review`: use before major product or UX direction changes.
- `ui-ux-designer`: use for visual hierarchy, spacing, affordance, and accessibility review.
- `computer-use`: use to inspect actual Anki UI with `get_app_state("Anki")`.

For major UX/product changes, spawn adversarial reviewers with these lenses:

- Med student using AnKing.
- New/confused Anki user.
- High-volume power user.
- UI/interaction polish reviewer.
- Skeptical learning-science/product reviewer.

For small copy/layout fixes, do not over-process. Inspect the live screen, make a
small change, test it, and commit.

## Agent Operating Advice

- Work in small commits. Aim for less than 150 lines of core logic per slice.
- Keep business/product logic testable outside Anki.
- Add or update unit tests for insight semantics and copy behavior.
- Do not add advanced Anki features unless they directly support the core next action.
- Prefer exact missed-card examples over broad deck/tag searches.
- Treat `Bonsai Details` as a low-priority fallback until redesigned.
- Be careful with Anki module caching: the running app may need restart after
  dataclass, loader, or entrypoint changes.
- Do not trust terminal screenshots for visual QA. Use Computer Use.

## Current Product Direction

Bonsai is being shaped into a calm post-study assistant, not a stats dashboard.
The main flow is:

1. The Anki deck page shows one primary Bonsai action: `Analyze missed cards`.
2. The debrief leads with the most useful check and may show a few secondary checks.
3. The recommendation distinguishes likely causes where possible:
   - problematic card format,
   - genuinely unlearned or lapsed material,
   - normal early learning/newly encountered material.
4. Dense analytics/details are intentionally de-emphasized until redesigned.

## Current Live UX

The Missed Cards debrief currently leads with a single card:

- Window heading: `Missed card analytics`.
- The deck-browser Bonsai panel includes a `Deck` dropdown with `All decks` plus decks seen in recent reviews.
- Selecting a deck scopes the panel count and the debrief to that deck for the current Anki session.
- Long nested deck names display as the last two path parts, for example `Zanki Biochemistry / Metabolism`.
- Title example: `Check missed examples from Cardiology Valves`.
- Signal badge example: `2 of 5 cards in this group needed another pass.`
- Primary action example: `Show 2 missed examples`.
- Lapsed-material next steps say `Check the missed examples first...` and explain when to inspect cards
  before studying more.
- Evidence appears below the action under `What Bonsai noticed`, with examples before the maturity breakdown.
- Safety copy appears under `Before studying more`.
- Secondary cards use ranked language such as `Also check...` or `Ignore for now...`.

Recent UI simplifications:

- Removed `See supporting cards` from the Anki deck panel.
- Removed `See supporting cards` from the debrief.
- Kept the debrief action button compact and left-aligned.
- Removed the high-Again-rate session note because it duplicated the main signal.
- Changed material actions to open exact missed examples when possible.
- Let secondary related-material panels open exact missed examples when Bonsai has those card IDs.
- Softened remaining `related cards` copy in the primary study path to `cards`, `examples`, or `missed examples`.
- Softened the secondary study support heading to `Also check cards`.
- Debrief action callbacks now close the dialog, then schedule Browse/open callbacks on the next Qt tick.
- Evidence examples are capped to two shortened labels plus `+N more missed cards` when the full missed
  set is larger than the visible examples.
- A repeatable E2E seeder now exists at `scripts/seed_e2e_deck.py`. It creates a named
  `Bonsai E2E Large Review Window` deck with 300 cards and 380 review-log rows.
- The main heading changed from `Missed cards` to `Missed card analytics`.
- Exact-card recommendation titles now say `Check missed examples from...`.
- The signal badge no longer says `consistent enough to check`; larger supported patterns still show the
  concrete count, but avoid sounding like a diagnosis.
- The evidence label changed from `Why this came up` to `What Bonsai noticed`.
- Live Anki visual QA against the 380-review fixture showed the debrief rendering the new copy cleanly.
- Clicking `Show 3 missed examples` still cannot be visually verified through Computer Use because the tool
  returns `noWindowsAvailable` after the dialog closes.
- No-signal debriefs now use the eyebrow `No action` instead of `Check first`.

## Latest Completed Slice

The latest working slice adds an in-session deck-scope dropdown to the Bonsai deck panel.

Behavior:

- The panel dropdown sends `bonsai:deck:<encoded deck name>` and refreshes the deck browser.
- The panel count uses the selected deck when one is chosen; otherwise it uses all decks.
- The debrief uses the same selected deck scope and names it in the intro line.
- Long nested deck names are shortened in visible panel copy while retaining the full deck value internally.
- Live Anki visual QA verified `All decks` at 82 repeated misses, `Bonsai E2E Large Review Window` at 80,
  and `Zanki Biochemistry / Metabolism` with no repeated misses.
- No-signal debriefs now say `No action` above `No action needed yet`.
- Study-target evidence says `2 of 5 cards from Cardiology Valves...` instead of `related cards`.
- Lapsed exact-card next steps say `Check the missed examples first...`.
- Broad fallback buttons say `Show cards to check`.
- Secondary study support panels say `Also check cards` instead of `Also check related material`.
- If Browse cannot open a single exact `cid:` search, the fallback now says `Copied search for this card`
  instead of the generic `Anki Browse` wording.
- Debrief action callbacks are scheduled after dialog close so Browser opening does not race modal teardown.
- A 380-review workflow test covers many misses in one tag and verifies the exact-card target remains capped
  while the visible examples line stays short and names the hidden missed-card count truthfully.
- Supported large clusters now outrank tiny high-rate quick checks. In the real E2E profile, the debrief leads
  with `80 of 300 cards...` instead of the older `2 of 5 cards...` fixture.
- The deck-browser panel now counts all repeated missed cards in the lookback window instead of the display cap.
  In the real E2E profile, it changed from `20 cards needed another pass...` to `82 cards...`.
- Secondary study checks hide targets that render to the same student-facing label as the primary target.
  In the real E2E profile, this removed a redundant secondary `Cardiology Valves` check.
- Copy from the UI debate was applied: action-first heading, softer evidence language, and less diagnostic
  confidence wording.
- The exact missed-card Browse behavior is unchanged.

Why:

- The screen should answer what the student should do next within one glance.
- `related cards` and `open...` made the UI feel more mechanical and diagnostic than necessary.
- Secondary check headings should stay concrete and scan-friendly.
- Fallback Browse messages should name exact-card actions clearly when opening Browse fails.
- Browse actions should run after the debrief modal has started closing, not inside the same click stack.
- Long AnKing-style labels should not make `What Bonsai noticed` unreadable as study volume grows.
- If Bonsai shows only a few exact examples from a large cluster, the evidence should still acknowledge
  the full cluster size instead of implying only one hidden example exists.
- Real review windows should not let a tiny, high-rate cluster outrank a much better-supported pattern.
- The deck-browser panel should summarize the actual repeated-miss count, not the capped number of detail rows.
- If two internal tags render to the same readable concept, show only the stronger one; duplicate same-label
  secondary checks add clutter without changing the user's next action.
- `consistent enough to check` read like a statistical claim and made the screen feel more diagnostic than
  helpful; the badge should name the observed count and let the next step carry the advice.

Commit:

- See the latest git log entry.

## Verification

Latest automated verification before this handoff:

```sh
make test
```

Result:

- 201 tests passed.

Also run before commits:

```sh
git diff --check
```

Visual verification:

- Use Computer Use `get_app_state("Anki")`.
- Do not rely on terminal `screencapture`; it captures the Codex desktop/wallpaper in this environment.
- The documented workflow is in `docs/anki_ui_verification.md`.
- On June 27, 2026, a temporary `/tmp/bonsai_large_debrief_preview` hook was used and then removed to
  preview a 380-review / 80-miss workflow in the actual Anki dialog. The screen stayed readable with:
  `80 of 300 cards...`, `Show 3 missed examples`, and
  `Examples: Valve physiology missed example 239...; Valve physiology missed example 240...; +78 more missed cards.`
  After removing the hook and sentinel, the real profile dialog returned to the normal 2-card fixture.
- On June 27, 2026, `scripts/seed_e2e_deck.py` seeded a real Anki deck named
  `Bonsai E2E Large Review Window`. The script created backups at:
  `~/Library/Application Support/Anki2/User 1/collection.anki2.bonsai-e2e-backup-20260627-125139`
  and `~/Library/Application Support/Anki2/User 1/collection.anki2.bonsai-e2e-backup-20260627-125350`.
  Computer Use verified the deck browser showed `Studied 380 cards...`, the Bonsai panel showed
  `82 cards needed another pass...`, and the debrief led with `80 of 300 cards...` plus
  `Show 3 missed examples`.
- After the same-label duplicate suppression, Computer Use verified the real E2E debrief no longer showed the
  redundant `Also check cards` section for the smaller `Cardiology Valves` fixture.

## Known Caveats

- The running Anki process can keep old Python modules in memory.
- Some changes, especially `anki_entry.py`, dataclass shape changes, and loader-list changes, may require restarting Anki.
- The deck page can remain stale after code changes until Anki/deck browser rerenders.
- In the current Codex/Computer Use setup, clicking the debrief Browse action has intermittently returned `noWindowsAvailable`
  even though Browse is visible to the user. This reproduced after clicking `Show 2 missed examples` and again after
  clicking `Show 3 missed examples` in the real E2E deck; the clipboard was empty.
  Scheduling the callback after dialog close did not make Computer Use able to verify the transition in this session.
  Treat exact Browse visual proof as incomplete if this recurs.
- The dense `Bonsai Details` / missed-card table still exists via the Tools menu, but it is not part of the primary debrief flow.

## Recent Commits

- `782a3c5` Keep large debrief examples scannable
- `373f6f6` Name single-card Browse fallback
- `3eab6a0` Clarify secondary debrief checks
- `a213072` Soften missed-example debrief copy
- `f46f000` Name exact missed example count in Browse feedback
- `869d58c` Name exact missed example count in debrief actions
- `24e8851` Title exact example debriefs as checks
- `daa3886` Soften grouped-card debrief signal
- `2f22502` Promote debrief signal in recommendation card
- `55822b2` Focus debrief action on missed examples
- `22fad1f` Hide non-actionable session miss rate note

## Suggested Next Steps

1. Open `Analyze missed cards` on the Test Deck.
2. Confirm the primary action says `Show 2 missed examples` when exact card IDs exist.
3. Click it and confirm Browse opens the exact missed cards, not the whole tag.
4. If Browse cannot be verified through Computer Use, note the `noWindowsAvailable` limitation instead of claiming proof.
5. Next product slice: decide whether `Bonsai Details` should be redesigned as a focused card-inspection sheet or left as a low-priority Tools-menu fallback.

## Files To Read First

- `handoff.md` for current state and strategy.
- `docs/post_session_debrief.md` for product planning context.
- `docs/anki_ui_verification.md` for actual-app visual QA.
- `addon/debrief.py` for insight construction.
- `addon/debrief_dialog.py` and `addon/debrief_dialog_copy.py` for the primary UI/copy.
- `addon/browser_search.py` and `addon/anki_entry.py` for Browse actions.
- `tests/test_debrief.py`, `tests/test_debrief_dialog.py`,
  `tests/test_debrief_dialog_widgets.py`, and `tests/test_browser_search.py`
  for behavioral expectations.
