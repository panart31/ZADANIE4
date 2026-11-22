"""Проверки разбора чисел и вспомогательных структур."""

import math

import pytest

from genlab.exceptions import ValidationError
from genlab.models import (
    RunRecord,
    TaskResult,
    circle_point_count,
    format_count,
    format_number,
    number_text,
    parse_float,
    parse_int,
    parse_int_list,
)


def test_parse_float_with_dot():
    assert parse_float("2.5", "Шаг") == 2.5
    assert parse_float(10, "Радиус") == 10.0


def test_parse_float_with_comma():
    assert parse_float("0,5", "Шаг") == 0.5
    assert parse_float(" 12,75 ", "Радиус") == 12.75


@pytest.mark.parametrize("value", ["", "  ", "abc", "12,3,4", True])
def test_parse_float_rejects_bad_text(value):
    with pytest.raises(ValidationError):
        parse_float(value, "Шаг")


@pytest.mark.parametrize("value", [float("nan"), float("inf"),
                                   float("-inf")])
def test_parse_float_rejects_non_finite(value):
    with pytest.raises(ValidationError):
        parse_float(value, "Шаг")


def test_parse_float_limits():
    assert parse_float("1", "Шаг", minimum=0) == 1.0
    with pytest.raises(ValidationError):
        parse_float("-1", "Шаг", minimum=0)
    with pytest.raises(ValidationError):
        parse_float("101", "Шаг", maximum=100)


def test_parse_int():
    assert parse_int("7", "Количество") == 7
    assert parse_int(7, "Количество") == 7
    for value in ("", "7.5", "abc", True):
        with pytest.raises(ValidationError):
            parse_int(value, "Количество")
    with pytest.raises(ValidationError):
        parse_int(0, "Количество", minimum=1)
    with pytest.raises(ValidationError):
        parse_int(11, "Количество", maximum=10)


def test_parse_int_list_with_spaces():
    assert parse_int_list("5 12 999 -34") == [5, 12, 999, -34]


def test_parse_int_list_with_commas_and_semicolons():
    assert parse_int_list("5, 12; 7") == [5, 12, 7]


def test_parse_int_list_errors():
    with pytest.raises(ValidationError):
        parse_int_list("")
    with pytest.raises(ValidationError) as error:
        parse_int_list("5 12 abc 7")
    assert "abc" in str(error.value)
    assert "№3" in str(error.value)
    with pytest.raises(ValidationError):
        parse_int_list("1 2 3 4", limit=3)


def test_circle_point_count():
    assert circle_point_count(10, 100, 1) == 91
    assert circle_point_count(10, 10.5, 0.5) == 2
    assert circle_point_count(10, 10.4, 0.5) == 1


@pytest.mark.parametrize("args", [
    (-1, 10, 1),
    (0, 10, 1),
    (10, 100, 0),
    (10, 100, -1),
    (20, 10, 1),
    (10, 100, 0.00001),
])
def test_circle_point_count_errors(args):
    with pytest.raises(ValidationError):
        circle_point_count(*args)


def test_number_formatting():
    assert format_number(314.159265) == "314,16"
    assert format_number(1234.5) == "1 234,50"
    assert format_count(100000) == "100 000"
    assert number_text(10.0) == "10"
    assert number_text(10.5) == "10,5"


def test_run_record_defaults():
    record = RunRecord("Круги", "5 значений", "314,16", 0.4)
    assert len(record.created) == 19
    assert record.run_id is None
    assert "Круги" in str(record)
    assert "5 значений" in str(record)


def test_task_result_string():
    result = TaskResult("Круги", ("№", "Площадь"), [(1, "314,16")],
                        "Показано 1 значение", 0.3)
    assert "Круги" in str(result)
    assert "Показано" in str(result)
    assert math.isclose(result.duration_ms, 0.3)
