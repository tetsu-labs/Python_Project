import json
import pytest
from exercises.incident_triage import build_report, classify, save_report


def event(**kwargs):
    data = {"timestamp": "2026-11-24T12:00:00+09:00", "host": "sw01", "severity": "CRITICAL", "message": "OSPF neighbor down"}
    data.update(kwargs)
    return data


@pytest.mark.parametrize("message,expected", [
    ("OSPF neighbor down", "OSPF_NEIGHBOR_DOWN"),
    ("BGP peer down", "BGP_PEER_DOWN"),
    ("Interface Gi0/1 down", "INTERFACE_DOWN"),
    ("CPU high", "HIGH_CPU"),
    ("unrecognized alarm", "UNCLASSIFIED"),
])
def test_classification(message, expected):
    assert classify(event(message=message))["category"] == expected


def test_report_deterministic_and_utc():
    first = build_report([event(), event(host="router01", message="BGP peer down")])
    second = build_report([event(host="router01", message="BGP peer down"), event()])
    assert first == second
    assert first["event_count"] == 2
    assert first["events"][0]["timestamp"] == "2026-11-24T03:00:00+00:00"
    assert all(e["status"] == "UNVERIFIED" for e in first["events"])


def test_write_json(tmp_path):
    output = tmp_path / "reports" / "incident.json"
    report = build_report([event()])
    save_report(report, output)
    assert json.loads(output.read_text(encoding="utf-8")) == report


@pytest.mark.parametrize("invalid", [
    {"timestamp": "bad"}, {"timestamp": "2026-11-24T12:00:00"},
    {"severity": "URGENT"}, {"host": ""}, {"message": 4},
])
def test_invalid_events(invalid):
    with pytest.raises(ValueError):
        build_report([event(**invalid)])


def test_invalid_source():
    with pytest.raises(ValueError):
        build_report([], source=" ")


def test_no_event_mutation():
    original = event()
    build_report([original])
    assert original["timestamp"].endswith("+09:00")


def test_invalid_classify_message():
    with pytest.raises(ValueError):
        classify({"message": None})
