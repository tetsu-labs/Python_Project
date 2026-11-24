"""Network operations log analyzer: parse and summarize incident events.

Example:
    python -m exercises.incident_report incidents.jsonl
"""
import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from exercises.incident_triage import build_report, save_report

SEVERITIES = {'INFO', 'WARNING', 'CRITICAL'}


def analyze(path: Path) -> dict:
    """Validate JSON Lines and produce an incident summary."""
    counts = Counter()
    hosts = Counter()
    incidents = []
    with path.open(encoding='utf-8-sig') as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f'line {line_no}: invalid JSON') from exc
            if not isinstance(event, dict):
                raise ValueError(f'line {line_no}: expected object')
            if set(event) != {'timestamp', 'host', 'severity', 'message'}:
                raise ValueError(f'line {line_no}: unexpected or missing fields')
            if not all(isinstance(event[k], str) and event[k].strip() for k in event):
                raise ValueError(f'line {line_no}: fields must be nonempty strings')
            if event['severity'] not in SEVERITIES:
                raise ValueError(f'line {line_no}: invalid severity')
            try:
                dt = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
            except ValueError as exc:
                raise ValueError(f'line {line_no}: invalid timestamp') from exc
            if dt.tzinfo is None or dt.utcoffset() is None:
                raise ValueError(f'line {line_no}: timestamp must have timezone')
            event['timestamp'] = dt.astimezone(timezone.utc).isoformat()
            counts[event['severity']] += 1
            hosts[event['host']] += 1
            if event['severity'] == 'CRITICAL':
                incidents.append(event)
    return {
        'total': sum(counts.values()),
        'by_severity': {level: counts[level] for level in sorted(SEVERITIES)},
        'by_host': dict(sorted(hosts.items())),
        'critical_events': sorted(incidents, key=lambda item: item['timestamp']),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Analyze network incident JSONL')
    parser.add_argument('input', type=Path)
    parser.add_argument('--evidence', type=Path, help='Write deterministic triage and runbook JSON')
    args = parser.parse_args()
    summary = analyze(args.input)
    if args.evidence is not None:
        events = []
        with args.input.open(encoding='utf-8-sig') as handle:
            for line in handle:
                if line.strip():
                    events.append(json.loads(line))
        save_report(build_report(events, source=str(args.input)), args.evidence)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
