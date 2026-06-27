# Post-Session Debrief Plan

Bonsai should become most useful immediately after study, when the user is
already thinking about what went wrong. The debrief should stay read-only,
calm, and lightweight: it should explain patterns without changing scheduling,
notes, cards, decks, or review history.

## Product Shape

The debrief has three distinct buckets.

1. Study material
   - Purpose: identify content that may need more review after card quality has
     been checked.
   - Inputs: repeated terms, deck concentration, tag concentration, and related
     missed cards.
   - Initial output: top 3 study targets, expandable later into related cards.

2. Fix cards
   - Purpose: identify cards where construction may be causing repeated misses.
   - Inputs: content clues such as weak cue, long card, dense card, cloze-heavy,
     list-like, many numbers, media reference, and comparison.
   - Initial output: a quiet notice like "2 cards may need editing"; suggestions
     appear only when the user asks.

3. Session habits
   - Purpose: describe how the session went without judging the user.
   - Inputs: review count, Again count/rate, total time, average seconds/card,
     hardest deck/tag, and time of day.
   - Initial output: descriptive metrics only. Trend claims such as "evening
     sessions are harder" require enough history and should come later.

## Workflow

The debrief should make one relationship explicit:

Repeated misses can mean the card needs editing, the content needs more study,
or both. Bonsai should help the user check card quality before concluding that
they simply need to study harder.

For tag-driven decks such as AnKing, repeated misses can also mean the user
unsuspended material that matches class tags but has not actually learned the
underlying lecture/topic yet. Bonsai should frame the debrief as a decision:

- If construction clues are present, check the specific card first.
- If construction clues are absent and misses cluster around a tag/deck/topic,
  treat the cluster as material to study, not a card-edit diagnosis.
- If the cards are new or recently unsuspended, avoid over-interpreting early
  misses as either bad cards or weak knowledge.

## Initial Semantics

For the first implementation, "post-session" means a recent review window, not a
true Anki session boundary. Bonsai should label this clearly as a debrief for
recent/today's reviews until session boundaries are modeled.

- Study material means "content areas worth reviewing if the cards look okay,"
  not a scheduler override.
- Fix cards means repeated-miss cards with construction clues, not an edit
  workflow.
- Session habits means observed facts only, not advice or judgment.

## Implementation Sequence

1. Define a pure debrief model from existing missed-card summaries.
   - Produce `study_next`, `cards_to_fix`, and `session_habits`.
   - Start with today's/recent review window instead of true Anki session
     boundaries.
   - Cover semantics with unit tests before adding UI.

2. Add a manual Session Debrief dialog.
   - Open it from the Bonsai front-page panel and/or Bonsai dialog.
   - Show top 3 study targets, card-fix notice, and basic session metrics.
   - Include a path back to full analytics.

3. Investigate Anki hooks for automatic post-review display.
   - Do not auto-popup until the manual version is useful and the hook is
     reliable.
   - Avoid annoying the user after every short review burst.
   - Treat auto hooks as a separate feature after manual validation.

## Testing Requirements

- Unit-test the debrief model outside Anki.
- Include empty/small-window tests so Bonsai does not overclaim from thin data.
- Keep ranking deterministic for top study targets.
- Keep Anki UI code thin and manually verify it in the actual Anki app before
  committing UI slices.
- Use adversarial review for product semantics before adding auto hooks.
