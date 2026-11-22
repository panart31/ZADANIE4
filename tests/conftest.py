"""Общие фикстуры для тестов."""

import pytest

from genlab.service import GenLabService
from genlab.storage import RunStorage


@pytest.fixture
def service(tmp_path):
    """Создаю сервис с временной базой и закрываю её после теста."""
    database = RunStorage(tmp_path / "test.db")
    result = GenLabService(database)
    yield result
    result.close()
