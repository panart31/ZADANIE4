# -*- coding: utf-8 -*-
"""Журнал запусков в SQLite."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .exceptions import StorageError
from .models import RunRecord


class RunStorage:
    """Храню историю расчётов, чтобы она не пропадала после закрытия окна."""

    def __init__(self, path="genlab.db"):
        self.path = str(path)
        # папку создаю заранее, иначе sqlite не сможет создать файл базы
        folder = Path(self.path).parent
        if str(folder) not in ("", "."):
            folder.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connect(self):
        """Открываю соединение на одну операцию и всегда закрываю его."""
        try:
            connection = sqlite3.connect(self.path)
        except sqlite3.Error as error:
            raise StorageError(f"не удалось открыть базу: {error}") from error
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except sqlite3.Error as error:
            connection.rollback()
            raise StorageError(f"ошибка базы данных: {error}") from error
        finally:
            connection.close()

    def _init_db(self):
        """Создаю таблицу журнала, если её ещё нет."""
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    preview TEXT NOT NULL DEFAULT '',
                    duration_ms REAL NOT NULL,
                    created TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def _to_record(row):
        """Превращаю строку SQLite в объект RunRecord."""
        return RunRecord(
            task=row["task"],
            summary=row["summary"],
            preview=row["preview"],
            duration_ms=row["duration_ms"],
            created=row["created"],
            run_id=row["id"],
        )

    def add_run(self, record):
        """Сохраняю одну запись и возвращаю её номер."""
        with self._connect() as connection:
            cursor = connection.execute(
                """INSERT INTO runs (task, summary, preview, duration_ms, created)
                   VALUES (?, ?, ?, ?, ?)""",
                (record.task, record.summary, record.preview,
                 record.duration_ms, record.created),
            )
            return cursor.lastrowid

    def list_runs(self, limit=50):
        """Отдаю последние записи: свежие идут первыми."""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [self._to_record(row) for row in rows]

    def count_runs(self):
        """Считаю, сколько всего записей лежит в журнале."""
        with self._connect() as connection:
            row = connection.execute("SELECT COUNT(*) AS total FROM runs").fetchone()
        return row["total"]

    def clear(self):
        """Удаляю все записи журнала и возвращаю их количество."""
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM runs")
            return cursor.rowcount

    def close(self):
        """Соединения уже закрыты, отдельно закрывать нечего."""
        pass
