import re
import datetime as dt
import subprocess
from typing import Any

from pathlib import Path

from config import BASE_DATETIME_FORMAT, SERVER_DATE_FORMAT


SUBPROCESS_CALL_TIMEOUT = 30


def transform_path_to_link(path: str) -> str | None:
    """Преобразование пути к файлу в абсолютную ссылку"""
    return f'/{path.lstrip("/code/").lstrip("/")}' if len(path.strip()) else None


def is_valid_email(email: str) -> bool:
    """
    Проверка, что Email корпоративный

    :param email: Email для проверки
    :return: True, если Email корпоративный, иначе False
    """
    return re.search(r'\w+@sber(bank)?.ru', email) is not None


def format_date(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Преобразование времени начала встречи в определенный формат.

    :param data: данные о встречах пользователя
    return: данные о встречах пользователя с новым форматом времени начала
    """
    for i, row in enumerate(data):
        date_start = row['date_start'] + dt.timedelta(hours=row['timezone'])
        data[i]['date_start'] = date_start.strftime(BASE_DATETIME_FORMAT)
    return data


def reformat_data(data: dict[str: Any]) -> dict[str: Any]:
    """
    Получение и преобразование данных из формы

    :param data: Request с данными из формы
    :return: отформатированные данные
    """
    data['timezone'] = - int(data['timezone']) / 60

    data['date_start'] = dt.datetime.strptime(data['date_start'], SERVER_DATE_FORMAT)
    data['date_start'] = data['date_start'].replace(second=0, microsecond=0, tzinfo=None)

    data['date_end'] = dt.datetime.strptime(data['date_end'], SERVER_DATE_FORMAT)
    data['date_end'] = data['date_end'].replace(second=0, microsecond=0, tzinfo=None)

    return data


async def add_watermark_cli(
        input_pdf: str | Path,
        output_pdf: str | Path,
        watermark: str,
        font_type: str,
        font_size: int,
        rotation: int,
        lines_count: int,
        word_in_line_count: int,
        opacity: float,
) -> None:
    """
    Добавить вотермарку к pdf файлу.

    Работает быстрее, удобнее, но запускается из командной строки (надо проверить работу в рамках контейнера).

    :param input_pdf:               Путь к файлу, к которому надо добавить вотермарку
    :param output_pdf:              Путь сохранения файла с вотермаркой
    :param watermark:               Текст вотермарки
    :param font_type:               Шрифт текста
    :param font_size:               Размера шрифта
    :param rotation:                Угол наклона текста
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

    subprocess.call(cmd, timeout=SUBPROCESS_CALL_TIMEOUT)
