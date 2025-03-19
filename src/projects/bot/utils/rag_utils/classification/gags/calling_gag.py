"""Модуль с оркестрацией вызова заглушек."""
from aiogram import Bot
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from constants.enums import RAGCategoryGroup
from constants.texts import texts_manager
from handlers.products.handler import main_menu
from handlers.quotes.handler import (
    exchange_info_command,
    send_eco_global_stake_img,
    send_eco_rus_influence,
    send_eco_stake
)
from utils.rag_utils.classification.gags.simple_gags import answer_by_gigachat, send_text_msg_and_cor
from utils.rag_utils.classification.prediction import predict_category_by_question


async def call_gag(question: str, bot: Bot, chat_id: int, message: Message, session: AsyncSession) -> str:
    """Вызов заглушки относительно категории вопроса."""
    # TODO: рефакторинг, когда будут все заглушки
    category = await predict_category_by_question(question)
    match category:
        case RAGCategoryGroup.stock_market:
            msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.STOCK_MARKET)
        case RAGCategoryGroup.etc:
            msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.ETC)
        case RAGCategoryGroup.taxes:
            msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.TAXES)
        case RAGCategoryGroup.macro_e_countries:
            msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.MACRO_E_COUNTRIES)
        case RAGCategoryGroup.inner_info:
            msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.INNER_INFO, main_menu(message))
        case RAGCategoryGroup.inflation:
            cor = send_eco_rus_influence(message)
            msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.INFLATION, cor)
        case RAGCategoryGroup.world_cb_rates:
            cor = send_eco_global_stake_img(message, session, with_reports=False)
            msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.WORLD_CB_RATES, cor)
        case RAGCategoryGroup.current_rate:
            msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.CURRENT_RATE, send_eco_stake(message))
        case RAGCategoryGroup.exchange_rates:
            cor = exchange_info_command(message, session, with_reports=False)
            msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.EXCHANGE_RATES, cor)
        case _:
            msg_text = await answer_by_gigachat(question, bot, chat_id)
    return msg_text
