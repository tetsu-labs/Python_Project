from pathlib import Path

from app.db import initialize
from app.repository import add_task, list_tasks, set_done


def test_persistence(tmp_path: Path):
    db = tmp_path / 'nested' / 'db.sqlite'
    initialize(db)
    task = add_task(db, 'sample')
    assert len(list_tasks(db)) == 1
    assert set_done(db, task['id'], True)['done'] == 1
