# -*- coding: utf-8 -*-
"""Функции-генераторы для трёх задач варианта 16."""

import math
import os
import random
from concurrent.futures import ProcessPoolExecutor
from string import ascii_lowercase, ascii_uppercase

from .exceptions import GenerationError, ValidationError
from .models import (
    MAX_BENCH_ADDRESSES,
    check_email_length,
    check_workers,
    circle_point_count,
    parse_int,
)

# набор символов для email-адресов из задания
CHARS = ascii_lowercase + ascii_uppercase + "0123456789_"
EMAIL_DOMAIN = "mail.ru"
TWO_DIGIT_MIN = 10
TWO_DIGIT_MAX = 99


def radius_values(start, end, step):
    """Выдаю радиусы по одному, не накапливая ошибку сложения float."""
    count = circle_point_count(start, end, step)
    for index in range(count):
        yield start + index * step


def circle_areas(start=10.0, end=100.0, step=1.0):
    """Выдаю площади кругов по формуле S = πr².

    Проверки выполняются при первом обращении к генератору, потому что тело
    функции с yield запускается только в момент next().
    """
    for radius in radius_values(start, end, step):
        yield math.pi * radius * radius


def email_addresses(length=8, domain=EMAIL_DOMAIN):
    """Бесконечно выдаю адреса из случайных букв, цифр и подчёркиваний."""
    length = check_email_length(length)
    if not isinstance(domain, str) or not domain.strip():
        raise ValidationError("Домен адреса не может быть пустым")
    while True:
        name = "".join(random.choice(CHARS) for _ in range(length))
        yield f"{name}@{domain}"


def only_two_digit(numbers):
    """Оставляю двузначные по модулю числа с помощью filter.

    Например, 12 и -34 остаются, а 5, 100 и 999 отбрасываются.
    """
    return filter(lambda number: TWO_DIGIT_MIN <= abs(number) <= TWO_DIGIT_MAX,
                  numbers)


def _email_chunk(bounds):
    """Генерирую пачку адресов в отдельном процессе.

    Функция должна быть на верхнем уровне модуля, иначе Windows не сможет
    передать её дочернему процессу.
    """
    count, length, seed = bounds
    generator = random.Random(seed)
    choose = generator.choice
    return [
        "".join(choose(CHARS) for _ in range(length)) + "@" + EMAIL_DOMAIN
        for _ in range(count)
    ]


def parallel_email_addresses(count, length=8, workers=2, chunk_size=10_000):
    """Выдаю адреса партиями: каждый процесс считает свой кусок.

    Генератор остаётся ленивым: в памяти лежит только одна пачка адресов,
    а не все значения сразу.
    """
    count = parse_int(count, "Количество адресов", 1, MAX_BENCH_ADDRESSES)
    length = check_email_length(length)
    workers = check_workers(workers)
    chunk_size = parse_int(chunk_size, "Размер пачки", 100, 100_000)

    parts = []
    for offset in range(0, count, chunk_size):
        size = min(chunk_size, count - offset)
        # у каждого процесса свой генератор случайных чисел
        parts.append((size, length, random.randrange(1, 1_000_000_000)))
    workers = min(workers, len(parts))

    # процессам передаю только границы пачек, а не готовые адреса
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for batch in pool.map(_email_chunk, parts):
            yield from batch


def default_workers():
    """Беру для замера не больше четырёх процессов, чтобы не перегружать слабый ПК."""
    return max(1, min(4, os.cpu_count() or 1))


def count_addresses(addresses, count):
    """Считаю, сколько адресов реально выдал генератор, и проверяю итог."""
    total = 0
    for _ in range(count):
        try:
            next(addresses)
        except StopIteration:
            break
        total += 1
    if total != count:
        raise GenerationError(
            f"генератор выдал {total} адресов вместо {count}"
        )
    return total
