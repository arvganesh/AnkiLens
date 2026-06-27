from __future__ import annotations


BUTTON_MESSAGE = "bonsai:open"
DEBRIEF_MESSAGE = "bonsai:debrief"


def deck_button_html(*, missed_cards: int | None = None, lookback_days: int | None = None) -> str:
    summary = _summary_text(missed_cards, lookback_days)
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
  <button
    onclick="pycmd('bonsai:open')"
    style="
      border: 1px solid #d9d0c1;
      border-radius: 999px;
      background: #fff;
      color: #26231e;
      cursor: pointer;
      font-size: 13px;
      padding: 7px 14px;
    "
  >
    Supporting Cards
  </button>
  <button
    onclick="pycmd('bonsai:debrief')"
    style="
      border: 1px solid #d9d0c1;
      border-radius: 999px;
      background: #fff;
      color: #26231e;
      cursor: pointer;
      font-size: 13px;
      margin-left: 6px;
      padding: 7px 14px;
    "
  >
    Recent Debrief
  </button>
</div>
"""


def _summary_text(missed_cards: int | None, lookback_days: int | None) -> str:
    if missed_cards is None or lookback_days is None:
        return "Review repeated misses and content patterns."
    if missed_cards == 0:
        return f"No repeated misses found in the last {lookback_days} days."
    card_label = "card" if missed_cards == 1 else "cards"
    return f"{missed_cards} {card_label} needing another pass in the last {lookback_days} days."
