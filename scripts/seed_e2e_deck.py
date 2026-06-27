from __future__ import annotations

import argparse
import shutil
import sqlite3
import time
from pathlib import Path


PROFILE_COLLECTION = (
    Path.home()
    / "Library"
    / "Application Support"
    / "Anki2"
    / "User 1"
    / "collection.anki2"
)

DECK_NAME = "Bonsai E2E Large Review Window"
NOTE_TYPE_ID = 1674685976679
TAGS = " AnKing::Cardiology::Valves BonsaiE2E "


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed a real Anki deck for Bonsai end-to-end debrief testing.")
    parser.add_argument("--collection", type=Path, default=PROFILE_COLLECTION)
    parser.add_argument("--no-backup", action="store_true", help="Skip the timestamped collection backup.")
    args = parser.parse_args()

    collection = args.collection.expanduser()
    if not collection.exists():
        raise SystemExit(f"collection not found: {collection}")

    if not args.no_backup:
        backup = collection.with_name(f"{collection.name}.bonsai-e2e-backup-{time.strftime('%Y%m%d-%H%M%S')}")
        shutil.copy2(collection, backup)
        print(f"backup: {backup}")

    with sqlite3.connect(collection) as db:
        db.create_collation("unicase", _unicase)
        db.execute("pragma foreign_keys = off")
        seed(db)
        db.commit()


def seed(db: sqlite3.Connection) -> None:
    deck_id = _deck_id(db)
    _delete_existing(db, deck_id)
    _insert_deck(db, deck_id)

    max_existing_id = max(
        _scalar(db, "select coalesce(max(id), 0) from notes"),
        _scalar(db, "select coalesce(max(id), 0) from cards"),
        _scalar(db, "select coalesce(max(id), 0) from revlog"),
        int(time.time() * 1000),
    )
    note_base = max_existing_id + 10_000
    card_base = note_base + 1_000_000
    revlog_base = note_base + 2_000_000
    now_secs = int(time.time())

    notes = []
    cards = []
    revlogs = []
    review_index = 0

    for index in range(1, 221):
        note_id = note_base + index
        card_id = card_base + index
        label = f"Stable valve review card {index}"
        notes.append(_note_row(note_id, label, "No action needed for this stable review.", now_secs))
        cards.append(_card_row(card_id, note_id, deck_id, reps=20, lapses=0, due=index))
        revlogs.append(_revlog_row(revlog_base + review_index, card_id, ease=3, duration_ms=2400))
        review_index += 1

    for index in range(221, 301):
        note_id = note_base + index
        card_id = card_base + index
        label = f"Valve physiology missed example {index} with long AnKing-style clinical wording"
        notes.append(_note_row(note_id, label, "High-yield valve physiology explanation.", now_secs))
        cards.append(_card_row(card_id, note_id, deck_id, reps=20, lapses=2, due=index))
        revlogs.append(_revlog_row(revlog_base + review_index, card_id, ease=1, duration_ms=4200))
        review_index += 1
        revlogs.append(_revlog_row(revlog_base + review_index, card_id, ease=1, duration_ms=3900))
        review_index += 1

    db.executemany(
        """
        insert into notes (id, guid, mid, mod, usn, tags, flds, sfld, csum, flags, data)
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        notes,
    )
    db.executemany(
        """
        insert into cards (id, nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps, lapses, left, odue, odid, flags, data)
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        cards,
    )
    db.executemany(
        """
        insert into revlog (id, cid, usn, ease, ivl, lastIvl, factor, time, type)
        values (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        revlogs,
    )
    _touch_collection(db, now_secs)
    print(f"seeded deck: {DECK_NAME}")
    print(f"notes: {len(notes)} cards: {len(cards)} revlog rows: {len(revlogs)}")


def _delete_existing(db: sqlite3.Connection, deck_id: int) -> None:
    card_ids = [row[0] for row in db.execute("select id from cards where did = ?", (deck_id,))]
    note_ids = [row[0] for row in db.execute("select id from notes where tags like '%BonsaiE2E%'")]
    if card_ids:
        db.executemany("delete from revlog where cid = ?", [(card_id,) for card_id in card_ids])
    if note_ids:
        db.executemany("delete from cards where nid = ?", [(note_id,) for note_id in note_ids])
        db.executemany("delete from notes where id = ?", [(note_id,) for note_id in note_ids])
    db.execute("delete from decks where id = ?", (deck_id,))


def _insert_deck(db: sqlite3.Connection, deck_id: int) -> None:
    common, kind = db.execute("select common, kind from decks where id = 1").fetchone()
    now_secs = int(time.time())
    db.execute(
        "insert into decks (id, name, mtime_secs, usn, common, kind) values (?, ?, ?, ?, ?, ?)",
        (deck_id, DECK_NAME, now_secs, -1, common, kind),
    )


def _note_row(note_id: int, front: str, back: str, now_secs: int) -> tuple:
    fields = f"{front}\x1f{back}"
    return (
        note_id,
        f"bonsai-e2e-{note_id}",
        NOTE_TYPE_ID,
        now_secs,
        -1,
        TAGS,
        fields,
        front,
        abs(hash(front)) % 4_294_967_296,
        0,
        "",
    )


def _card_row(card_id: int, note_id: int, deck_id: int, *, reps: int, lapses: int, due: int) -> tuple:
    now_secs = int(time.time())
    return (
        card_id,
        note_id,
        deck_id,
        0,
        now_secs,
        -1,
        2,
        2,
        due,
        21,
        2500,
        reps,
        lapses,
        0,
        0,
        0,
        0,
        "",
    )


def _revlog_row(revlog_id: int, card_id: int, *, ease: int, duration_ms: int) -> tuple:
    ivl = -600 if ease == 1 else 21
    last_ivl = 21
    return (revlog_id, card_id, -1, ease, ivl, last_ivl, 2500, duration_ms, 1)


def _touch_collection(db: sqlite3.Connection, now_secs: int) -> None:
    db.execute("update col set mod = ?, scm = ?", (now_secs, int(time.time() * 1000)))


def _deck_id(db: sqlite3.Connection) -> int:
    existing = db.execute("select id from decks where name = ?", (DECK_NAME,)).fetchone()
    if existing:
        return int(existing[0])
    return max(int(time.time() * 1000), _scalar(db, "select coalesce(max(id), 0) from decks") + 1)


def _scalar(db: sqlite3.Connection, query: str) -> int:
    return int(db.execute(query).fetchone()[0])


def _unicase(left: str, right: str) -> int:
    left_key = left.casefold()
    right_key = right.casefold()
    return (left_key > right_key) - (left_key < right_key)


if __name__ == "__main__":
    main()
