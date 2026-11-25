import json

import pytest

from exercises.incident_cli import connect, load
from exercises.incident_import import import_critical


def write(tmp_path, *events):
    path = tmp_path / "events.jsonl"
    path.write_text("".join(json.dumps(e) + "\n" for e in events), encoding="utf-8")
    return path


def event(severity="CRITICAL", host="sw01"):
    return {"timestamp": "2026-11-24T12:00:00+09:00",
            "host": host, "severity": severity, "message": "OSPF neighbor down"}


def test_import_and_audit(tmp_path):
    db = tmp_path / "incidents.db"
    result = import_critical(write(tmp_path, event(), event("INFO")), db)
    assert result["critical_count"] == 1
    assert len(result["imported"]) == 1
    key = result["imported"][0]["incident_id"]
    assert load(db, key)["state"] == "DETECTED"
    with connect(db) as conn:
        assert conn.execute("SELECT count(*) FROM incident_audit").fetchone()[0] == 1


def test_idempotent(tmp_path):
    db = tmp_path / "incidents.db"
    path = write(tmp_path, event())
    first = import_critical(path, db)
    second = import_critical(path, db)
    assert len(first["imported"]) == 1
    assert len(second["imported"]) == 0
    assert second["skipped_duplicates"] == [first["imported"][0]["incident_id"]]


def test_different_hosts_get_distinct_tickets(tmp_path):
    db = tmp_path / "incidents.db"
    result = import_critical(write(tmp_path, event(host="sw01"), event(host="sw02")), db)
    assert len(result["imported"]) == 2


def test_invalid_source_creates_no_tickets(tmp_path):
    db = tmp_path / "incidents.db"
    bad = event()
    bad["timestamp"] = "invalid"
    with pytest.raises(ValueError):
        import_critical(write(tmp_path, event(), bad), db)
    assert not db.exists()


def test_no_critical_events(tmp_path):
    result = import_critical(write(tmp_path, event("INFO")), tmp_path / "db.sqlite")
    assert result == {"critical_count": 0, "imported": [], "skipped_duplicates": []}
