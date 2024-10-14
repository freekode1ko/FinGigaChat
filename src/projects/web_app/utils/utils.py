import datetime as dt
import subprocess
from typing import Any

from pathlib import Path

from config import BASE_DATETIME_FORMAT, SERVER_DATE_FORMAT

SUBPROCESS_CALL_TIMEOUT = 30

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


def add_watermark_cli(
        input_pdf: str | Path,
        output_pdf: str | Path,
        watermark: str,
        font_type: str = 'Helvetica',  # FIXME: достать константы из редиса
        font_size: int = 20,  # FIXME: достать константы из редиса
        rotation: int = 45,  # FIXME: достать константы из редиса
        lines_count: int = 3,  # FIXME: достать константы из редиса
        word_in_line_count: int = 3,  # FIXME: достать константы из редиса
        opacity: float = 0.3,  # FIXME: достать константы из редиса
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

    subprocess.call(cmd, timeout=SUBPROCESS_CALL_TIMEOUT)
