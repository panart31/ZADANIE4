"""Проверки журнала в SQLite."""

import pytest

from genlab.exceptions import StorageError
from genlab.models import RunRecord
from genlab.storage import RunStorage


def make_record(task="Круги", summary="5 значений", preview="314,16"):
    return RunRecord(task=task, summary=summary, preview=preview,
                     duration_ms=0.5)


def test_add_and_list(tmp_path):
    storage = RunStorage(tmp_path / "runs.db")
    first = storage.add_run(make_record())
    second = storage.add_run(make_record("Почта", "7 адресов", "abc@mail.ru"))
    records = storage.list_runs()
    assert [record.run_id for record in records] == [second, first]
    assert records[0].task == "Почта"
    assert records[1].preview == "314,16"
    storage.close()


def test_limit(tmp_path):
    storage = RunStorage(tmp_path / "runs.db")
    for index in range(5):
        storage.add_run(make_record(summary=f"Запись {index}"))
    records = storage.list_runs(2)
    assert len(records) == 2
    assert records[0].summary == "Запись 4"
    storage.close()


def test_count_and_clear(tmp_path):
    storage = RunStorage(tmp_path / "runs.db")
    for _ in range(3):
        storage.add_run(make_record())
    assert storage.count_runs() == 3
    assert storage.clear() == 3
    assert storage.count_runs() == 0
    storage.close()


def test_persistence(tmp_path):
    path = tmp_path / "runs.db"
    first = RunStorage(path)
    first.add_run(make_record())
    first.close()

    second = RunStorage(path)
    assert second.count_runs() == 1
    assert second.list_runs()[0].task == "Круги"
    second.close()


def test_bad_path(tmp_path):
    with pytest.raises(StorageError):
        RunStorage(tmp_path)


def test_created_is_filled(tmp_path):
    storage = RunStorage(tmp_path / "runs.db")
    record = make_record()
    assert len(record.created) == 19
    storage.add_run(record)
    saved = storage.list_runs()[0]
    assert saved.created == record.created
    storage.close()
