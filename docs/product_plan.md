# AnkiLens Product Plan

## Current Focus

Ship a useful read-only Anki add-on that helps learners understand recent
missed cards for one selected deck and time window.

The first version should prove that users repeatedly find value in:

- missed-card themes grounded in real review history
- plain-language recommendations
- direct links back into Anki Browse
- low-friction use inside Anki

## Monetization Direction

AnkiLens can eventually support a paid hosted AI tier, but billing should come
after the core insight loop is clearly useful.

Prefer a simple monthly plan over an explicit credit system at first. Credits
are useful for cost control, but they make the product feel more complicated.

Do not make token price the center of the product. BYO-key alpha users may see
that raw model calls can be inexpensive, especially with non-premium models.
The paid tier needs to justify itself through convenience and workflow:

- hosted setup with no API-key management
- better default model choices and fallbacks
- larger analysis windows
- stronger clustering over many missed cards
- saved insight history
- card-improvement suggestions that save editing time
- support and continued product maintenance

Avoid showing per-call token costs in the Anki UI. Keep cost responsibility
clear in docs for BYO-key users, but do not train users to evaluate AnkiLens as
a thin token markup.

### Free Tier

The free tier should be generous enough to prove the product:

- bring-your-own OpenRouter key support
- a small number of hosted AI analyses per month
- capped review-event window
- capped missed-card evidence sent to the model
- basic content-theme insights
- open missed cards in Anki Browse
- optional bring-your-own OpenRouter key for advanced users

### Paid Tier

The paid tier should buy better learning insight, not just more AI calls:

- hosted AI with no API-key setup
- larger review windows for heavy users
- more missed-card evidence analyzed
- better default model or fallback model routing
- deeper card-level clustering
- leech/card-edit recommendations
- saved insight history
- comparison over time, such as what changed since last week
- future cloze-aware normalization

## Implementation Sequence

1. Ship local/BYO-key AnkiLens first.
2. Watch whether users repeatedly run insights and open missed cards.
3. Add an optional hosted API proxy so model choice, keys, and quotas are server-side.
4. Add accounts and simple monthly usage limits.
5. Add Stripe billing.
6. Add higher-value paid features after there is real usage signal.

Quota and billing checks should live on a server. Local add-on enforcement is
fine for UI hints, but it is not reliable for real paid limits.
