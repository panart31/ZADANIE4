# -*- coding: utf-8 -*-
"""Проверка ввода и небольшие структуры данных для журнала."""

import math
from dataclasses import dataclass, field
from datetime import datetime

from .exceptions import ValidationError

MAX_POINTS = 1_000_000
MAX_EMAILS = 1000
MAX_NUMBERS = 10_000
MAX_BENCH_ADDRESSES = 2_000_000
MIN_EMAIL_LENGTH = 4
MAX_EMAIL_LENGTH = 32
MIN_WORKERS = 1
MAX_WORKERS = 16


def number_text(value):
    """Показываю число без лишнего нуля после запятой: 10, а не 10.0."""
    if float(value).is_integer():
        return str(int(value))
    return str(value).replace(".", ",")


def format_number(value, digits=2):
    """Показываю число с пробелами между тысячами и запятой в дробной части."""
    text = f"{value:,.{digits}f}"
    return text.replace(",", " ").replace(".", ",")


def format_count(value):
    """Показываю целое количество с пробелами между тысячами."""
    return f"{int(value):,}".replace(",", " ")


def parse_float(value, field, minimum=None, maximum=None):
    """Проверяю число: принимаю запятую, отбрасываю NaN, бесконечность и bool."""
    # bool в Python является подклассом int, поэтому его проверяю отдельно
    if isinstance(value, bool):
        raise ValidationError(f"{field}: нужно число, а не логическое значение")
    if isinstance(value, str):
        text = value.strip().replace(",", ".")
        if not text:
            raise ValidationError(f"{field}: поле не заполнено")
        try:
            number = float(text)
        except ValueError:
            raise ValidationError(f"{field}: «{value}» не является числом") from None
    elif isinstance(value, (int, float)):
        number = float(value)
    else:
        raise ValidationError(f"{field}: ожидается число")
    if not math.isfinite(number):
        raise ValidationError(f"{field}: число должно быть конечным")
    if minimum is not None and number < minimum:
        raise ValidationError(
            f"{field}: значение должно быть не меньше {number_text(minimum)}"
        )
    if maximum is not None and number > maximum:
        raise ValidationError(
            f"{field}: значение должно быть не больше {number_text(maximum)}"
        )
    return number


def parse_int(value, field, minimum=None, maximum=None):
    """Проверяю целое число, например количество строк или процессов."""
    if isinstance(value, bool):
        raise ValidationError(f"{field}: нужно целое число, а не логическое значение")
    if isinstance(value, int):
        number = value
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValidationError(f"{field}: поле не заполнено")
        try:
            number = int(text)
        except ValueError:
            raise ValidationError(f"{field}: «{value}» не является целым числом") from None
    else:
        raise ValidationError(f"{field}: ожидается целое число")
    if minimum is not None and number < minimum:
        raise ValidationError(f"{field}: значение должно быть не меньше {minimum}")
    if maximum is not None and number > maximum:
        raise ValidationError(f"{field}: значение должно быть не больше {maximum}")
    return number


def parse_int_list(text, limit=MAX_NUMBERS):
    """Разбираю строку с целыми числами: пробелы, запятые и точки с запятой."""
    if not isinstance(text, str):
        raise ValidationError("Список чисел: ожидается строка")
    # пользователь может разделить числа не только пробелами
    cleaned = text.replace(",", " ").replace(";", " ")
    tokens = cleaned.split()
    if not tokens:
        raise ValidationError("Список чисел: введите хотя бы одно число")
    if len(tokens) > limit:
        raise ValidationError(f"Список чисел: не больше {format_count(limit)} значений")
    try:
        # map применяет int к каждому элементу, как требует задание
        return list(map(int, tokens))
    except ValueError:
        for index, token in enumerate(tokens, start=1):
            try:
                int(token)
            except ValueError:
                raise ValidationError(
                    f"Список чисел: элемент №{index} «{token}» не является целым числом"
                ) from None
        raise ValidationError("Список чисел: не удалось разобрать строку") from None


def circle_point_count(start, end, step):
    """Считаю количество радиусов в диапазоне и сразу проверяю границы."""
    # радиус и шаг должны быть положительными, иначе площадь теряет смысл
    if start <= 0 or end <= 0:
        raise ValidationError("Радиусы должны быть больше нуля")
    if step <= 0:
        raise ValidationError("Шаг должен быть больше нуля")
    if start > end:
        raise ValidationError("Начальный радиус не может быть больше конечного")
    # небольшой запас убирает ошибку округления при делении
    count = int(math.floor((end - start) / step + 1e-9)) + 1
    if count > MAX_POINTS:
        raise ValidationError(
            f"Слишком много значений: {format_count(count)}, "
            f"допустимо не больше {format_count(MAX_POINTS)}"
        )
    return count


def check_email_length(value):
    """Проверяю длину имени адреса: от 4 до 32 символов."""
    return parse_int(value, "Длина адреса", MIN_EMAIL_LENGTH, MAX_EMAIL_LENGTH)


def check_workers(value):
    """Проверяю количество процессов для параллельного генератора."""
    return parse_int(value, "Количество процессов", MIN_WORKERS, MAX_WORKERS)


@dataclass
class TaskResult:
    """Результат одного расчёта: таблица, итог и время работы."""

    task: str
    columns: tuple
    rows: list
    summary: str
    duration_ms: float

    def __str__(self):
        return f"{self.task}: {self.summary}"


@dataclass
class RunRecord:
    """Запись журнала: что считали, с каким итогом и сколько это заняло."""

    task: str
    summary: str
    preview: str
    duration_ms: float
    created: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    run_id: int | None = None

    def __str__(self):
        return f"{self.created} | {self.task} | {self.summary}"
