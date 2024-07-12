"""
Доп функции для обработчика меню новостей.

Вынимает список выбранных субъектов, по которым пользователь собирается получить новости.
Обновляет список выбранных субъектов.
Оборачивает в строку список выбранных субъектов.
"""
from pymorphy2 import MorphAnalyzer

from handlers.news import callback_data_factories

morph = MorphAnalyzer()


def get_selected_ids_from_callback_data(callback_data: callback_data_factories.NewsMenuData) -> list[int]:
    """
    Вынимает список выбранных субъектов, по которым пользователь собирается получить новости.

    :param callback_data:   Колбэк данные, где хранится список выбранных субъектов
    :returns:               список id выбранных субъектов
    """
    return [int(i) for i in callback_data.subject_ids.split(',') if i != '0']


def update_selected_ids(selected_ids: list[int], subject_id: int) -> list[int]:
    """
    Обновляет список субъектов, по которым пользователь собирается получить новости.

    :param selected_ids:    список id выбранных субъектов
    :param subject_id:      id субъекта, который надо добавить или удалить из списк
    :returns:               обновленный список id выбранных субъектов
    """
    if subject_id:
        if subject_id in selected_ids:
            selected_ids.remove(subject_id)
        else:
            selected_ids.append(subject_id)
    return selected_ids


def wrap_selected_ids(selected_ids: list[int]) -> str:
    """
    Оборачивает список выбранных субъектов в строку.

    :param selected_ids:    список id выбранных субъектов
    :returns:               строку с выбранными субъектами
    """
    return ','.join(map(str, selected_ids)) or '0'


def decline_name(name: str, case: str = 'gent') -> str:
    """
    Склоняет слова в заданный падеж.

    :param name: Слова ("Олег Дерипаска").
    :param case: Падеж ('datv' - дательный, 'gent' - родительный и тд).
    :return:     Слова в нужном падеже.
    """
    name_parts = name.strip().split()
    return ' '.join(morph.parse(name_part)[0].inflect({case}).word for name_part in name_parts)
