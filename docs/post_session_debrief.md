# Post-Session Debrief Plan

AnkiLens should become most useful immediately after study, when the user is
already thinking about what went wrong. The debrief should stay read-only,
calm, and lightweight: it should explain patterns without changing scheduling,
notes, cards, decks, or review history.

## Product Shape

AnkiLens should lead with the most useful check and may show a small ranked set of
secondary checks. Supporting facts can appear below each action, but the first
screen should not feel like a dashboard. Every visible fact should help answer
"what should I inspect or ignore next?"

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

3. Inspect missed examples or related material
   - Purpose: identify content that may need more review after card quality has
     been checked.
   - Inputs: repeated terms, deck concentration, tag concentration, and related
     missed cards.
   - Guardrail: broad study targets require support across at least two
     distinct notes/cards, so one cloze-heavy note does not masquerade as a weak
     topic.
   - Action: inspect exact missed examples when available. If prompts are clear
     and the examples still feel unfamiliar, revisit nearby material.

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
or both. AnkiLens should help the user check card quality before concluding that
they simply need to study harder.

For tag-driven decks such as AnKing, repeated misses can also mean the user
unsuspended material that matches class tags but has not actually learned the
underlying lecture/topic yet. AnkiLens should frame the debrief as a decision:

- If mature construction clues are present, check the specific card first.
- If misses cluster around one note, inspect that note before deciding to study
  more.
- If construction clues are absent and misses span multiple notes in a
  tag/deck/topic, treat the cluster as material to check, not a card-edit
  diagnosis.
- If the cards are new or recently unsuspended, avoid over-interpreting early
  misses as either bad cards or weak knowledge.

## Initial Semantics

For the first implementation, "post-session" means a recent review window, not a
true Anki session boundary. AnkiLens should label this clearly as a debrief for
recent/today's reviews until session boundaries are modeled.

- Study material means "content areas worth checking if the cards look okay,"
  not a scheduler override.
- Fix cards means repeated-miss cards with surface clues, not an automatic edit
  workflow.
- Same-note support means one note/card family to inspect, not proof the whole
  tag is weak.
- Session habits means observed facts only, not judgment.

## Implementation Sequence

1. Define a pure debrief model from existing missed-card summaries.
   - Produce `study_next`, `cards_to_fix`, `early_learning`,
     `same_note_cluster`, and `session_habits`.
   - Start with today's/recent review window instead of true Anki session
     boundaries.
   - Cover semantics with unit tests before adding UI.

2. Keep the manual debrief as a page-based Insights flow.
   - Open it from the AnkiLens top toolbar or Tools menu.
   - Lead with concise LLM-generated sections grounded by the selected deck and
     time window.
   - Keep recommendations concrete enough to apply from Browse.
   - Avoid dashboard-like metric blocks unless they directly support the
     recommendation.

3. Investigate Anki hooks for automatic post-review display.
   - Do not auto-popup until the manual version is useful and the hook is
     reliable.
   - Avoid annoying the user after every short review burst.
   - Treat auto hooks as a separate feature after manual validation.

## Testing Requirements

- Unit-test the debrief model outside Anki.
- Include empty/small-window tests so AnkiLens does not overclaim from thin data.
- Keep ranking deterministic for supported study targets.
- Include cloze-heavy AnKing scenarios where sibling cards from one note should
  not become broad study support.
- Keep Anki UI code thin and manually verify it in the actual Anki app before
  committing UI slices.
- Use adversarial review for product semantics before adding auto hooks.

## Future Direction: Med-School Scale Windows

For heavy med-school users, a 30-day window can contain thousands of review
events and hundreds of unique missed cards. The LLM should not rely only on a
small sample of card text in that scenario.

A future version should build a deterministic review-window profile before the
LLM call. That profile should summarize the full selected deck/window, then
send representative missed-card examples only after the aggregate facts.

Useful full-window stats may include:

- total review events
- unique cards reviewed
- cards with at least one miss
- total misses
- repeated-miss cards, such as cards with 2+ or 3+ misses
- top decks, tags, topics, or repeated terms by miss count
- early/new cards versus mature or lapsed missed cards
- card-surface signals such as long, list-like, or many-number cards

The goal is to help the LLM rank what matters at scale. Raw examples help it
read the card content; aggregate stats help it understand whether a pattern is
large enough to act on. The UI should continue to show only concise,
student-facing insights and concrete read-only actions such as opening the
relevant missed cards in Browse.

Some review-event stats should also become visible product evidence, not only
hidden LLM context. For example, med-school users may want a compact
read-only view of total review events, cards reviewed, cards with misses,
Again rate, repeated-miss cards, and top missed topics. Keep this separate
from the prose insight card so the first screen stays calm, but make the
evidence available for users who want to inspect the numbers behind the
recommendations.

### Cloze Normalization

For cloze-heavy decks, especially AnKing-style medical decks, the LLM should
not treat every missed cloze sibling as an independent raw card. Multiple
missed siblings from one note may indicate one crowded note or one cloze family
to inspect, not a broad weakness across the whole topic.

A future prompt builder should group missed cloze siblings by note when
`note_id` is available. Instead of sending repeated raw card text for each
sibling, send one normalized note-level entry with sibling stats:

- note/card family id
- deck
- total sibling cards when available
- missed sibling count
- total misses and reviews across the sibling cards
- hardest cloze siblings, such as `c2 missed 3/4`
- shared note text or a compact normalized card text
- content labels such as long, list-like, or many-number card
- exact card ids to open in Browse

Single-card misses can still be sent as normal card entries. The goal is to
help the LLM distinguish "this one cloze note may ask too much" from "this
whole topic needs attention," while preserving concrete Browse actions for the
missed sibling cards.
