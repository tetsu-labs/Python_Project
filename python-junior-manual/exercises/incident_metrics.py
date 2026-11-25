"""Incident metrics: recovery time and unresolved backlog from SQLite snapshots.

MTTR = mean(DETECTED -> first RECOVERED) in minutes.
ROLLED_BACK is not counted as recovered. No SLA claims are made.
"""
import argparse
import json
import statistics
from collections import Counter
from datetime import datetime
from pathlib import Path

from exercises.incident_cli import connect


def _minutes(start: str, end: str) -> float:
    seconds = (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds()
    if seconds < 0:
        raise ValueError("negative incident duration")
    return seconds / 60


def summarize(db: Path) -> dict:
    """Read incident snapshots; count states and compute recovery durations."""
    with connect(db) as conn:
        rows = conn.execute("SELECT payload FROM incidents ORDER BY id").fetchall()
    states = Counter()
    recovery_minutes = []
    unresolved = []
    rolled_back = 0
    for (payload,) in rows:
        record = json.loads(payload)
        state = record["state"]
        states[state] += 1
        history = record["history"]
        detected = next((entry["timestamp"] for entry in history if entry["state"] == "DETECTED"), None)
        recovered = next((entry["timestamp"] for entry in history if entry["state"] == "RECOVERED"), None)
        if detected is None:
            raise ValueError("missing DETECTED event")
        if recovered is not None:
            recovery_minutes.append(_minutes(detected, recovered))
        if state == "ROLLED_BACK" or any(entry["state"] == "ROLLED_BACK" for entry in history):
            rolled_back += 1
        if state not in {"CLOSED", "RECOVERED", "ROLLED_BACK"}:
            unresolved.append(record["incident_id"])
    return {
        "total": len(rows),
        "by_state": dict(sorted(states.items())),
        "recovered_count": len(recovery_minutes),
        "mttr_minutes": round(statistics.mean(recovery_minutes), 2) if recovery_minutes else None,
        "rolled_back_count": rolled_back,
        "unresolved_ids": sorted(unresolved),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Incident recovery metrics from SQLite")
    parser.add_argument("--db", type=Path, default=Path("incidents.sqlite"))
    args = parser.parse_args(argv)
    print(json.dumps(summarize(args.db), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
