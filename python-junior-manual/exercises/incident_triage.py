"""Deterministic incident triage and auditable runbook generation."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

RULES = (
    ("OSPF_NEIGHBOR_DOWN", re.compile(r"\bospf\b.*\b(neighbou?r|adjacency)\b.*\b(down|lost|failed)\b", re.I), "show ip ospf neighbor", "Check interface, MTU, area and OSPF timers; do not change configuration without approval."),
    ("INTERFACE_DOWN", re.compile(r"\b(interface|link|port)\b.*\b(down|lost)\b", re.I), "show interfaces status", "Check physical cabling and interface errors; escalate before changes."),
    ("BGP_PEER_DOWN", re.compile(r"\bbgp\b.*\b(peer|neighbou?r|session)\b.*\b(down|lost|idle)\b", re.I), "show ip bgp summary", "Verify reachability and peer state; escalate route changes."),
    ("HIGH_CPU", re.compile(r"\b(cpu|processor)\b.*\b(high|critical|overload|[89]\d%|100%)\b", re.I), "show processes cpu sorted", "Identify the consuming process and assess impact before restarting anything."),
)


def classify(event: dict) -> dict:
    """Return non-destructive suggested diagnostic steps, never execute them."""
    message = event.get("message")
    if not isinstance(message, str):
        raise ValueError("event.message must be a string")
    for code, pattern, command, guidance in RULES:
        if pattern.search(message):
            return {"category": code, "diagnostic_command": command, "guidance": guidance}
    return {"category": "UNCLASSIFIED", "diagnostic_command": None, "guidance": "Collect logs and escalate for manual triage."}


def build_report(events: list[dict], *, source: str = "manual") -> dict:
    """Create a reproducible report with a content hash for audit comparison."""
    if not isinstance(source, str) or not source.strip():
        raise ValueError("source must be nonempty")
    records = []
    for index, event in enumerate(events, 1):
        if not isinstance(event, dict):
            raise ValueError(f"event {index}: expected object")
        required = ("timestamp", "host", "severity", "message")
        if any(not isinstance(event.get(key), str) or not event[key].strip() for key in required):
            raise ValueError(f"event {index}: missing or invalid fields")
        if event["severity"] not in ("INFO", "WARNING", "CRITICAL"):
            raise ValueError(f"event {index}: invalid severity")
        try:
            dt = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"event {index}: invalid timestamp") from exc
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError(f"event {index}: timestamp needs timezone")
        normalized = {"timestamp": dt.astimezone(timezone.utc).isoformat(), "host": event["host"], "severity": event["severity"], "message": event["message"]}
        records.append({**normalized, **classify(normalized), "status": "UNVERIFIED"})
    records.sort(key=lambda item: (item["timestamp"], item["host"], item["message"]))
    canonical = json.dumps(records, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {"schema_version": 1, "source": source, "event_count": len(records), "sha256": hashlib.sha256(canonical).hexdigest(), "events": records, "note": "Suggestions only. No commands were executed; recovery is unverified."}


def save_report(report: dict, output: Path) -> None:
    """Write UTF-8 JSON; caller controls the destination path."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
