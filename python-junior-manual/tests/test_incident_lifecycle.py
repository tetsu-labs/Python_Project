import pytest
from exercises.incident_lifecycle import advance, fingerprint, start


def init():
    return start("INC-001", timestamp="2026-11-24T09:00:00+09:00", operator="analyst")


def step(record, state, minute, **kwargs):
    return advance(record, state, timestamp=f"2026-11-24T00:{minute:02d}:00+00:00",
                   operator="analyst", evidence="Verified log reference", **kwargs)


def test_recovery_flow():
    record = init()
    for state, minute, approval in [
        ("TRIAGED", 1, False), ("RECOVERY_PENDING", 2, True),
        ("RECOVERED", 3, False), ("CLOSED", 4, True),
    ]:
        record = step(record, state, minute, approved=approval)
    assert record["state"] == "CLOSED"
    assert len(record["history"]) == 5


def test_rollback_flow():
    record = step(init(), "TRIAGED", 1)
    record = step(record, "RECOVERY_PENDING", 2, approved=True)
    record = step(record, "ROLLBACK_PENDING", 3, approved=True)
    record = step(record, "ROLLED_BACK", 4)
    assert record["state"] == "ROLLED_BACK"


def test_approval_required():
    record = step(init(), "TRIAGED", 1)
    with pytest.raises(PermissionError):
        step(record, "RECOVERY_PENDING", 2)


def test_invalid_transition():
    with pytest.raises(ValueError):
        step(init(), "CLOSED", 1, approved=True)


def test_no_mutation():
    record = init()
    step(record, "TRIAGED", 1)
    assert record["state"] == "DETECTED"
    assert len(record["history"]) == 1


def test_fingerprint_is_deterministic():
    assert fingerprint(init()) == fingerprint(init())


def test_timestamp_order():
    with pytest.raises(ValueError):
        step(init(), "TRIAGED", 0)


@pytest.mark.parametrize("value", ["2026-11-24", "nonsense", ""])
def test_invalid_initial_timestamp(value):
    with pytest.raises(ValueError):
        start("INC-1", timestamp=value, operator="analyst")


def test_evidence_required():
    with pytest.raises(ValueError):
        advance(init(), "TRIAGED", timestamp="2026-11-24T00:01:00Z",
                operator="analyst", evidence="")


def test_closed_is_terminal():
    record = init()
    for state, minute, approved in [
        ("TRIAGED", 1, False), ("RECOVERY_PENDING", 2, True),
        ("RECOVERED", 3, False), ("CLOSED", 4, True),
    ]:
        record = step(record, state, minute, approved=approved)
    with pytest.raises(ValueError):
        step(record, "TRIAGED", 5)
