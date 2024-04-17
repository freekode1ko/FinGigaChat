import datetime as dt
from typing import Any

from config import BASE_DATETIME_FORMAT, SERVER_DATE_FORMAT


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
