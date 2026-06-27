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

The Recent Debrief currently leads with a single card:

- Title example: `Relearning signal: Cardiology Valves`.
- Primary action example: `Show missed examples`.
- Evidence appears below the action under `What Bonsai saw`, split into short lines.
- Safety copy appears under `Before studying more`.
- Secondary cards use ranked language such as `Also check...` or `Ignore for now...`.

Recent UI simplifications:

- Removed `See supporting cards` from the Anki deck panel.
- Removed `See supporting cards` from the debrief.
- Kept the debrief action button compact and left-aligned.
- Removed the high-Again-rate session note because it duplicated the main signal.
- Changed material actions to open exact missed examples when possible.

## Latest Completed Slice

The latest committed slice makes `Show related cards` more precise.

Behavior:

- `StudyTarget` now carries `related_card_ids` for the missed example cards already shown in the debrief.
- Browser search prefers exact missed examples when those IDs exist:
  - `cid:123 or cid:456`
- Broad target search remains the fallback:
  - `tag:... -is:suspended`
  - `deck:"..."`
  - `w:...`
- The debrief button says `Show missed examples` when the action opens exact cards.

Why:

- For large AnKing tags, opening the whole tag is too broad.
- The useful action is to inspect the specific missed examples behind Bonsai's recommendation.

Commit:

- `55822b2` Focus debrief action on missed examples

## Verification

Latest automated verification before this handoff:

```sh
make test
```

Result:

- 166 tests passed.

Also run before commits:

```sh
git diff --check
```

Visual verification:

- Use Computer Use `get_app_state("Anki")`.
- Do not rely on terminal `screencapture`; it captures the Codex desktop/wallpaper in this environment.
- The documented workflow is in `docs/anki_ui_verification.md`.

## Known Caveats

- The running Anki process can keep old Python modules in memory.
- Some changes, especially `anki_entry.py`, dataclass shape changes, and loader-list changes, may require restarting Anki.
- The deck page can remain stale after code changes until Anki/deck browser rerenders.
- The dense `Bonsai Details` / missed-card table still exists via the Tools menu, but it is not part of the primary debrief flow.

## Recent Commits

- `55822b2` Focus debrief action on missed examples
- `22fad1f` Hide non-actionable session miss rate note
- `259d3cb` Remove dense details link from debrief
- `7ed70a3` Keep debrief action buttons compact
- `512d6ac` Remove details button from deck panel
- `b8f8372` Reload deck button modules during render
- `73f8d53` Document Anki visual QA path
- `9ff2570` Clarify supporting cards path
- `9c7e750` Reload debrief dialog modules in Anki
- `c5f71a5` Clarify tag study recommendation titles

## Suggested Next Steps

1. Restart Anki to pick up the latest loader/model changes.
2. Open `Analyze missed cards` on the Test Deck.
3. Confirm the primary action says `Show missed examples`.
4. Click it and confirm Browse opens the exact missed cards, not the whole tag.
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
