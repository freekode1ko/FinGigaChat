"""Дополнительные функции для работы с клиентами"""
from aiogram import types

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
