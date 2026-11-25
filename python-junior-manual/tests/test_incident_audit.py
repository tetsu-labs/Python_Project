import json
import sqlite3

from exercises.incident_audit import append, setup, verify


def record(n=1):
    return {"incident_id": "INC-1", "state": "DETECTED", "history": [
        {"state": "DETECTED", "timestamp": "2026-11-24T00:00:00Z", "operator": "alice", "evidence": "log"}
    ] * n}


def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE incidents(id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
    return conn


def test_chain_and_current_snapshot():
    with db() as conn:
        first = record()
        second = record(2)
        append(conn, first)
        append(conn, second)
        conn.execute("INSERT INTO incidents VALUES (?, ?)", ("INC-1", json.dumps(second)))
        result = verify(conn, "INC-1")
        assert result["valid"] is True
        assert result["entries"] == 2


def test_detect_changed_audit_payload():
    with db() as conn:
        first = record()
        append(conn, first)
        conn.execute("INSERT INTO incidents VALUES (?, ?)", ("INC-1", json.dumps(first)))
        conn.execute("UPDATE incident_audit SET payload = ? WHERE seq = 1", ('{}',))
        assert verify(conn, "INC-1") == {"valid": False, "broken_at": 1}


def test_detect_changed_current():
    with db() as conn:
        first = record()
        append(conn, first)
        conn.execute("INSERT INTO incidents VALUES (?, ?)", ("INC-1", json.dumps(record(2))))
        assert verify(conn, "INC-1") == {"valid": False, "broken_at": "current"}


def test_missing_audit():
    with db() as conn:
        try:
            verify(conn, "missing")
        except LookupError:
            pass
        else:
            raise AssertionError("expected LookupError")
