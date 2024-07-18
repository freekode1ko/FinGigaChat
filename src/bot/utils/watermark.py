"""Функции для создания слайда с текстом вотермарки и наложения вотермарки на pdf файлы."""

import subprocess
from pathlib import Path

from constants.texts import texts_manager


def add_watermark_cli(
        input_pdf: str | Path,
        output_pdf: str | Path,
        watermark: str,
        font_type: str = texts_manager.FONT_TYPE,
        font_size: int = texts_manager.FONT_SIZE,
        rotation: int = texts_manager.ROTATION,
        lines_count: int = texts_manager.VERTICAL_REPETITIONS,
        word_in_line_count: int = texts_manager.HORIZONTAL_REPETITIONS,
        opacity: float = texts_manager.FONT_COLOR_ALPHA,
) -> None:
    """
    Добавить вотермарку к pdf файлу.

    Работает быстрее, удобнее, но запускается из командной строки (надо проверить работу в рамках контейнера).

    :param input_pdf:               Путь к файлу, к которому надо добавить вотермарку
    :param output_pdf:              Путь сохранения файла с вотермаркой
    :param watermark:               Текст вотермарки
    :param font_type:               Шрифт текста
    :param font_size:               Размера шрифта
    :param rotation: Угол наклона текста
    :param lines_count:             Кол-во строк на странице с вотермаркой
    :param word_in_line_count:      Кол-во повторений слова в строке
    :param opacity:                 Прозрачность текста
    """
    cmd = [
        'watermark',
        'grid',
        '-s', str(output_pdf),
        '-tf', str(font_type),
        '-ts', str(font_size),
        '-a', str(rotation),
        '-h', str(lines_count),
        '-v', str(word_in_line_count),
        '-o', str(opacity),
        # '--save-as-image',  # преобразует все страницы в картинки
        str(input_pdf),
        watermark,
    ]

    try:
        subprocess.call(cmd)
    except subprocess.SubprocessError as e:
        print(f'Error: {e}')
