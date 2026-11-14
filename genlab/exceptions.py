# -*- coding: utf-8 -*-
"""Собственные исключения приложения."""


class GenLabError(Exception):
    """Общая ошибка «Генераторной станции»."""


class ValidationError(GenLabError):
    """Некорректные входные данные."""


class GenerationError(GenLabError):
    """Генератор не смог выдать результат."""


class StorageError(GenLabError):
    """Ошибка при работе с журналом в SQLite."""


class ExportError(GenLabError):
    """Не удалось сохранить файл."""
