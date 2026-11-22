"""Проверки консольного режима."""

from genlab.cli import run_console, run_demo


def make_input(values):
    """Возвращаю функцию ввода, которая выдаёт заранее заданные строки."""
    iterator = iter(values)
    return lambda prompt="": next(iterator)


def test_demo_output(service):
    lines = []
    assert run_demo(service, lines.append) == 0
    text = "\n".join(lines)
    assert "[1] Площади кругов" in text
    assert "314,16" in text
    assert "[2] Email-адреса" in text
    assert "@mail.ru" in text
    assert "[3] Двузначные числа" in text
    assert "12" in text
    assert "Журнал: сохранено записей — 3" in text


def test_console_exit(service):
    lines = []
    assert run_console(service, make_input(["0"]), lines.append) == 0
    assert "До встречи" in "\n".join(lines)


def test_console_circle_flow(service):
    lines = []
    code = run_console(
        service,
        make_input(["1", "10", "12", "1", "3", "0"]),
        lines.append,
    )
    text = "\n".join(lines)
    assert code == 0
    assert "314,16" in text
    assert "380,13" in text
    assert "452,39" in text
    assert "Показано 3 из 3 значений" in text


def test_console_error_and_journal(service):
    lines = []
    code = run_console(
        service,
        make_input(["1", "abc", "100", "1", "5", "5", "0"]),
        lines.append,
    )
    text = "\n".join(lines)
    assert code == 0
    assert "Ошибка: Радиус от" in text
    assert "Записей показано: 0" in text
