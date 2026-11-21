# -*- coding: utf-8 -*-
"""Консольный режим и демонстрация для Docker."""

import argparse
import sys

from . import APP_NAME, APP_VERSION, VARIANT
from .exceptions import GenLabError
from .generators import default_workers
from .models import format_count, format_number
from .service import create_service

# в консоли Windows не всегда есть символы π, ² и ×, поэтому заменяю их
CONSOLE_REPLACEMENTS = {"πr²": "pi*r^2", "π": "pi", "²": "^2", "×": "x"}


def console_text(value):
    """Заменяю математические символы на понятные ASCII-варианты."""
    text = str(value)
    for old, new in CONSOLE_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def print_table(columns, rows, print_func=print):
    """Печатаю простую таблицу с выровненными столбцами."""
    widths = []
    for index, column in enumerate(columns):
        width = len(str(column))
        for row in rows:
            width = max(width, len(str(row[index])))
        widths.append(width)

    header = "  ".join(str(column).ljust(widths[index])
                       for index, column in enumerate(columns))
    print_func(console_text(header))
    print_func("-" * len(header))
    for row in rows:
        line = "  ".join(str(value).ljust(widths[index])
                         for index, value in enumerate(row))
        print_func(console_text(line))


def print_result(result, print_func=print):
    """Печатаю результат расчёта вместе с итогом и временем."""
    print_table(result.columns, result.rows, print_func)
    print_func(console_text(f"{result.summary}."))
    print_func(f"Время: {format_number(result.duration_ms, 2)} мс.")
    print_func("")


def run_demo(service, print_func=print):
    """Показываю все три задачи без ввода — этот режим запускается в Docker."""
    print_func(f"--- {APP_NAME} | демонстрация | вариант {VARIANT} ---")
    print_func("")

    print_func("[1] Площади кругов (радиусы 10..100, первые 5 значений)")
    circle = service.circle_report(10, 100, 1, 5)
    print_result(circle, print_func)

    print_func("[2] Email-адреса (7 штук, имя из 8 символов)")
    email = service.email_report(8, 7)
    print_result(email, print_func)

    print_func("[3] Двузначные числа из строки")
    numbers = service.two_digit_report("5 12 999 -34 100 7 56")
    print_result(numbers, print_func)

    print_func(f"Журнал: сохранено записей — {service.history_count()}.")
    return 0


def run_benchmark(service, count=1_000_000, workers=None, print_func=print):
    """Печатаю сравнение обычного и параллельного генераторов."""
    workers = workers or default_workers()
    print_func(f"--- Сравнение скорости | вариант {VARIANT} ---")
    print_func(f"Адресов: {format_count(count)}, процессов: {workers}")
    print_func("")
    result = service.benchmark_report(count=count, length=8, workers=workers)
    print_table(result.columns, result.rows, print_func)
    print_func("")
    print_func(console_text(f"{result.summary}."))
    return 0


def run_console(service, input_func=input, print_func=print):
    """Меню консольного режима: те же три задачи и журнал."""
    print_func(f"--- {APP_NAME} | ЛР №4, вариант {VARIANT} ---")
    while True:
        print_func("")
        print_func("1. Площади кругов")
        print_func("2. Email-адреса")
        print_func("3. Двузначные числа")
        print_func("4. Сравнение скорости")
        print_func("5. Журнал запусков")
        print_func("0. Выход")
        try:
            choice = input_func("Выберите пункт: ").strip()
        except EOFError:
            print_func("")
            print_func("Ввод завершён.")
            return 0
        except KeyboardInterrupt:
            print_func("")
            print_func("Выход по Ctrl+C.")
            return 0

        try:
            if choice == "1":
                start = input_func("Радиус от [10]: ").strip() or "10"
                end = input_func("Радиус до [100]: ").strip() or "100"
                step = input_func("Шаг [1]: ").strip() or "1"
                limit = input_func("Сколько показать [5]: ").strip() or "5"
                result = service.circle_report(start, end, step, limit)
                print_result(result, print_func)
            elif choice == "2":
                length = input_func("Длина имени [8]: ").strip() or "8"
                count = input_func("Сколько адресов [7]: ").strip() or "7"
                result = service.email_report(length, count)
                print_result(result, print_func)
            elif choice == "3":
                text = input_func("Введите целые числа через пробел: ")
                result = service.two_digit_report(text)
                print_result(result, print_func)
            elif choice == "4":
                count = input_func("Сколько адресов [1000000]: ").strip() or "1000000"
                workers = (input_func("Процессов [4]: ").strip()
                           or str(default_workers()))
                result = service.benchmark_report(count=count, length=8,
                                                 workers=workers)
                print_result(result, print_func)
            elif choice == "5":
                records = service.history(10)
                print_func(f"Записей показано: {len(records)} "
                           f"из {service.history_count()}.")
                for record in records:
                    print_func(console_text(record))
            elif choice == "0":
                print_func("До встречи.")
                return 0
            else:
                print_func("Нет такого пункта меню.")
        except GenLabError as error:
            print_func(f"Ошибка: {error}")
        except (EOFError, KeyboardInterrupt):
            print_func("")
            print_func("Ввод завершён.")
            return 0


def build_parser():
    """Описываю параметры командной строки."""
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument("--console", action="store_true",
                        help="запустить консольное меню")
    parser.add_argument("--demo", action="store_true",
                        help="показать три задачи без ввода")
    parser.add_argument("--benchmark", action="store_true",
                        help="сравнить обычный и параллельный генераторы")
    parser.add_argument("--count", type=int, default=1_000_000,
                        help="количество адресов для замера")
    parser.add_argument("--workers", type=int, default=None,
                        help="количество процессов для замера")
    parser.add_argument("--db", default=None,
                        help="путь к файлу журнала SQLite")
    parser.add_argument("--version", action="version",
                        version=f"{APP_NAME} {APP_VERSION}")
    return parser


def main(argv=None):
    """Выбираю режим запуска: окно, консоль, демонстрация или замер."""
    args = build_parser().parse_args(argv)

    if args.console or args.demo or args.benchmark:
        service = create_service(args.db)
        try:
            if args.demo:
                return run_demo(service)
            if args.benchmark:
                return run_benchmark(service, args.count, args.workers)
            return run_console(service)
        except GenLabError as error:
            print(f"Ошибка: {error}")
            return 1
        finally:
            service.close()

    # PySide6 импортирую только для графического режима: Docker запускает демо
    try:
        from PySide6.QtWidgets import QApplication
        from .ui import MainWindow, apply_theme
    except ImportError:
        print("PySide6 не установлен. Установите зависимости:")
        print("  pip install -r requirements.txt")
        print("Или запустите консольный режим: python main.py --console")
        return 1

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    apply_theme(app)
    service = create_service(args.db)
    window = MainWindow(service)
    window.show()
    return app.exec()
