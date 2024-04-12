import datetime as dt
from typing import Any

from configs.config import BASE_DATETIME_FORMAT


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
    data['timezone'] = - int(data.get('timezone')) / 60
    data['date_start'] = dt.datetime.strptime(data.get('date_start'), BASE_DATETIME_FORMAT)
    data['date_end'] = dt.datetime.strptime(data.get('date_end'), BASE_DATETIME_FORMAT) \
        if data.get('date_end') \
        else data['date_start'] + dt.timedelta(minutes=1)

    # to utc
    data['date_start'] = data['date_start'] - dt.timedelta(hours=data['timezone'])
    data['date_end'] = data['date_end'] - dt.timedelta(hours=data['timezone'])

    return data
