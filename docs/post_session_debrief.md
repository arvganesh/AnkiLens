# Post-Session Debrief Plan

Bonsai should become most useful immediately after study, when the user is
already thinking about what went wrong. The debrief should stay read-only,
calm, and lightweight: it should explain patterns without changing scheduling,
notes, cards, decks, or review history.

## Product Shape

Bonsai should lead with one recommended next check. Supporting cards and
secondary evidence can appear below it, but the first screen should not feel like
a dashboard. Every visible fact should help answer "what should I do next?"

Current recommendation hierarchy:

1. Inspect a card
   - Use when mature repeated misses have card-surface clues such as long,
     dense, list-like, many numbers, media reference, or multiple weaker clues.
   - Action: open the card, read the prompt, and edit only if it asks too much
     or is unclear.

2. Treat as early learning
   - Use when misses are mostly fresh/new cards.
   - Action: keep reviewing normally; study extra only if the examples felt
     unfamiliar or clustered around the same concept.

3. Sample material
   - Purpose: identify content that may need more review after card quality has
     been checked.
   - Inputs: repeated terms, deck concentration, tag concentration, and related
     missed cards.
   - Guardrail: broad study targets require evidence across at least two
     distinct notes/cards, so one cloze-heavy note does not masquerade as a weak
     topic.
   - Action: sample related cards first. If prompts are clear and the examples
     still feel unfamiliar, revisit nearby material.

4. Inspect one note
   - Use when repeated misses are concentrated in sibling cards from one note.
   - Action: open one sibling card and inspect the note. Treat this as one note
     to inspect, not proof the whole topic is weak.

5. Stay quiet
   - Use when there are repeated misses but they do not yet point clearly to a
     card edit, one-note inspection, early-learning case, or broad study target.
   - Action: do not edit or cram from this alone; keep reviewing unless one card
     felt wrong.

Session habits are supporting context only.
   - Purpose: describe how the session went without judging the user.
   - Inputs: review count, Again count/rate, total time, average seconds/card,
     hardest deck/tag, and time of day.
   - Output: show only when the context changes interpretation, such as many
     cards feeling new or unusually fast reviewing. Trend claims such as
     "evening sessions are harder" require enough history and should come later.

## Workflow

The debrief should make one relationship explicit:

Repeated misses can mean the card needs editing, the content needs more study,
or both. Bonsai should help the user check card quality before concluding that
they simply need to study harder.

For tag-driven decks such as AnKing, repeated misses can also mean the user
unsuspended material that matches class tags but has not actually learned the
underlying lecture/topic yet. Bonsai should frame the debrief as a decision:

- If mature construction clues are present, check the specific card first.
- If misses cluster around one note, inspect that note before deciding to study
  more.
- If construction clues are absent and misses span multiple notes in a
  tag/deck/topic, treat the cluster as material to sample, not a card-edit
  diagnosis.
- If the cards are new or recently unsuspended, avoid over-interpreting early
  misses as either bad cards or weak knowledge.

## Initial Semantics

For the first implementation, "post-session" means a recent review window, not a
true Anki session boundary. Bonsai should label this clearly as a debrief for
recent/today's reviews until session boundaries are modeled.

- Study material means "content areas worth sampling if the cards look okay,"
  not a scheduler override.
- Fix cards means repeated-miss cards with surface clues, not an automatic edit
  workflow.
- Same-note evidence means one note/card family to inspect, not proof the whole
  tag is weak.
- Session habits means observed facts only, not judgment.

## Implementation Sequence

1. Define a pure debrief model from existing missed-card summaries.
   - Produce `study_next`, `cards_to_fix`, `early_learning`,
     `same_note_cluster`, and `session_habits`.
   - Start with today's/recent review window instead of true Anki session
     boundaries.
   - Cover semantics with unit tests before adding UI.

2. Add a manual Session Debrief dialog.
   - Open it from the Bonsai front-page panel and/or Bonsai dialog.
   - Lead with one recommended next check.
   - Keep support evidence below the recommendation and avoid dashboard-like
     metric blocks.
   - Include a path back to full analytics.

3. Investigate Anki hooks for automatic post-review display.
   - Do not auto-popup until the manual version is useful and the hook is
     reliable.
   - Avoid annoying the user after every short review burst.
   - Treat auto hooks as a separate feature after manual validation.

## Testing Requirements

- Unit-test the debrief model outside Anki.
- Include empty/small-window tests so Bonsai does not overclaim from thin data.
- Keep ranking deterministic for supported study targets.
- Include cloze-heavy AnKing scenarios where sibling cards from one note should
  not become broad study evidence.
- Keep Anki UI code thin and manually verify it in the actual Anki app before
  committing UI slices.
- Use adversarial review for product semantics before adding auto hooks.
