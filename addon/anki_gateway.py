from __future__ import annotations

from datetime import datetime

try:
    from .analytics import ReviewLogEntry
except ImportError:
    from analytics import ReviewLogEntry


def load_review_entries(mw) -> list[ReviewLogEntry]:
    rows = mw.col.db.all(
        """
        select
          revlog.cid,
          revlog.ease,
          revlog.id,
          cards.did,
          coalesce(notes.sfld, cast(revlog.cid as text)),
          notes.tags
        from revlog
        join cards on cards.id = revlog.cid
        join notes on notes.id = cards.nid
        order by revlog.id desc
        """
    )

    return [
        ReviewLogEntry(
            card_id=card_id,
            ease=ease,
            reviewed_at=datetime.fromtimestamp(reviewed_at_ms / 1000),
            deck_name=mw.col.decks.name(deck_id) or "Unknown deck",
            card_label=card_label,
            tags=tuple(tag for tag in tags.split() if tag),
        )
        for card_id, ease, reviewed_at_ms, deck_id, card_label, tags in rows
    ]
