"""Методы для вызова простых заглушек."""
import re
from typing import Coroutine

from aiogram import Bot
from langchain_core.messages import HumanMessage

from constants.texts import texts_manager
from module.llm_langchain import giga


async def send_text_msg_and_cor(bot: Bot, chat_id: int, text: str, cor: Coroutine | None = None) -> str:
    """Отправка заглушки в виде текстового сообщения."""
    await bot.send_message(chat_id, text, parse_mode='HTML', disable_web_page_preview=True)
    if cor:
        await cor
    return text


async def answer_by_gigachat(question: str, bot: Bot, chat_id: int) -> str:
    """Отправка заглушки GigaChat."""
    response = await giga.ainvoke([HumanMessage(question), ])
    if not response:
        await bot.send_message(chat_id, texts_manager.RAG_ERROR_ANSWER)
        return texts_manager.RAG_ERROR_ANSWER

    response = re.sub(r'#+\s*(.+)', r'*\1*', response)
    await bot.send_message(chat_id, texts_manager.OTHER)
    await bot.send_message(chat_id, text=response, parse_mode='Markdown')
    return texts_manager.OTHER + ': ' + response
