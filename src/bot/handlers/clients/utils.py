"""Дополнительные функции для работы с клиентами

"""
import logging

from aiogram import types

from db import models
from db.api.client import client_db, get_research_type_id_by_name
from handlers.clients import keyboards
from module.fuzzy_search import FuzzyAlternativeNames


async def is_client_in_message(
        message: types.Message,
        logger: logging.Logger,
        send_message_if_client_in_message: bool = True,
        score_for_fuzzy: int = 95
) -> bool:
    """Функция для проверки, что введенное сообщение совпадает с именем клиента и отправки меню клиента

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param logger: логгер
    :param send_message_if_client_in_message: отправлять ли сообщение с меню пользователя
    :param score_for_fuzzy: величина в процентах совпадение с референсными именами клиентов
    :return: булевое значение о том ли сообщение совпадает с именем клиента
    """
    fuzzy_searcher = FuzzyAlternativeNames(logger=logger)
    clients_id = await fuzzy_searcher.find_subjects_id_by_name(message.text, subject_types=[models.ClientAlternative], score=score_for_fuzzy)
    clients = await client_db.get_by_ids(clients_id)

    if len(clients) >= 1:  # больше одного клиента найтись скорее всего не может, если большой процент совпадения стоит
        if send_message_if_client_in_message:
            client_name = clients['name'].iloc[0]
            keyboard = keyboards.get_client_menu_kb(
                clients['id'].iloc[0],
                current_page=0,
                research_type_id=await get_research_type_id_by_name(client_name),
                with_back_button=False,
            )
            msg_text = f'Выберите раздел для получения данных по клиенту <b>{client_name}</b>'
            await message.answer(msg_text, reply_markup=keyboard, parse_mode='HTML')
        return True
    return False
