from __future__ import annotations

try:
    from .anki_entry import register_toolbar

    register_toolbar()
except Exception as error:
    print(f"Missed Card Insights did not start: {error}")
