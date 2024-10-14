"""Дополнительные функции для macro_view"""
from pathlib import Path

from constants.analytics import macro_view


def get_macro_brief_file() -> Path | None:
    """
    Получить документ macro brief

    :return: Объект типа Path или None, если файла нет
    """
    files = [f for f in macro_view.FILES_PATH.iterdir() if f.is_file()] if macro_view.FILES_PATH.exists() else []
    return files[0] if files else None
