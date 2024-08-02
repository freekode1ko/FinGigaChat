"""
Доп функции для обработчика меню новостей.

Вынимает список выбранных субъектов, по которым пользователь собирается получить новости.
Обновляет список выбранных субъектов.
Оборачивает в строку список выбранных субъектов.
"""
from typing import Callable, Iterable, Sequence

from pymorphy2 import MorphAnalyzer

from constants.enums import StakeholderType
from constants.texts.texts_manager import texts_manager
from db.models import Stakeholder
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


def decline_words(words: str, case: Iterable[str] = 'gent', str_func: Callable = str.title) -> str:
    """
    Склоняет слова в заданный падеж.

    :param words:       Слова ("Олег Дерипаска").
    :param case:        Падеж ('datv' - дательный, 'gent' - родительный и тд).
    :param str_func:    Str функция для форматирования слов.
    :return:            Слова в нужном падеже.
    """
    name_parts = words.strip().split()
    words = ' '.join(morph.parse(name_part)[0].inflect(set(case)).word for name_part in name_parts)
    return str_func(words)


def get_menu_msg_by_sh_type(sh_types: Sequence[str], sh_obj: Stakeholder) -> str:
    """
    Получение текста для меню стейкхолдеров в зависимости от того, кем является стейкхолдер по отношению к клиентам.

    :param sh_types:    Последовательность уникальных StakeholderType.
    :param sh_obj:      Сущность стейкхолдера.
    :return:            Строка для формирования сообщения.
    """
    match ''.join(sh_types):
        case StakeholderType.lpr:
            msg_text = texts_manager.LPR_MENU_NEWS
        case StakeholderType.beneficiary:
            msg_text = texts_manager.BEN_MENU_NEWS
        case _:
            msg_text = texts_manager.COMMON_MENU_NEWS

    forbes_link = texts_manager.BIO_LINK.format(link=sh_obj.forbes_link) if sh_obj.forbes_link else ''
    return msg_text + forbes_link


def get_show_msg_by_sh_type(sh_types: Sequence[str], sh_obj: Stakeholder, client: str = '') -> str:
    """
    Получение текста для отображения новостей в зависимости от того, кем является стейкхолдер по отношению к клиентам(у).

    :param sh_types:    Последовательность уникальных StakeholderType.
    :param sh_obj:      Сущность стейкхолдера.
    :param client:      Имя единственного клиента стейкхолдера, если клиент единственный.
    :return:            Строку для формирования сообщения.
    """
    # forbes_link = texts_manager.BIO_LINK.format(link=sh_obj.forbes_link) if sh_obj.forbes_link else ''
    match ''.join(sh_types):
        case StakeholderType.lpr:
            # sh_name = sh_obj.name.title()
            if client:
                return texts_manager.ONE_LPR_SHOW_NEWS.format(client=client)
            return texts_manager.FEW_LPR_SHOW_NEWS
        case StakeholderType.beneficiary:
            # sh_name = decline_words(sh_obj.name)
            if client:
                return texts_manager.ONE_BEN_SHOW_NEWS
            return texts_manager.FEW_BEN_SHOW_NEWS
        case _:
            # sh_name = decline_words(sh_obj.name, case='ablt')
            if client:
                return texts_manager.ONE_COMMON_SHOW_NEWS
            return texts_manager.FEW_COMMON_SHOW_NEWS
