from __future__ import annotations

try:
    from .anki_entry import register_menu

    register_menu()
except Exception as error:
    print(f"Bonsai did not start: {error}")
