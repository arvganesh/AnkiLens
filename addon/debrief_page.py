from __future__ import annotations

import json
from html import escape

try:
    from .anki_browser import browser_search_for_cards
    from .debrief import Debrief, LlmDebriefSummary
except ImportError:
    from anki_browser import browser_search_for_cards
    from debrief import Debrief, LlmDebriefSummary


DECK_SCOPE_MESSAGE_PREFIX = "ankilens:deck:"
LOOKBACK_SCOPE_MESSAGE_PREFIX = "ankilens:lookback:"
BROWSE_SEARCH_MESSAGE_PREFIX = "ankilens:browse:"


def debrief_page_html(
    debrief: Debrief,
    *,
    lookback_days: int,
    lookback_options: tuple[int, ...] = (7, 30, 90),
    deck_options: tuple[str, ...] = (),
    selected_deck: str | None = None,
    deck_label: str | None = None,
    llm_enabled: bool = True,
) -> str:
    grounding = grounding_text(deck_label or selected_deck, lookback_days)
    llm_summary = (
        llm_summary_html(debrief.llm_summary, debrief.evidence, grounding=grounding)
        if debrief.llm_summary
        else _llm_loading_html(debrief.evidence, grounding=grounding) if llm_enabled else _llm_disabled_html(debrief.evidence, grounding=grounding)
    )
    sections = [f'<div id="ankilens-llm-summary">{llm_summary}</div>']
    return f"""
<style>
  body {{
    background: #f5f6f8;
    color: #202124;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    margin: 0;
  }}
  .ankilens-page {{
    box-sizing: border-box;
    margin: 0 auto;
    max-width: 880px;
    padding: 30px 24px 48px;
  }}
  .ankilens-page h1 {{
    font-size: 28px;
    line-height: 1.15;
    margin: 0 0 7px;
  }}
  .ankilens-header {{
    align-items: end;
    display: grid;
    gap: 18px;
    grid-template-columns: minmax(0, 1fr) minmax(300px, 430px);
    margin-bottom: 18px;
  }}
  .ankilens-filters {{
    display: grid;
    gap: 10px;
    grid-template-columns: minmax(150px, 1fr) minmax(120px, 0.6fr);
  }}
  .ankilens-filter label {{
    color: #5f6368;
    display: block;
    font-size: 12px;
    font-weight: 650;
    margin-bottom: 5px;
  }}
  .ankilens-filter select {{
    background: #ffffff;
    border: 1px solid #dadce0;
    border-radius: 6px;
    box-sizing: border-box;
    color: #202124;
    font-size: 13px;
    min-height: 36px;
    padding: 7px 9px;
    width: 100%;
  }}
  @media (max-width: 680px) {{
    .ankilens-header {{
      align-items: stretch;
      grid-template-columns: 1fr;
    }}
    .ankilens-filters {{
      grid-template-columns: 1fr;
    }}
  }}
  .ankilens-stack {{
    display: grid;
    gap: 14px;
  }}
  .ankilens-card {{
    background: #ffffff;
    border: 1px solid #dadce0;
    border-radius: 7px;
    box-sizing: border-box;
    padding: 18px 20px;
  }}
  .ankilens-card.primary {{
    padding: 20px 22px;
  }}
  .ankilens-card h2 {{
    font-size: 19px;
    line-height: 1.2;
    margin: 0 0 9px;
  }}
  .ankilens-card.primary h2 {{
    font-size: 22px;
  }}
  .ankilens-card p {{
    color: #202124;
    font-size: 13px;
    line-height: 1.38;
  }}
  .ankilens-insight-body {{
    max-width: 760px;
  }}
  .ankilens-insight-context {{
    border-bottom: 1px solid #e8eaed;
    color: #3c4043;
    font-size: 13px;
    line-height: 1.35;
    margin: 0 0 18px;
    padding-bottom: 13px;
  }}
  .ankilens-insight-section {{
    margin: 0;
    padding: 0 0 17px;
  }}
  .ankilens-insight-section + .ankilens-insight-section {{
    border-top: 1px solid #e8eaed;
    padding-top: 16px;
  }}
  .ankilens-insight-section:last-of-type {{
    padding-bottom: 0;
  }}
  .ankilens-insight-section h3 {{
    border-radius: 4px;
    display: inline-block;
    font-size: 13px;
    font-weight: 750;
    line-height: 1.25;
    margin: 0 0 9px;
    padding: 2px 6px;
  }}
  .ankilens-insight-section.good h3 {{
    background: #e9f5ee;
    color: #276749;
  }}
  .ankilens-insight-section.improve h3 {{
    background: #fff3bf;
    color: #6b5200;
  }}
  .ankilens-recommendations {{
    color: #202124;
    font-size: 13px;
    line-height: 1.45;
    margin: 0;
    padding-left: 18px;
  }}
  .ankilens-recommendations li {{
    margin: 0 0 10px;
    padding-left: 2px;
  }}
  .ankilens-recommendations li::marker {{
    color: #5f6368;
  }}
  .ankilens-recommendations li:last-child {{
    margin-bottom: 0;
  }}
  .ankilens-action {{
    color: #5f6368;
    display: block;
    font-size: 12px;
    line-height: 1.35;
    margin-top: 3px;
  }}
  .ankilens-insight-actions {{
    border-top: 1px solid #e8eaed;
    margin-top: 17px;
    padding-top: 14px;
  }}
  .ankilens-action-button {{
    background: transparent;
    color: #3c4043;
    cursor: pointer;
    font-size: 12px;
    font-weight: 500;
    line-height: 1.35;
    text-decoration: underline;
    text-underline-offset: 2px;
  }}
  .ankilens-action-button:focus {{
    outline: 1px solid #9aa0a6;
    outline-offset: 2px;
  }}
  .ankilens-action-button:hover {{
    color: #202124;
  }}
  @media (prefers-color-scheme: dark) {{
    body {{
      background: #202124;
      color: #e8eaed;
    }}
    .ankilens-filter label,
    .ankilens-insight-context,
    .ankilens-action {{
      color: #bdc1c6;
    }}
    .ankilens-filter select,
    .ankilens-card {{
      background: #2b2c2f;
      border-color: #3c4043;
      color: #e8eaed;
    }}
    .ankilens-action-button {{
      color: #e8eaed;
    }}
    .ankilens-insight-context,
    .ankilens-insight-section + .ankilens-insight-section,
    .ankilens-insight-actions {{
      border-color: #3c4043;
    }}
    .ankilens-card p,
    .ankilens-recommendations {{
      color: #e8eaed;
    }}
    .ankilens-insight-section.good h3 {{
      background: #1f3a2d;
      color: #b9e3c8;
    }}
    .ankilens-insight-section.improve h3 {{
      background: #3e341c;
      color: #f2d982;
    }}
  }}
</style>
<script>
  window.ankilensSetLlmSummary = function(html) {{
    const target = document.getElementById("ankilens-llm-summary");
    if (target) {{
      target.innerHTML = html;
    }}
  }};
  document.addEventListener("click", function(event) {{
    const button = event.target.closest("[data-ankilens-browse-query]");
    if (!button) {{
      return;
    }}
    event.preventDefault();
    pycmd("{BROWSE_SEARCH_MESSAGE_PREFIX}" + encodeURIComponent(button.dataset.ankilensBrowseQuery));
  }});
</script>
<main class="ankilens-page">
  <header class="ankilens-header">
    <div>
      <h1>{escape(debrief_title())}</h1>
    </div>
    {_filters_html(deck_options, selected_deck, lookback_options, lookback_days)}
  </header>
  <section class="ankilens-stack">
    {"".join(sections)}
  </section>
</main>
"""


def llm_summary_html(summary: LlmDebriefSummary, evidence=None, *, grounding: str = "") -> str:
    return _panel_html(
        "",
        f'<div class="ankilens-insight-body">{_insight_context_html(evidence)}{_insight_rows_html(summary)}{_insight_actions_html(summary)}</div>',
        primary=True,
    )


def llm_summary_update_js(summary: LlmDebriefSummary, evidence=None, *, grounding: str = "") -> str:
    return f"window.ankilensSetLlmSummary({json.dumps(llm_summary_html(summary, evidence, grounding=grounding))});"


def llm_summary_status_update_js(message: str, evidence=None, *, grounding: str = "") -> str:
    return f"window.ankilensSetLlmSummary({json.dumps(_llm_status_html(message, evidence, grounding=grounding))});"


def _filters_html(
    deck_options: tuple[str, ...],
    selected_deck: str | None,
    lookback_options: tuple[int, ...],
    selected_lookback_days: int,
) -> str:
    deck_selector = _deck_selector_html(deck_options, selected_deck)
    lookback_selector = _lookback_selector_html(lookback_options, selected_lookback_days)
    if not deck_selector and not lookback_selector:
        return ""
    return f'<div class="ankilens-filters">{deck_selector}{lookback_selector}</div>'


def _deck_selector_html(deck_options: tuple[str, ...], selected_deck: str | None) -> str:
    if not deck_options:
        return ""
    options = []
    for deck in deck_options:
        selected = " selected" if deck == selected_deck else ""
        options.append(
            f'<option value="{escape(deck, quote=True)}"{selected} title="{escape(deck, quote=True)}">'
            f"{escape(_deck_display_label(deck))}</option>"
        )
    return f"""
<div class="ankilens-filter">
  <label for="ankilens-deck-select">Deck</label>
  <select
    id="ankilens-deck-select"
    onchange="pycmd('{DECK_SCOPE_MESSAGE_PREFIX}' + encodeURIComponent(this.value))"
  >
    {"".join(options)}
  </select>
</div>
"""


def _lookback_selector_html(lookback_options: tuple[int, ...], selected_lookback_days: int) -> str:
    options = []
    for days in lookback_options:
        selected = " selected" if days == selected_lookback_days else ""
        label = f"{days} days"
        options.append(f'<option value="{days}"{selected}>{escape(label)}</option>')
    return f"""
<div class="ankilens-filter">
  <label for="ankilens-lookback-select">Time window</label>
  <select
    id="ankilens-lookback-select"
    onchange="pycmd('{LOOKBACK_SCOPE_MESSAGE_PREFIX}' + encodeURIComponent(this.value))"
  >
    {"".join(options)}
  </select>
</div>
"""


def _panel_html(title: str, body: str, *, primary: bool = False) -> str:
    primary_class = " primary" if primary else ""
    title_html = f"<h2>{escape(title)}</h2>" if title else ""
    return f'<article class="ankilens-card{primary_class}">{title_html}{body}</article>'


def _paragraph(text: str) -> str:
    return f"<p>{escape(text)}</p>"


def _insight_context_html(evidence) -> str:
    if evidence is None:
        return ""
    label = "review" if evidence.reviews == 1 else "reviews"
    return f'<p class="ankilens-insight-context">Based on analysis of the last {evidence.reviews} {label}:</p>'


def _insight_rows_html(summary: LlmDebriefSummary) -> str:
    sections = []
    if summary.positives:
        sections.append(_bullet_section_html("What you're doing well", summary.positives))
    sections.append(_improvement_section_html("Areas for improvement", summary.improvements))
    return "".join(sections)


def _bullet_section_html(title: str, items: tuple[str, ...]) -> str:
    item_html = "".join(f"<li>{escape(item)}</li>" for item in items)
    return f'<section class="ankilens-insight-section good"><h3>{escape(title)}</h3><ul class="ankilens-recommendations">{item_html}</ul></section>'


def _improvement_section_html(title: str, items) -> str:
    item_html = "".join(
        f"<li>{escape(item.insight)} <span class=\"ankilens-action\">Try: {escape(item.action)}</span></li>"
        for item in items
    )
    return f'<section class="ankilens-insight-section improve"><h3>{escape(title)}</h3><ul class="ankilens-recommendations">{item_html}</ul></section>'


def _insight_actions_html(summary: LlmDebriefSummary) -> str:
    card_ids = _unique_card_ids(summary.action_card_ids)
    query = _card_search_query(card_ids)
    if not query:
        return ""
    return (
        '<div class="ankilens-insight-actions">'
        f'<a href="#" class="ankilens-action-button" data-ankilens-browse-query="{escape(query, quote=True)}">'
        f"Open {_count_label(len(card_ids), 'missed card', 'missed cards')} in Browse"
        "</a>"
        "</div>"
    )


def _card_search_query(card_ids: tuple[int, ...]) -> str:
    return browser_search_for_cards(card_ids)


def _unique_card_ids(card_ids: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(dict.fromkeys(card_id for card_id in card_ids if card_id))


def _count_label(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"


def grounding_text(deck_label: str | None, lookback_days: int) -> str:
    deck = deck_label or "selected deck"
    return f"Based on {deck}, last {lookback_days} days. Uses review logs and missed-card text only."


def _llm_loading_html(evidence=None, *, grounding: str = "") -> str:
    return _panel_html(
        "",
        _paragraph("Looking for patterns in the missed cards..."),
        primary=True,
    )


def _llm_disabled_html(evidence=None, *, grounding: str = "") -> str:
    return _llm_status_html("LLM insights are not enabled for this add-on configuration.", evidence, grounding=grounding)


def _llm_status_html(message: str, evidence=None, *, grounding: str = "") -> str:
    return _panel_html(
        "",
        _paragraph(message),
        primary=True,
    )


def _deck_display_label(deck_name: str) -> str:
    parts = [part.strip() for part in deck_name.split("::") if part.strip()]
    if len(parts) > 2:
        return " / ".join(parts[-2:])
    return deck_name


def debrief_title() -> str:
    return "Insights"
