"""
Доп функции для обработчика меню новостей.

Вынимает список выбранных субъектов, по которым пользователь собирается получить новости.
Обновляет список выбранных субъектов.
Оборачивает в строку список выбранных субъектов.
"""
from typing import Sequence, Callable

from pymorphy2 import MorphAnalyzer

from constants.enums import StakeholderType
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


def decline_words(words: str, case: str = 'gent', str_func: Callable = str.title) -> str:
    """
    Склоняет слова в заданный падеж.

    :param words:       Слова ("Олег Дерипаска").
    :param case:        Падеж ('datv' - дательный, 'gent' - родительный и тд).
    :param str_func:    Str функция для форматирования слов.
    :return:            Слова в нужном падеже.
    """
    name_parts = words.strip().split()
    words = ' '.join(morph.parse(name_part)[0].inflect({case}).word for name_part in name_parts)
    return str_func(words)


def get_menu_msg_by_sh_type(sh_types: Sequence[str], sh_obj: Stakeholder) -> str:
    """
    Получение сообщения в зависимости от того, кем является стейкхолдер по отношению к клиентам.

    :param sh_types:    Последовательность уникальных StakeholderType.
    :param sh_obj:      Сущность стейкхолдера.
    :return:            Строка для формирования сообщения.
    """
    lpr_text = '<b>{ben_name}</b> является ЛПР следующих компаний, выберете по которым Вы хотите получить новости {forbes_link}'
    ben_text = 'Выберите активы <b>{ben_name}</b>, по которым Вы хотите получить новости {forbes_link}'
    lpr_and_ben_text = 'Выберите из списка компании, аффилированные с <b>{ben_name}</b>, по которым Вы хотите получить новости {forbes_link}'

    match ''.join(sh_types):
        case StakeholderType.lpr:
            msg_text = lpr_text.format(ben_name=sh_obj.name.title())
        case StakeholderType.beneficiary:
            msg_text = ben_text.format(ben_name=decline_words(sh_obj.name))
        case _:
            msg_text = lpr_and_ben_text.format(ben_name=decline_words(sh_obj.name, case='ablt'))

    forbes_link = f'<a href="{sh_obj.forbes_link}">forbes.ru</a>' if sh_obj.forbes_link else ''
    return msg_text.format(forbes_link=forbes_link)


def get_show_msg_by_sh_type(sh_types: Sequence[str], sh_obj: Stakeholder, client: str = '') -> str:
    """
    Получение сообщения в зависимости от того, кем является стейкхолдер по отношению к клиентам(у).

    :param sh_types:    Последовательность уникальных StakeholderType.
    :param sh_obj:      Сущность стейкхолдера.
    :param client:      Имя единственного клиента стейкхолдера, если клиент единственный.
    :return:            Строку для формирования сообщения.
    """
    lpr_text_for_few_clients = 'Вот новости по клиентам, для которого <b>{ben_name}</b> является ЛПР'
    ben_text_for_few_clients = 'Вот новости по активам <b>{ben_name}</b>'
    lpr_and_ben_text_few_clients = 'Вот новости по компаниям, аффилированным с <b>{ben_name}</b>'
    lpr_text_for_one_client = 'Вот новости по активу <b>{ben_name}</b>\n\n'
    ben_text_for_one_client = 'Вот новости по <b>{client}</b>, для которого <b>{ben_name}</b> является ЛПР\n\n'
    match ''.join(sh_types):

        case StakeholderType.lpr:
            if client:
                return lpr_text_for_one_client.format(ben_name=decline_words(sh_obj.name))
            return lpr_text_for_few_clients.format(ben_name=sh_obj.name.title())

        case StakeholderType.beneficiary:
            ben_name = decline_words(sh_obj.name)
            if client:
                return ben_text_for_one_client.format(client=client, ben_name=ben_name)
            return ben_text_for_few_clients.format(ben_name=ben_name)

        case _:
            ben_name = decline_words(sh_obj.name, case='ablt')
            return lpr_and_ben_text_few_clients.format(ben_name=ben_name)
