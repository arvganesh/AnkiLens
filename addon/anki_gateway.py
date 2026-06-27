from __future__ import annotations

from datetime import datetime

try:
    from .analytics import ReviewLogEntry
    from .content_text import clean_card_text
except ImportError:
    from analytics import ReviewLogEntry
    from content_text import clean_card_text


def load_review_entries(mw) -> list[ReviewLogEntry]:
    rows = mw.col.db.all(
        """
        select
          revlog.cid,
          revlog.ease,
          revlog.id,
          revlog.time,
          revlog.type,
          cards.did,
          cards.nid,
          note_cards.card_count,
          cards.reps,
          cards.lapses,
          cards.type,
          cards.queue,
          coalesce(notes.sfld, cast(revlog.cid as text)),
          notes.tags,
          notes.flds
        from revlog
        join cards on cards.id = revlog.cid
        join notes on notes.id = cards.nid
        join (
          select nid, count(*) as card_count
          from cards
          group by nid
        ) note_cards on note_cards.nid = cards.nid
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
            note_id=note_id,
            note_card_count=note_card_count,
            tags=tuple(tag for tag in tags.split() if tag),
            source_text=clean_card_text(fields),
            duration_ms=duration_ms,
            review_type=review_type,
            card_reps=card_reps,
            card_lapses=card_lapses,
            card_type=card_type,
            card_queue=card_queue,
        )
        for (
            card_id,
            ease,
            reviewed_at_ms,
            duration_ms,
            review_type,
            deck_id,
            note_id,
            note_card_count,
            card_reps,
            card_lapses,
            card_type,
            card_queue,
            card_label,
            tags,
            fields,
        ) in rows
    ]
