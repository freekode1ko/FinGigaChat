"""Дополнительные функции для работы с клиентами"""
from typing import Sequence

from aiogram import types

from constants.enums import StakeholderType
from constants.texts import texts_manager
from db import models
from db.api.client import client_db, get_research_type_id_by_name
from handlers.clients import keyboards
from module.fuzzy_search import FuzzyAlternativeNames


async def is_client_in_message(
        message: types.Message,
        send_message_if_client_in_message: bool = True,
        fuzzy_score: int = 95
) -> bool:
    """Функция для проверки, что введенное сообщение совпадает с именем клиента и отправки меню клиента

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param send_message_if_client_in_message: отправлять ли сообщение с меню пользователя
    :param fuzzy_score: величина в процентах совпадение с референсными именами клиентов
    :return: булевое значение о том ли сообщение совпадает с именем клиента
    """
    clients_id = await FuzzyAlternativeNames().find_subjects_id_by_name(
        message.text.replace(texts_manager.CLIENT_ADDITIONAL_INFO, ''),
        subject_types=[models.ClientAlternative],
        score=fuzzy_score
    )
    clients = await client_db.get_by_ids(clients_id)

    if len(clients) >= 1:  # больше одного клиента найтись скорее всего не может, если большой процент совпадения стоит
        if send_message_if_client_in_message:
            client_name: str = clients['name'].iloc[0]
            keyboard = keyboards.get_client_menu_kb(
                clients['id'].iloc[0],
                current_page=0,
                research_type_id=await get_research_type_id_by_name(client_name),
                with_back_button=False,
            )
            msg_text = texts_manager.CHOOSE_CLIENT_SECTION.format(name=client_name.capitalize())
            await message.answer(msg_text, reply_markup=keyboard, parse_mode='HTML')
        return True
    return False


def get_menu_msg_by_sh_type(sh_types: Sequence[str], sh_obj: models.Stakeholder) -> str:
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


def get_show_msg_by_sh_type(sh_types: Sequence[str], sh_obj: models.Stakeholder, client: str = '') -> str:
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
