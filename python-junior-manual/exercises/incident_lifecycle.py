"""Human-reviewed incident lifecycle; no network commands are executed."""
import hashlib
import json
from datetime import datetime, timezone

STATES = ("DETECTED", "TRIAGED", "RECOVERY_PENDING", "RECOVERED", "ROLLBACK_PENDING", "ROLLED_BACK", "CLOSED")
TRANSITIONS = {
    "DETECTED": {"TRIAGED"},
    "TRIAGED": {"RECOVERY_PENDING"},
    "RECOVERY_PENDING": {"RECOVERED", "ROLLBACK_PENDING"},
    "RECOVERED": {"CLOSED", "ROLLBACK_PENDING"},
    "ROLLBACK_PENDING": {"ROLLED_BACK"},
    "ROLLED_BACK": {"CLOSED"},
    "CLOSED": set(),
}


def start(incident_id: str, *, timestamp: str, operator: str) -> dict:
    if not all(isinstance(x, str) and x.strip() for x in (incident_id, timestamp, operator)):
        raise ValueError("id, timestamp and operator are required")
    _utc(timestamp)
    return {"incident_id": incident_id, "state": "DETECTED", "history": [
        {"state": "DETECTED", "timestamp": _utc(timestamp), "operator": operator, "evidence": "Detection recorded"}
    ]}


def _utc(value: str) -> str:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise ValueError("invalid ISO timestamp") from exc
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("timezone required")
    return dt.astimezone(timezone.utc).isoformat()


def advance(record: dict, next_state: str, *, timestamp: str, operator: str, evidence: str, approved: bool = False) -> dict:
    """Return a new record; do not mutate input or perform recovery operations."""
    if next_state not in TRANSITIONS.get(record.get("state"), set()):
        raise ValueError("invalid state transition")
    if not isinstance(operator, str) or not operator.strip() or not isinstance(evidence, str) or not evidence.strip():
        raise ValueError("operator and evidence are required")
    if next_state in {"RECOVERY_PENDING", "ROLLBACK_PENDING", "CLOSED"} and approved is not True:
        raise PermissionError("explicit approval required")
    normalized = _utc(timestamp)
    if normalized < record["history"][-1]["timestamp"]:
        raise ValueError("timestamps must be monotonic")
    entry = {"state": next_state, "timestamp": normalized, "operator": operator, "evidence": evidence}
    updated = {"incident_id": record["incident_id"], "state": next_state, "history": [*record["history"], entry]}
    return updated


def fingerprint(record: dict) -> str:
    """Stable SHA-256 for comparing an evidence trail across systems."""
    payload = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
