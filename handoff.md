# Bonsai Anki Extension Handoff

## Current Product Direction

Bonsai is being shaped into a calm post-study assistant, not a stats dashboard.
The main flow is:

1. The Anki deck page shows one primary Bonsai action: `What should I check?`.
2. The debrief gives one recommended next check.
3. The recommendation distinguishes likely causes where possible:
   - problematic card format,
   - genuinely unlearned or lapsed material,
   - normal early learning/newly encountered material.
4. Dense analytics/details are intentionally de-emphasized until redesigned.

## Current Live UX

The Recent Debrief currently leads with a single card:

- Title example: `Relearning signal: Cardiology Valves`.
- Primary action example: `Show missed examples`.
- Evidence appears below the action under `Why`.
- Safety copy appears under `Double-check`.

Recent UI simplifications:

- Removed `See supporting cards` from the Anki deck panel.
- Removed `See supporting cards` from the debrief.
- Kept the debrief action button compact and left-aligned.
- Removed the high-Again-rate session note because it duplicated the main signal.

## Latest Uncommitted Slice

The current uncommitted change makes `Show related cards` more precise.

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
2. Open `What should I check?` on the Test Deck.
3. Confirm the primary action says `Show missed examples`.
4. Click it and confirm Browse opens the exact missed cards, not the whole tag.
5. Next product slice: decide whether `Bonsai Details` should be redesigned as a focused card-inspection sheet or left as a low-priority Tools-menu fallback.
