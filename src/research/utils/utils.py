"""Вспомогательные функции."""
from pathlib import Path


def read_file_lines(file_path: str | Path) -> list[str]:
    """Чтение файла."""
    with open(file_path, encoding='utf-8') as file:
        return file.readlines()
