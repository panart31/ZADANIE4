# -*- coding: utf-8 -*-
"""Сервисный слой: связываю генераторы, проверки и журнал."""

import csv
import os
import time
from itertools import islice

from .exceptions import ExportError, GenerationError
from .generators import (
    circle_areas,
    count_addresses,
    email_addresses,
    only_two_digit,
    parallel_email_addresses,
    radius_values,
)
from .models import (
    MAX_BENCH_ADDRESSES,
    MAX_EMAILS,
    RunRecord,
    TaskResult,
    check_email_length,
    check_workers,
    circle_point_count,
    format_count,
    format_number,
    parse_float,
    parse_int,
    parse_int_list,
)
from .storage import RunStorage


def process_word(value):
    """Подбираю правильное окончание слова «процесс» для числа."""
    if value % 10 == 1 and value % 100 != 11:
        return "процесс"
    if value % 10 in (2, 3, 4) and value % 100 not in (12, 13, 14):
        return "процесса"
    return "процессов"


class GenLabService:
    """Считаю задачи и записываю каждый запуск в журнал."""

    def __init__(self, storage):
        self.storage = storage

    def _save(self, task, summary, preview, duration_ms):
        """Сохраняю запись о запуске и возвращаю её номер."""
        record = RunRecord(
            task=task,
            summary=summary,
            preview=preview,
            duration_ms=duration_ms,
        )
        return self.storage.add_run(record)

    def circle_report(self, start, end, step, limit=5):
        """Считаю первые площади кругов и показываю радиус рядом с площадью."""
        started = time.perf_counter()
        start = parse_float(start, "Радиус от", minimum=0)
        end = parse_float(end, "Радиус до", minimum=0)
        step = parse_float(step, "Шаг", minimum=0)
        limit = parse_int(limit, "Сколько показать", 1, 50)
        count = circle_point_count(start, end, step)
        limit = min(limit, count)

        radii = list(islice(radius_values(start, end, step), limit))
        areas = list(islice(circle_areas(start, end, step), limit))
        rows = []
        # zip соединяет радиус и площадь в одну строку таблицы
        for index, (radius, area) in enumerate(zip(radii, areas), start=1):
            rows.append((index, format_number(radius, 2), format_number(area, 2)))

        duration_ms = (time.perf_counter() - started) * 1000
        summary = (f"Показано {len(rows)} из {format_count(count)} значений; "
                   f"формула S = πr²")
        preview = ", ".join(row[2] for row in rows[:3])
        self._save("Площади кругов", summary, preview, duration_ms)
        return TaskResult(
            task="Площади кругов",
            columns=("№", "Радиус", "Площадь"),
            rows=rows,
            summary=summary,
            duration_ms=duration_ms,
        )

    def email_report(self, length=8, count=7):
        """Беру первые адреса из бесконечного генератора."""
        started = time.perf_counter()
        length = check_email_length(length)
        count = parse_int(count, "Количество адресов", 1, MAX_EMAILS)
        addresses = list(islice(email_addresses(length), count))
        rows = [(index, address) for index, address in enumerate(addresses, start=1)]

        duration_ms = (time.perf_counter() - started) * 1000
        summary = (f"Сгенерировано {len(rows)} адресов; "
                   f"домен mail.ru, длина имени {length}")
        preview = addresses[0] if addresses else ""
        self._save("Email-адреса", summary, preview, duration_ms)
        return TaskResult(
            task="Email-адреса",
            columns=("№", "Адрес"),
            rows=rows,
            summary=summary,
            duration_ms=duration_ms,
        )

    def two_digit_report(self, text):
        """Оставляю в списке только двузначные числа через filter."""
        started = time.perf_counter()
        numbers = parse_int_list(text)
        kept = list(only_two_digit(numbers))
        rows = [(index, number) for index, number in enumerate(kept, start=1)]

        duration_ms = (time.perf_counter() - started) * 1000
        summary = (f"Из {format_count(len(numbers))} чисел двузначных: {len(kept)}")
        preview = ", ".join(str(number) for number in kept[:5])
        self._save("Двузначные числа", summary, preview, duration_ms)
        return TaskResult(
            task="Двузначные числа",
            columns=("№", "Число"),
            rows=rows,
            summary=summary,
            duration_ms=duration_ms,
        )

    def benchmark_report(self, count=1_000_000, length=8, workers=4):
        """Сравниваю обычный и параллельный генераторы адресов."""
        count = parse_int(count, "Количество адресов", 1000,
                          MAX_BENCH_ADDRESSES)
        length = check_email_length(length)
        workers = check_workers(workers)
        started = time.perf_counter()

        seq_started = time.perf_counter()
        seq_count = count_addresses(email_addresses(length), count)
        seq_time = time.perf_counter() - seq_started

        par_started = time.perf_counter()
        par_count = count_addresses(
            parallel_email_addresses(count, length, workers), count
        )
        par_time = time.perf_counter() - par_started

        if seq_count != count or par_count != count:
            raise GenerationError("генераторы выдали разное количество адресов")
        if par_time <= 0:
            raise GenerationError("не удалось измерить время параллельного запуска")
        speedup = seq_time / par_time
        duration_ms = (time.perf_counter() - started) * 1000

        rows = [
            ("Последовательно", format_number(seq_time, 3),
             f"{format_count(seq_count)} адресов"),
            ("Параллельно", format_number(par_time, 3),
             f"{format_count(par_count)} адресов"),
            ("Ускорение", f"{format_number(speedup, 2)}×",
             f"{workers} {process_word(workers)}"),
        ]
        summary = (f"{format_count(count)} адресов, {workers} "
                   f"{process_word(workers)}: параллельно быстрее в "
                   f"{format_number(speedup, 2)} раза")
        preview = f"{format_number(speedup, 2)}× на {format_count(count)} адресах"
        self._save("Скорость генератора", summary, preview, duration_ms)
        return TaskResult(
            task="Скорость генератора",
            columns=("Режим", "Время, с", "Результат"),
            rows=rows,
            summary=summary,
            duration_ms=duration_ms,
        )

    def history(self, limit=50):
        """Последние записи журнала для окна и консоли."""
        limit = parse_int(limit, "Количество записей", 1, 200)
        return self.storage.list_runs(limit)

    def history_count(self):
        """Общее количество записей в журнале."""
        return self.storage.count_runs()

    def clear_history(self):
        """Очищаю журнал и возвращаю число удалённых записей."""
        return self.storage.clear()

    def export_history(self, path):
        """Сохраняю журнал в CSV, чтобы его можно было открыть в Excel."""
        records = self.storage.list_runs(1000)
        try:
            # utf-8-sig добавляет метку BOM, иначе Excel ломает кириллицу
            with open(path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow(["ID", "Задача", "Итог", "Начало",
                                 "Время, мс"])
                for record in reversed(records):
                    writer.writerow([
                        record.run_id,
                        record.task,
                        record.summary,
                        record.created,
                        f"{record.duration_ms:.1f}".replace(".", ","),
                    ])
        except OSError as error:
            raise ExportError(f"не удалось сохранить файл: {error}") from error
        return len(records)

    def close(self):
        """Закрываю хранилище."""
        self.storage.close()


def create_service(path=None):
    """Создаю сервис с базой по умолчанию из переменной GENLAB_DB."""
    database = path or os.environ.get("GENLAB_DB", "genlab.db")
    return GenLabService(RunStorage(database))
