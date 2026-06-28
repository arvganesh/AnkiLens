from __future__ import annotations

from html import escape


BUTTON_MESSAGE = "bonsai:open"
DEBRIEF_MESSAGE = "bonsai:debrief"
DECK_SCOPE_MESSAGE_PREFIX = "bonsai:deck:"


def deck_button_html(
    *,
    missed_cards: int | None = None,
    lookback_days: int | None = None,
    deck_options: tuple[str, ...] = (),
    selected_deck: str | None = None,
) -> str:
    summary = _summary_text(missed_cards, lookback_days, selected_deck=selected_deck)
    deck_select = _deck_select_html(deck_options, selected_deck)
    return f"""
<div
  style="
    margin: 18px auto 0;
    max-width: 360px;
    border: 1px solid #e4dfd4;
    border-radius: 14px;
    background: #fbfaf6;
    color: #26231e;
    padding: 12px 14px;
    text-align: left;
  "
>
  <div style="font-weight: 700; margin-bottom: 3px;">Bonsai</div>
  <div style="color: #676056; font-size: 12px; line-height: 1.35; margin-bottom: 10px;">
    {summary}
  </div>
  {deck_select}
  <div style="color: #7a7267; font-size: 11px; line-height: 1.35; margin-top: 9px;">
    Use the Bonsai tab above to analyze missed cards. Read-only: Bonsai does not change scheduling.
  </div>
</div>
"""


def _deck_select_html(deck_options: tuple[str, ...], selected_deck: str | None) -> str:
    if not deck_options:
        return ""
    options = ['<option value="">All decks</option>']
    for deck in deck_options:
        selected = " selected" if deck == selected_deck else ""
        options.append(
            f'<option value="{escape(deck, quote=True)}"{selected} title="{escape(deck, quote=True)}">'
            f"{escape(_deck_display_label(deck))}</option>"
        )
    return f"""
  <label style="display: block; color: #676056; font-size: 11px; font-weight: 600; margin-bottom: 5px;">
    Deck
  </label>
  <select
    onchange="pycmd('{DECK_SCOPE_MESSAGE_PREFIX}' + encodeURIComponent(this.value))"
    style="
      width: 100%;
      border: 1px solid #d8d0c2;
      border-radius: 8px;
      background: #fffaf0;
      color: #2f382f;
      font-size: 12px;
      margin-bottom: 10px;
      padding: 6px 8px;
    "
  >
    {"".join(options)}
  </select>
"""


def _summary_text(missed_cards: int | None, lookback_days: int | None, *, selected_deck: str | None = None) -> str:
    scope = f" in {_deck_display_label(selected_deck)}" if selected_deck else ""
    if missed_cards is None or lookback_days is None:
        return "Analyze missed cards for possible edits or study follow-up."
    if missed_cards == 0:
        return f"No repeated misses found{scope} in the last {lookback_days} days."
    card_label = "card" if missed_cards == 1 else "cards"
    return f"{missed_cards} {card_label} needed another pass{scope} in the last {lookback_days} days."


def _deck_display_label(deck_name: str) -> str:
    parts = [part.strip() for part in deck_name.split("::") if part.strip()]
    if len(parts) > 2:
        return " / ".join(parts[-2:])
    return deck_name
