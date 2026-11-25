import pytest

from exercises.incident_cli import create, update
from exercises.incident_metrics import main, summarize


def create_at(db, incident_id, minute):
    create(db, incident_id, "alice", f"2026-11-24T00:{minute:02d}:00Z")


def advance_at(db, incident_id, state, minute, approved=False):
    update(db, incident_id, state, "alice", "ticket evidence",
           timestamp=f"2026-11-24T00:{minute:02d}:00Z", approved=approved)


def test_empty_database(tmp_path):
    result = summarize(tmp_path / "incidents.db")
    assert result["total"] == 0
    assert result["mttr_minutes"] is None


def test_recovery_time_and_unresolved(tmp_path):
    db = tmp_path / "incidents.db"
    create_at(db, "INC-1", 0)
    advance_at(db, "INC-1", "TRIAGED", 1)
    advance_at(db, "INC-1", "RECOVERY_PENDING", 2, True)
    advance_at(db, "INC-1", "RECOVERED", 10)
    create_at(db, "INC-2", 3)
    result = summarize(db)
    assert result["total"] == 2
    assert result["recovered_count"] == 1
    assert result["mttr_minutes"] == 10.0
    assert result["unresolved_ids"] == ["INC-2"]


def test_rollback_not_counted_as_recovery(tmp_path):
    db = tmp_path / "incidents.db"
    create_at(db, "INC-1", 0)
    advance_at(db, "INC-1", "TRIAGED", 1)
    advance_at(db, "INC-1", "RECOVERY_PENDING", 2, True)
    advance_at(db, "INC-1", "ROLLBACK_PENDING", 3, True)
    advance_at(db, "INC-1", "ROLLED_BACK", 4)
    result = summarize(db)
    assert result["recovered_count"] == 0
    assert result["rolled_back_count"] == 1
    assert result["mttr_minutes"] is None


def test_mean_recovery_time(tmp_path):
    db = tmp_path / "incidents.db"
    for incident_id, recovery in [("A", 10), ("B", 20)]:
        create_at(db, incident_id, 0)
        advance_at(db, incident_id, "TRIAGED", 1)
        advance_at(db, incident_id, "RECOVERY_PENDING", 2, True)
        advance_at(db, incident_id, "RECOVERED", recovery)
    assert summarize(db)["mttr_minutes"] == 15.0


def test_cli_output(tmp_path, capsys):
    db = tmp_path / "incidents.db"
    assert main(["--db", str(db)]) == 0
    assert '"total": 0' in capsys.readouterr().out
