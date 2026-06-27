from __future__ import annotations


BUTTON_MESSAGE = "bonsai:open"


def deck_button_html() -> str:
    return """
<div style="margin-top: 12px; text-align: center;">
  <button
    onclick="pycmd('bonsai:open')"
    style="
      border: 1px solid #d9d9d9;
      border-radius: 999px;
      background: #f7f7f7;
      color: #222;
      cursor: pointer;
      font-size: 13px;
      padding: 7px 14px;
    "
  >
    Open Bonsai
  </button>
</div>
"""
