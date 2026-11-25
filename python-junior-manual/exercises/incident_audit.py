"""Append-only, hash-linked incident audit trail for training.

A hash chain detects accidental edits when a trusted digest is retained separately.
It is NOT tamper-proof against a database administrator who can rewrite the chain.
"""
import hashlib
import json
import sqlite3

GENESIS = "0" * 64


def canonical(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(previous: str, payload: str) -> str:
    return hashlib.sha256((previous + "\n" + payload).encode("utf-8")).hexdigest()


def setup(conn: sqlite3.Connection) -> None:
    conn.execute("""CREATE TABLE IF NOT EXISTS incident_audit (
        seq INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_id TEXT NOT NULL,
        previous_hash TEXT NOT NULL,
        payload TEXT NOT NULL,
        entry_hash TEXT NOT NULL
    )""")


def append(conn: sqlite3.Connection, record: dict) -> str:
    """Append a snapshot inside the caller's transaction."""
    setup(conn)
    incident_id = record["incident_id"]
    row = conn.execute(
        "SELECT entry_hash FROM incident_audit WHERE incident_id = ? ORDER BY seq DESC LIMIT 1",
        (incident_id,),
    ).fetchone()
    previous = row[0] if row else GENESIS
    payload = canonical(record)
    current = digest(previous, payload)
    conn.execute(
        "INSERT INTO incident_audit(incident_id, previous_hash, payload, entry_hash) VALUES (?, ?, ?, ?)",
        (incident_id, previous, payload, current),
    )
    return current


def verify(conn: sqlite3.Connection, incident_id: str) -> dict:
    """Check each link, state history, and current snapshot."""
    setup(conn)
    rows = conn.execute(
        "SELECT previous_hash, payload, entry_hash FROM incident_audit WHERE incident_id = ? ORDER BY seq",
        (incident_id,),
    ).fetchall()
    if not rows:
        raise LookupError("audit history not found")
    previous = GENESIS
    for position, (stored_previous, payload, stored_hash) in enumerate(rows, 1):
        if stored_previous != previous or digest(previous, payload) != stored_hash:
            return {"valid": False, "broken_at": position}
        try:
            record = json.loads(payload)
        except json.JSONDecodeError:
            return {"valid": False, "broken_at": position}
        if record.get("incident_id") != incident_id or len(record.get("history", [])) != position:
            return {"valid": False, "broken_at": position}
        previous = stored_hash
    current = conn.execute("SELECT payload FROM incidents WHERE id = ?", (incident_id,)).fetchone()
    if current is None or canonical(json.loads(current[0])) != canonical(record):
        return {"valid": False, "broken_at": "current"}
    return {"valid": True, "entries": len(rows), "head": previous}
