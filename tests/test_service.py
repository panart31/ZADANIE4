"""Проверки сервисного слоя."""

import csv

import pytest

from genlab.exceptions import ExportError, ValidationError


def test_circle_report(service):
    result = service.circle_report(10, 100, 1, 5)
    assert result.rows[0] == (1, "10,00", "314,16")
    assert result.rows[1] == (2, "11,00", "380,13")
    assert len(result.rows) == 5
    assert "5 из 91" in result.summary
    assert result.duration_ms >= 0


def test_circle_report_with_comma(service):
    result = service.circle_report("10,5", "11,5", "0,5", 3)
    assert len(result.rows) == 3
    assert result.rows[0][1] == "10,50"


def test_circle_report_saves_journal(service):
    service.circle_report(10, 20, 1, 5)
    records = service.history()
    assert len(records) == 1
    assert records[0].task == "Площади кругов"
    assert "5 из 11" in records[0].summary


@pytest.mark.parametrize("args", [
    ("abc", 100, 1, 5),
    (10, 5, 1, 5),
    (10, 100, 0, 5),
    (10, 100, 1, 0),
])
def test_circle_report_errors(service, args):
    with pytest.raises(ValidationError):
        service.circle_report(*args)


def test_circle_report_limits_limit(service):
    result = service.circle_report(10, 12, 1, 50)
    assert len(result.rows) == 3


def test_email_report(service):
    result = service.email_report(8, 7)
    assert len(result.rows) == 7
    for row in result.rows:
        name, domain = row[1].split("@")
        assert len(name) == 8
        assert domain == "mail.ru"
    assert "7 адресов" in result.summary


def test_email_report_errors(service):
    with pytest.raises(ValidationError):
        service.email_report(3, 7)
    with pytest.raises(ValidationError):
        service.email_report(8, 0)


def test_two_digit_report(service):
    result = service.two_digit_report("5 12 999 -34 100 7 56")
    assert result.rows == [(1, 12), (2, -34), (3, 56)]
    assert "двузначных: 3" in result.summary


def test_two_digit_report_empty_result(service):
    result = service.two_digit_report("5 999 100")
    assert result.rows == []
    assert "двузначных: 0" in result.summary


def test_two_digit_report_bad_token(service):
    with pytest.raises(ValidationError):
        service.two_digit_report("5 abc 7")


def test_benchmark_report(service):
    result = service.benchmark_report(count=2000, length=8, workers=2)
    assert len(result.rows) == 3
    assert result.rows[0][0] == "Последовательно"
    assert result.rows[1][0] == "Параллельно"
    assert result.rows[2][0] == "Ускорение"
    assert "2 000" in result.rows[0][2]
    assert service.history_count() == 1


def test_benchmark_errors(service):
    with pytest.raises(ValidationError):
        service.benchmark_report(count=10, workers=2)
    with pytest.raises(ValidationError):
        service.benchmark_report(count=2000, workers=0)


def test_history_and_clear(service):
    service.circle_report(10, 20, 1, 5)
    service.email_report(8, 7)
    assert service.history_count() == 2
    assert len(service.history(1)) == 1
    assert service.clear_history() == 2
    assert service.history_count() == 0


def test_export_history(service, tmp_path):
    service.circle_report(10, 20, 1, 5)
    service.email_report(8, 7)
    path = tmp_path / "history.csv"
    assert service.export_history(path) == 2
    with open(path, encoding="utf-8-sig", newline="") as file:
        rows = list(csv.reader(file, delimiter=";"))
    assert rows[0] == ["ID", "Задача", "Итог", "Начало", "Время, мс"]
    assert len(rows) == 3
    assert rows[1][1] == "Площади кругов"


def test_export_history_error(service, tmp_path):
    with pytest.raises(ExportError):
        service.export_history(tmp_path)
