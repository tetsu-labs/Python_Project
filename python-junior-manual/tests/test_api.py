from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client(tmp_path: Path):
    with TestClient(create_app(tmp_path / 'tasks.sqlite3')) as api:
        yield api


def test_health(client):
    assert client.get('/health').json() == {'status': 'ok'}


def test_crud(client):
    response = client.post('/tasks', json={'title': '  CCNA lab  '})
    assert response.status_code == 201
    task = response.json()
    assert task['title'] == 'CCNA lab'
    task_id = task['id']
    assert client.get(f'/tasks/{task_id}').status_code == 200
    assert len(client.get('/tasks').json()) == 1
    response = client.patch(f'/tasks/{task_id}', json={'done': True})
    assert response.status_code == 200
    assert response.json()['done'] is True
    assert client.delete(f'/tasks/{task_id}').status_code == 204
    assert client.get(f'/tasks/{task_id}').status_code == 404


@pytest.mark.parametrize('bad', ['', ' ', 'x' * 121])
def test_invalid_title(client, bad):
    assert client.post('/tasks', json={'title': bad}).status_code == 422


def test_unknown_fields(client):
    assert client.post('/tasks', json={'title': 'ok', 'admin': True}).status_code == 422


def test_missing_id(client):
    assert client.patch('/tasks/999', json={'done': True}).status_code == 404
    assert client.delete('/tasks/999').status_code == 404


def test_sql_injection_is_data(client):
    title = "'); DROP TABLE tasks; --"
    assert client.post('/tasks', json={'title': title}).status_code == 201
    assert client.get('/tasks').json()[0]['title'] == title
