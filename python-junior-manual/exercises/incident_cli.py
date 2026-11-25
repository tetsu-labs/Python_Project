"""Incident CLI with SQLite persistence, review gates, and Markdown export.

Usage:
 python -m exercises.incident_cli --db incidents.sqlite init INC-1 --operator alice
 python -m exercises.incident_cli --db incidents.sqlite advance INC-1 TRIAGED --operator alice --evidence "show output"
 python -m exercises.incident_cli --db incidents.sqlite show INC-1
 python -m exercises.incident_cli --db incidents.sqlite report INC-1 --output report.md

No network device commands are executed.
"""
import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from exercises.incident_lifecycle import advance, fingerprint, start
from exercises.incident_audit import append, verify


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect(db: Path) -> sqlite3.Connection:
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db, timeout=5)
    conn.execute("CREATE TABLE IF NOT EXISTS incidents (id TEXT PRIMARY KEY, revision INTEGER NOT NULL, payload TEXT NOT NULL)")
    return conn


def create(db: Path, incident_id: str, operator: str, timestamp: str | None = None) -> dict:
    record = start(incident_id, timestamp=timestamp or now(), operator=operator)
    with connect(db) as conn:
        conn.execute("INSERT INTO incidents (id, revision, payload) VALUES (?, 1, ?)",
                     (incident_id, json.dumps(record, ensure_ascii=False)))
        append(conn, record)
    return record


def load(db: Path, incident_id: str) -> dict:
    with connect(db) as conn:
        row = conn.execute("SELECT payload FROM incidents WHERE id = ?", (incident_id,)).fetchone()
    if row is None:
        raise LookupError(f"incident not found: {incident_id}")
    return json.loads(row[0])


def update(db: Path, incident_id: str, state: str, operator: str, evidence: str,
           *, approved: bool = False, timestamp: str | None = None) -> dict:
    """Serialize concurrent updates with BEGIN IMMEDIATE."""
    conn = connect(db)
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT revision, payload FROM incidents WHERE id = ?", (incident_id,)).fetchone()
        if row is None:
            raise LookupError(f"incident not found: {incident_id}")
        updated = advance(json.loads(row[1]), state, timestamp=timestamp or now(),
                          operator=operator, evidence=evidence, approved=approved)
        conn.execute("UPDATE incidents SET revision = ?, payload = ? WHERE id = ?",
                     (row[0] + 1, json.dumps(updated, ensure_ascii=False), incident_id))
        append(conn, updated)
        conn.commit()
        return updated
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()


def markdown(record: dict) -> str:
    """Generate an escaped Markdown table and reproducible evidence digest."""
    def cell(value: str) -> str:
        return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").replace("\r", " ")

    lines = [
        "# Incident " + cell(record["incident_id"]),
        "",
        "**Status:** " + cell(record["state"]),
        "",
        "**SHA-256:** `" + fingerprint(record) + "`",
        "",
        "| UTC timestamp | State | Operator | Evidence |",
        "|---|---|---|---|",
    ]
    for item in record["history"]:
        lines.append("| " + " | ".join(cell(item[key]) for key in ("timestamp", "state", "operator", "evidence")) + " |")
    lines.extend(["", "Review evidence manually. This tool did not execute recovery commands.", ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Auditable incident management training CLI")
    parser.add_argument("--db", type=Path, default=Path("incidents.sqlite"))
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("incident_id")
    init.add_argument("--operator", required=True)
    change = commands.add_parser("advance")
    change.add_argument("incident_id")
    change.add_argument("state")
    change.add_argument("--operator", required=True)
    change.add_argument("--evidence", required=True)
    change.add_argument("--approved", action="store_true")
    show = commands.add_parser("show")
    show.add_argument("incident_id")
    audit = commands.add_parser("verify")
    audit.add_argument("incident_id")
    report = commands.add_parser("report")
    report.add_argument("incident_id")
    report.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "verify":
        with connect(args.db) as conn:
            result = verify(conn, args.incident_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["valid"] else 1
    if args.command == "init":
        result = create(args.db, args.incident_id, args.operator)
    elif args.command == "advance":
        result = update(args.db, args.incident_id, args.state, args.operator, args.evidence,
                        approved=args.approved)
    else:
        result = load(args.db, args.incident_id)
    if args.command == "report":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown(result), encoding="utf-8")
        print(args.output)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
