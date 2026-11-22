"""Educational CRUD API. Authentication is not included: do not deploy publicly unprotected."""
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from . import repository
from .db import initialize


class TaskIn(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str = Field(min_length=1, max_length=120)

    @field_validator('title')
    @classmethod
    def normalize_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError('タイトルは空白だけにできません')
        return value


class DoneIn(BaseModel):
    model_config = ConfigDict(extra='forbid')
    done: bool


class TaskOut(BaseModel):
    id: int
    title: str
    done: bool
    created_at: str


def create_app(db_path: Path | None = None) -> FastAPI:
    path = db_path if db_path is not None else Path(os.getenv('TASK_DB_PATH', 'data/tasks.sqlite3'))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        initialize(path)
        yield

    app = FastAPI(title='Junior Task API', version='1.0', lifespan=lifespan)
    app.state.db_path = path

    @app.get('/health')
    def health() -> dict[str, str]:
        return {'status': 'ok'}

    @app.get('/tasks', response_model=list[TaskOut])
    def tasks(request: Request):
        return repository.list_tasks(request.app.state.db_path)

    @app.post('/tasks', response_model=TaskOut, status_code=status.HTTP_201_CREATED)
    def create(payload: TaskIn, request: Request):
        return repository.add_task(request.app.state.db_path, payload.title)

    @app.get('/tasks/{task_id}', response_model=TaskOut)
    def detail(task_id: int, request: Request):
        result = repository.get_task(request.app.state.db_path, task_id)
        if result is None:
            raise HTTPException(status_code=404, detail='task not found')
        return result

    @app.patch('/tasks/{task_id}', response_model=TaskOut)
    def update(task_id: int, payload: DoneIn, request: Request):
        result = repository.set_done(request.app.state.db_path, task_id, payload.done)
        if result is None:
            raise HTTPException(status_code=404, detail='task not found')
        return result

    @app.delete('/tasks/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
    def remove(task_id: int, request: Request):
        if not repository.delete_task(request.app.state.db_path, task_id):
            raise HTTPException(status_code=404, detail='task not found')

    return app


app = create_app()
