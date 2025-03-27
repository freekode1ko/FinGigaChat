"""Модуль с заглушкой по клиентам."""
import ast

import pandas as pd
from aiogram import Bot, types
from langchain_core.messages import HumanMessage

from constants.texts import texts_manager
from db import models
from db.api.client import client_db, get_research_type_id_by_name
from handlers.clients import keyboards
from handlers.clients.handler import main_menu
from log.bot_logger import logger
from module.fuzzy_search import FuzzyAlternativeNames
from module.llm_langchain import giga

COMPANY_PROMPT = """\
Извлеки из вопроса "{question}" имя компании(ий), о которой(ых) спрашивает пользователь.
Ответ дай в формате списка: [имя компании, имя компании]
"""


async def get_company_name_from_question(question: str) -> list[str]:
    """Получить список из компаний, указанных в вопросе."""
    content = COMPANY_PROMPT.format(question=question)
    giga_answer = await giga.ainvoke([HumanMessage(content), ])
    giga_answer = giga_answer.replace('"', '')
    try:
        company_names = ast.literal_eval(giga_answer)
        logger.info(f'Распознанные компании: {company_names}')
        return company_names
    except (ValueError, SyntaxError) as e:
        logger.error(f'Ошибка при разборе ответа GigaChat: "{giga_answer}", error: {e}')
        return [giga_answer, ]


async def send_company_menu(question: str, bot: Bot, message: types.Message) -> str:
    """Отправить меню по клиентам, указанных в вопросе."""
    founded_clients = []
    text = texts_manager.CLIENTS
    clients_names_from_question = await get_company_name_from_question(question)

    fuzzy_searcher = FuzzyAlternativeNames()
    for name in clients_names_from_question:
        clients_ids = await fuzzy_searcher.find_subjects_id_by_name(name.lower(), subject_types=[models.ClientAlternative])
        if clients_ids:
            logger.info(f'Найден ID: {clients_ids[0]} для компании {name}')
            founded_clients.append(await client_db.get(clients_ids[0]))
        else:
            logger.warning(f'ID для компании {name} не найден')

    if founded_clients:
        await bot.send_message(message.chat.id, texts_manager.CLIENTS)

        for client in founded_clients:
            keyboard = keyboards.get_client_menu_kb(
                client['id'],
                current_page=0,
                subscribed=False,
                research_type_id=await get_research_type_id_by_name(client['name']),
                with_back_button=False
            )
            msg_text = client['name'].capitalize()
            text += msg_text
            logger.debug(f'Отправка меню для клиента: {client["name"]}')
            await message.answer(
                msg_text, reply_markup=keyboard,
                parse_mode='HTML', protect_content=texts_manager.PROTECT_CONTENT
            )
    else:
        logger.info('Клиенты не найдены, отправка стандартного меню')
        await bot.send_message(message.chat.id, text)
        await main_menu(message)
    return text
