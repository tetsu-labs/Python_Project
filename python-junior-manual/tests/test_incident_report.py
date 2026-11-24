import json
import pytest
from exercises.incident_report import analyze


def write(tmp_path, *lines):
    path = tmp_path / 'incidents.jsonl'
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return path


def event(**overrides):
    item = {'timestamp': '2026-11-24T12:00:00+09:00', 'host': 'sw01',
            'severity': 'CRITICAL', 'message': 'OSPF neighbor down'}
    item.update(overrides)
    return json.dumps(item)


def test_summary(tmp_path):
    report = analyze(write(tmp_path, event(), event(severity='INFO', host='router01')))
    assert report['total'] == 2
    assert report['by_severity'] == {'CRITICAL': 1, 'INFO': 1, 'WARNING': 0}
    assert report['by_host'] == {'router01': 1, 'sw01': 1}
    assert report['critical_events'][0]['timestamp'] == '2026-11-24T03:00:00+00:00'


def test_empty_file(tmp_path):
    assert analyze(write(tmp_path))['total'] == 0


@pytest.mark.parametrize('line', ['{bad', '[]', '"text"', '{}'])
def test_invalid_json_or_shape(tmp_path, line):
    with pytest.raises(ValueError, match='line 1'):
        analyze(write(tmp_path, line))


@pytest.mark.parametrize('overrides', [
    {'severity': 'EMERGENCY'}, {'timestamp': 'yesterday'},
    {'timestamp': '2026-11-24T12:00:00'}, {'host': ''}, {'message': 42},
    {'extra': 'unrecognized'},
])
def test_invalid_event(tmp_path, overrides):
    with pytest.raises(ValueError, match='line 1'):
        analyze(write(tmp_path, event(**overrides)))


def test_invalid_second_line_reports_line_number(tmp_path):
    with pytest.raises(ValueError, match='line 2'):
        analyze(write(tmp_path, event(), '{broken'))


def test_critical_sorted_by_utc_timestamp(tmp_path):
    newer = event(timestamp='2026-11-24T14:00:00+09:00')
    older = event(timestamp='2026-11-24T01:00:00+00:00')
    report = analyze(write(tmp_path, newer, older))
    assert report['critical_events'][0]['timestamp'] == '2026-11-24T01:00:00+00:00'
