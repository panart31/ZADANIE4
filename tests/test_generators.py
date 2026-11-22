"""Проверки функций-генераторов."""

import math
import random
import re
from itertools import islice

import pytest

from genlab.exceptions import ValidationError
from genlab.generators import (
    CHARS,
    email_addresses,
    only_two_digit,
    parallel_email_addresses,
    radius_values,
    circle_areas,
)

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9_]{8}@mail\.ru$")


def test_radius_values():
    assert list(radius_values(10, 12, 1)) == [10, 11, 12]
    assert list(radius_values(10, 10.5, 0.5)) == [10, 10.5]


def test_circle_areas_first_five():
    areas = list(islice(circle_areas(10, 100, 1), 5))
    expected = [math.pi * radius ** 2 for radius in (10, 11, 12, 13, 14)]
    assert len(areas) == 5
    for area, value in zip(areas, expected):
        assert math.isclose(area, value, rel_tol=1e-12)


def test_circle_areas_count_and_step():
    areas = list(circle_areas(10, 12, 0.5))
    assert len(areas) == 5
    assert math.isclose(areas[0], math.pi * 10 ** 2)
    assert math.isclose(areas[-1], math.pi * 12 ** 2)


@pytest.mark.parametrize("args", [
    (-1, 10, 1),
    (10, 9, 1),
    (10, 100, 0),
])
def test_circle_areas_errors(args):
    with pytest.raises(ValidationError):
        list(circle_areas(*args))


def test_email_generator_format():
    random.seed(42)
    addresses = list(islice(email_addresses(8), 7))
    assert len(addresses) == 7
    for address in addresses:
        assert EMAIL_PATTERN.match(address)
        assert set(address.split("@")[0]) <= set(CHARS)


def test_email_generator_custom_length():
    random.seed(1)
    address = next(email_addresses(12, "example.ru"))
    name, domain = address.split("@")
    assert len(name) == 12
    assert domain == "example.ru"
    assert set(name) <= set(CHARS)


def test_email_generator_is_infinite():
    random.seed(3)
    addresses = list(islice(email_addresses(8), 50))
    assert len(addresses) == 50


def test_only_two_digit_sample():
    numbers = [5, 12, 999, -34, 100, 7, 56]
    assert list(only_two_digit(numbers)) == [12, -34, 56]


def test_only_two_digit_returns_filter():
    result = only_two_digit([10, 11])
    assert isinstance(result, filter)


def test_parallel_email_generator():
    addresses = list(parallel_email_addresses(1500, 8, 2, 500))
    assert len(addresses) == 1500
    for address in addresses[:20]:
        assert EMAIL_PATTERN.match(address)


def test_parallel_email_generator_is_lazy():
    generator = parallel_email_addresses(2000, 8, 2, 500)
    first = list(islice(generator, 10))
    assert len(first) == 10
    assert all(EMAIL_PATTERN.match(address) for address in first)


@pytest.mark.parametrize("args", [
    (0, 8, 2, 500),
    (100, 3, 2, 500),
    (100, 8, 0, 500),
    (100, 8, 2, 50),
])
def test_parallel_email_generator_errors(args):
    with pytest.raises(ValidationError):
        list(parallel_email_addresses(*args))
