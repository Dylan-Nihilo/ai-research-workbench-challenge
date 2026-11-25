import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .schemas import Task


class TaskStore:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(path)) as connection, connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, created_at TEXT NOT NULL, payload TEXT NOT NULL)"
            )

    def create(self, question: str) -> Task:
        now = datetime.now(timezone.utc)
        task = Task(id=str(uuid4()), question=question, created_at=now, updated_at=now)
        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute("INSERT INTO tasks VALUES (?, ?, ?)",
                               (task.id, task.created_at.isoformat(), task.model_dump_json()))
        return task

    def get(self, task_id: str) -> Task | None:
        with closing(sqlite3.connect(self.path)) as connection:
            row = connection.execute("SELECT payload FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return Task.model_validate_json(row[0]) if row else None

    def list(self) -> list[Task]:
        with closing(sqlite3.connect(self.path)) as connection:
            rows = connection.execute("SELECT payload FROM tasks ORDER BY created_at DESC, id DESC").fetchall()
        return [Task.model_validate_json(row[0]) for row in rows]

    def save(self, task: Task) -> None:
        task.updated_at = datetime.now(timezone.utc)
        with closing(sqlite3.connect(self.path)) as connection, connection:
            cursor = connection.execute("UPDATE tasks SET payload = ? WHERE id = ?",
                                        (task.model_dump_json(), task.id))
            if cursor.rowcount != 1:
                raise KeyError(task.id)

    def delete(self, task_id: str) -> None:
        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
