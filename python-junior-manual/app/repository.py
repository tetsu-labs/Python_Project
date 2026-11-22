"""Persistence layer: SQL is kept out of HTTP endpoints."""
from pathlib import Path
from .db import connection


def list_tasks(path: Path) -> list[dict]:
    with connection(path) as conn:
        rows = conn.execute('SELECT id,title,done,created_at FROM tasks ORDER BY id').fetchall()
        return [dict(row) for row in rows]


def get_task(path: Path, task_id: int) -> dict | None:
    with connection(path) as conn:
        row = conn.execute('SELECT id,title,done,created_at FROM tasks WHERE id=?', (task_id,)).fetchone()
        return dict(row) if row else None


def add_task(path: Path, title: str) -> dict:
    with connection(path) as conn:
        cursor = conn.execute('INSERT INTO tasks(title) VALUES(?)', (title,))
        row = conn.execute('SELECT id,title,done,created_at FROM tasks WHERE id=?', (cursor.lastrowid,)).fetchone()
        return dict(row)


def set_done(path: Path, task_id: int, done: bool) -> dict | None:
    with connection(path) as conn:
        cursor = conn.execute('UPDATE tasks SET done=? WHERE id=?', (int(done), task_id))
        if cursor.rowcount == 0:
            return None
        row = conn.execute('SELECT id,title,done,created_at FROM tasks WHERE id=?', (task_id,)).fetchone()
        return dict(row)


def delete_task(path: Path, task_id: int) -> bool:
    with connection(path) as conn:
        cursor = conn.execute('DELETE FROM tasks WHERE id=?', (task_id,))
        return cursor.rowcount > 0
