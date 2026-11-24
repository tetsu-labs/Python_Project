"""End-to-end persistence and workflow tests using isolated SQLite files."""
import pytest
from exercises.incident_cli import create, load, main, markdown, update


def test_create_and_load(tmp_path):
    db = tmp_path / "nested" / "incident.db"
    created = create(db, "INC-1", "alice", "2026-11-24T00:00:00Z")
    assert load(db, "INC-1") == created


def test_duplicate_rejected(tmp_path):
    db = tmp_path / "db.sqlite"
    create(db, "INC-1", "alice")
    with pytest.raises(Exception):
        create(db, "INC-1", "bob")


def test_full_recovery_flow(tmp_path):
    db = tmp_path / "db.sqlite"
    create(db, "INC-1", "alice", "2026-11-24T00:00:00Z")
    for state, minute, approved in [
        ("TRIAGED", 1, False), ("RECOVERY_PENDING", 2, True),
        ("RECOVERED", 3, False), ("CLOSED", 4, True),
    ]:
        update(db, "INC-1", state, "alice", "ticket-123",
               approved=approved, timestamp=f"2026-11-24T00:{minute:02d}:00Z")
    assert load(db, "INC-1")["state"] == "CLOSED"
    assert len(load(db, "INC-1")["history"]) == 5


def test_rejected_update_does_not_change_database(tmp_path):
    db = tmp_path / "db.sqlite"
    create(db, "INC-1", "alice", "2026-11-24T00:00:00Z")
    original = load(db, "INC-1")
    with pytest.raises(ValueError):
        update(db, "INC-1", "CLOSED", "alice", "no review", approved=True,
               timestamp="2026-11-24T00:01:00Z")
    assert load(db, "INC-1") == original


def test_approval_gate(tmp_path):
    db = tmp_path / "db.sqlite"
    create(db, "INC-1", "alice", "2026-11-24T00:00:00Z")
    update(db, "INC-1", "TRIAGED", "alice", "show output", timestamp="2026-11-24T00:01:00Z")
    with pytest.raises(PermissionError):
        update(db, "INC-1", "RECOVERY_PENDING", "alice", "ticket", timestamp="2026-11-24T00:02:00Z")
    assert load(db, "INC-1")["state"] == "TRIAGED"


def test_report_escapes_markdown(tmp_path):
    db = tmp_path / "db.sqlite"
    create(db, "INC-1", "alice", "2026-11-24T00:00:00Z")
    update(db, "INC-1", "TRIAGED", "alice", "port|down", timestamp="2026-11-24T00:01:00Z")
    report = markdown(load(db, "INC-1"))
    assert "port\\|down" in report
    assert "SHA-256" in report


def test_missing_incident(tmp_path):
    with pytest.raises(LookupError):
        load(tmp_path / "db.sqlite", "MISSING")


def test_cli_end_to_end(tmp_path, capsys):
    db = tmp_path / "db.sqlite"
    output = tmp_path / "report.md"
    assert main(["--db", str(db), "init", "INC-7", "--operator", "alice"]) == 0
    assert main(["--db", str(db), "advance", "INC-7", "TRIAGED",
                 "--operator", "alice", "--evidence", "show command output"]) == 0
    assert main(["--db", str(db), "report", "INC-7", "--output", str(output)]) == 0
    assert "TRIAGED" in output.read_text(encoding="utf-8")
