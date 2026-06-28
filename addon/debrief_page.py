from __future__ import annotations

import json
from html import escape

try:
    from .debrief import Debrief, LlmCheck, LlmDebriefSummary, StudyTarget
    from .debrief_dialog_copy import (
        debrief_intro_text,
        debrief_title,
        early_learning_evidence,
        early_learning_check_text,
        early_learning_next_step,
        early_learning_title,
        evidence_confidence_text,
        mixed_repair_signal_text,
        no_pattern_evidence,
        no_pattern_confidence_text,
        no_pattern_check_text,
        no_pattern_next_step,
        no_pattern_title,
        repair_evidence,
        repair_next_step,
        repair_title,
        same_note_cluster_check_text,
        same_note_cluster_evidence,
        same_note_cluster_next_step,
        same_note_cluster_title,
        short_label,
        scoped_early_learning_evidence,
        scoped_early_learning_title,
        target_detail_text,
        target_display_label,
        target_signal_text,
        study_next_step,
    )
    from .session_context import session_context_text
except ImportError:
    from debrief import Debrief, LlmCheck, LlmDebriefSummary, StudyTarget
    from debrief_dialog_copy import (
        debrief_intro_text,
        debrief_title,
        early_learning_evidence,
        early_learning_check_text,
        early_learning_next_step,
        early_learning_title,
        evidence_confidence_text,
        mixed_repair_signal_text,
        no_pattern_evidence,
        no_pattern_confidence_text,
        no_pattern_check_text,
        no_pattern_next_step,
        no_pattern_title,
        repair_evidence,
        repair_next_step,
        repair_title,
        same_note_cluster_check_text,
        same_note_cluster_evidence,
        same_note_cluster_next_step,
        same_note_cluster_title,
        short_label,
        scoped_early_learning_evidence,
        scoped_early_learning_title,
        target_detail_text,
        target_display_label,
        target_signal_text,
        study_next_step,
    )
    from session_context import session_context_text


def debrief_page_html(debrief: Debrief, *, lookback_days: int, deck_label: str | None = None) -> str:
    llm_summary = llm_summary_html(debrief.llm_summary) if debrief.llm_summary else _llm_loading_html()
    sections = [
        _top_check_html(debrief),
        f'<div id="bonsai-llm-summary">{llm_summary}</div>',
        _supporting_sections_html(debrief),
    ]
    context = session_context_text(debrief.session_habits)
    if context:
        sections.append(_panel_html("Session note", _paragraph(context), quiet=True))
    return f"""
<style>
  body {{
    background: #f5f2ea;
    color: #1f2a20;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    margin: 0;
  }}
  .bonsai-page {{
    box-sizing: border-box;
    margin: 0 auto;
    max-width: 900px;
    padding: 34px 26px 56px;
  }}
  .bonsai-page h1 {{
    font-size: 28px;
    line-height: 1.1;
    margin: 0 0 8px;
  }}
  .bonsai-intro {{
    color: #4d554d;
    font-size: 14px;
    margin-bottom: 18px;
  }}
  .bonsai-stack {{
    display: grid;
    gap: 14px;
  }}
  .bonsai-card {{
    background: #fbfdf7;
    border: 1px solid #d8e8cc;
    border-radius: 13px;
    box-sizing: border-box;
    padding: 18px 20px;
  }}
  .bonsai-card.quiet {{
    background: #f7f4ec;
    border-color: #ebe4d8;
    padding: 13px 15px;
  }}
  .bonsai-eyebrow {{
    color: #64705f;
    font-size: 11px;
    font-weight: 700;
    margin-bottom: 5px;
  }}
  .bonsai-card h2 {{
    font-size: 19px;
    line-height: 1.2;
    margin: 0 0 9px;
  }}
  .bonsai-card.quiet h2 {{
    font-size: 15px;
    margin-bottom: 6px;
  }}
  .bonsai-pill {{
    background: #f1f5e8;
    border: 1px solid #d8e8cc;
    border-radius: 8px;
    color: #344232;
    display: inline-block;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 13px;
    padding: 6px 9px;
  }}
  .bonsai-main {{
    color: #263726;
    font-size: 14px;
    font-weight: 650;
    line-height: 1.35;
    margin: 0 0 13px;
  }}
  .bonsai-detail {{
    margin-top: 9px;
  }}
  .bonsai-detail strong {{
    color: #667064;
    display: block;
    font-size: 12px;
    margin-bottom: 4px;
  }}
  .bonsai-detail span, .bonsai-card p {{
    color: #2f382f;
    font-size: 13px;
    line-height: 1.38;
  }}
  .bonsai-card.quiet p, .bonsai-card.quiet .bonsai-detail span {{
    color: #4d554d;
    font-size: 12px;
  }}
</style>
<script>
  window.bonsaiSetLlmSummary = function(html) {{
    const target = document.getElementById("bonsai-llm-summary");
    if (target) {{
      target.innerHTML = html;
    }}
  }};
</script>
<main class="bonsai-page">
  <h1>{escape(debrief_title())}</h1>
  <div class="bonsai-intro">{escape(debrief_intro_text(lookback_days, deck_label=deck_label))}</div>
  <section class="bonsai-stack">
    {"".join(sections)}
  </section>
</main>
"""


def llm_summary_html(summary: LlmDebriefSummary) -> str:
    rows = []
    if summary.check_first:
        rows.append(_detail_html("Suggested check", _llm_check_text(summary.check_first)))
    rows.extend(_detail_html("Also consider", _llm_check_text(check)) for check in summary.other_checks[:2])
    return _panel_html("Bonsai summary", _paragraph(summary.summary) + "".join(rows), quiet=True)


def llm_summary_update_js(summary: LlmDebriefSummary) -> str:
    return f"window.bonsaiSetLlmSummary({json.dumps(llm_summary_html(summary))});"


def _top_check_html(debrief: Debrief) -> str:
    kind = debrief.next_check_kind
    if kind == "repair":
        card = debrief.cards_to_fix.cards[0]
        return _recommendation_html(
            repair_title(short_label(card.card_label)),
            confidence=evidence_confidence_text(card.misses, card.total_reviews),
            evidence=repair_evidence(card),
            next_step=repair_next_step(),
            check="Inspect first; edit only if the prompt is unclear after opening it.",
        )
    if kind == "early_learning":
        target = debrief.study_next[0] if debrief.study_next else None
        return _recommendation_html(
            scoped_early_learning_title(_target_label(target)) if target else early_learning_title(),
            confidence=evidence_confidence_text(_early_learning_count(debrief), 0, early_learning=True),
            evidence=(
                scoped_early_learning_evidence(_early_learning_count(debrief), _target_label(target))
                if target
                else early_learning_evidence(_early_learning_count(debrief))
            ),
            next_step=early_learning_next_step(),
            check=early_learning_check_text(),
        )
    if kind == "study":
        target = debrief.study_next[0]
        return _recommendation_html(
            f"Check missed examples from {_target_label(target)}",
            confidence=target_signal_text(
                target.count,
                target.reviewed_count,
                active_cards=target.kind == "tag",
                mixed_signals=bool(debrief.cards_to_fix.cards),
            ),
            evidence=target_detail_text(
                target.related_cards,
                early_count=target.early_count,
                mature_count=target.mature_count,
                lapsed_count=target.lapsed_count,
                total_examples=target.count,
            ),
            next_step=study_next_step(
                target.kind,
                mostly_early=target.mostly_early,
                early_count=target.early_count,
                mature_count=target.mature_count,
                lapsed_count=target.lapsed_count,
            ),
            check=mixed_repair_signal_text() if debrief.cards_to_fix.cards else "",
        )
    if kind == "same_note" and debrief.same_note_cluster:
        card = debrief.same_note_cluster
        return _recommendation_html(
            same_note_cluster_title(short_label(card.card_label)),
            confidence="Same note repeated",
            evidence=same_note_cluster_evidence(card),
            next_step=same_note_cluster_next_step(),
            check=same_note_cluster_check_text(),
        )
    has_repeated_misses = bool(debrief.missed_cards)
    return _recommendation_html(
        no_pattern_title(has_repeated_misses=has_repeated_misses),
        confidence=no_pattern_confidence_text(has_repeated_misses=has_repeated_misses),
        evidence=no_pattern_evidence(has_repeated_misses=has_repeated_misses),
        next_step=no_pattern_next_step(has_repeated_misses=has_repeated_misses),
        check=no_pattern_check_text(has_repeated_misses=has_repeated_misses),
        eyebrow="No action",
    )


def _supporting_sections_html(debrief: Debrief) -> str:
    panels = []
    if debrief.cards_to_fix.cards:
        card = debrief.cards_to_fix.cards[0]
        panels.append(
            _panel_html(
                "Also check card format",
                _paragraph(f"{debrief.cards_to_fix.count} card{_plural(debrief.cards_to_fix.count)} may need a card-format check.")
                + _detail_html(
                    "Start here",
                    f"{card.card_label}: {_repair_clues(card)}; needed another pass on {card.misses}/{card.total_reviews} reviews",
                ),
                quiet=True,
            )
        )
    if debrief.study_next and debrief.next_check_kind != "study":
        target = debrief.study_next[0]
        panels.append(_panel_html("Also check cards", _detail_html("Also check", _target_summary(target)), quiet=True))
    return "".join(panels)


def _recommendation_html(
    title: str,
    *,
    confidence: str,
    evidence: str,
    next_step: str,
    check: str,
    eyebrow: str = "Check first",
) -> str:
    check_html = _detail_html("Before studying more", check) if check else ""
    return f"""
<article class="bonsai-card">
  <div class="bonsai-eyebrow">{escape(eyebrow)}</div>
  <h2>{escape(title)}</h2>
  <div class="bonsai-pill">{escape(confidence)}</div>
  <p class="bonsai-main">{escape(next_step)}</p>
  {_detail_html("What Bonsai noticed", evidence)}
  {check_html}
</article>
"""


def _panel_html(title: str, body: str, *, quiet: bool = False) -> str:
    quiet_class = " quiet" if quiet else ""
    return f'<article class="bonsai-card{quiet_class}"><h2>{escape(title)}</h2>{body}</article>'


def _paragraph(text: str) -> str:
    return f"<p>{escape(text)}</p>"


def _detail_html(label: str, value: str) -> str:
    return f'<div class="bonsai-detail"><strong>{escape(label)}</strong><span>{escape(value)}</span></div>'


def _llm_check_text(check: LlmCheck) -> str:
    examples = f" Examples: {', '.join(check.examples)}." if check.examples else ""
    return f"{check.title}: {check.why}{examples}"


def _target_label(target: StudyTarget | None) -> str:
    if target is None:
        return ""
    return target_display_label(target.label, target.kind)


def _target_summary(target: StudyTarget) -> str:
    return target_detail_text(
        target.related_cards,
        early_count=target.early_count,
        mature_count=target.mature_count,
        lapsed_count=target.lapsed_count,
        total_examples=target.count,
    )


def _repair_clues(summary) -> str:
    return ", ".join(summary.content_labels) if summary.content_labels else "repeated misses"


def _early_learning_count(debrief: Debrief) -> int:
    return getattr(debrief.early_learning, "count", 0)


def _llm_loading_html() -> str:
    return _panel_html("Bonsai summary", _paragraph("Looking for patterns in the missed cards..."), quiet=True)


def _plural(count: int) -> str:
    return "" if count == 1 else "s"
