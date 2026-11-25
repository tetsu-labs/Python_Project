"""Import CRITICAL network log events as incident tickets, idempotently."""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

from exercises.incident_cli import connect, create
from exercises.incident_report import analyze
from exercises.incident_triage import classify


def incident_id(event: dict) -> str:
    canonical = json.dumps(
        {key: event[key] for key in ("timestamp", "host", "severity", "message")},
        ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    )
    return "LOG-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:20].upper()


def import_critical(path: Path, db: Path, *, operator: str = "log-import") -> dict:
    """Validate entire source before importing; duplicates are skipped."""
    summary = analyze(path)
    imported = []
    skipped = []
    for event in summary["critical_events"]:
        key = incident_id(event)
        category = classify(event)["category"]
        try:
            create(db, key, operator, timestamp=event["timestamp"])
        except sqlite3.IntegrityError:
            # An existing ID is not overwritten. Check that it actually exists.
            with connect(db) as conn:
                if conn.execute("SELECT 1 FROM incidents WHERE id = ?", (key,)).fetchone() is None:
                    raise
            skipped.append(key)
        else:
            imported.append({"incident_id": key, "host": event["host"], "category": category})
    return {"critical_count": len(summary["critical_events"]),
            "imported": imported, "skipped_duplicates": skipped}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import CRITICAL JSONL events into SQLite")
    parser.add_argument("input", type=Path)
    parser.add_argument("--db", type=Path, default=Path("incidents.sqlite"))
    parser.add_argument("--operator", default="log-import")
    args = parser.parse_args(argv)
    result = import_critical(args.input, args.db, operator=args.operator)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
