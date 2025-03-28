"""Модуль с оркестрацией вызова заглушек."""
from aiogram import Bot
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from sqlalchemy.ext.asyncio import AsyncSession

from constants.constants import DEFAULT_RAG_ANSWER
from constants.enums import RAGCategoryGroup
from constants.texts import texts_manager
from handlers.products.handler import main_menu
from handlers.quotes.handler import (
    bonds_info_command,
    exchange_info_command,
    metal_info_command,
    send_eco_global_stake_img,
    send_eco_rus_influence,
    send_eco_stake
)
from log.bot_logger import logger
from utils.rag_utils.classification.gags.hard_gags.client import send_company_menu
from utils.rag_utils.classification.gags.hard_gags.eco_mark import send_eco_marks
from utils.rag_utils.classification.gags.hard_gags.industry import send_industry_report
from utils.rag_utils.classification.gags.hard_gags.reports import (
    send_currency_market_anal_reports,
    send_eco_research_reports,
    send_weekly_pulse,
)
from utils.rag_utils.classification.gags.simple_gags import answer_by_gigachat, send_text_msg_and_cor
from utils.rag_utils.classification.prediction import predict_category_by_question


async def send_gag(question: str, bot: Bot, message: Message, session: AsyncSession) -> str:
    """Отправка заглушки относительно категории вопроса."""
    chat_id = message.chat.id
    msg_text = DEFAULT_RAG_ANSWER
    category = await predict_category_by_question(question)

    async with ChatActionSender(bot=bot, chat_id=chat_id):
        match category:
            case RAGCategoryGroup.currency_market_analytics:
                msg_text = await send_currency_market_anal_reports(bot, chat_id, session)

            case RAGCategoryGroup.industry_analytics:
                msg_text = await send_industry_report(question, bot, message)

            case RAGCategoryGroup.clients:
                msg_text = await send_company_menu(question, bot, message)

            case RAGCategoryGroup.unemployment:
                msg_text = await send_eco_marks(bot, chat_id, texts_manager.UNEMPLOYMENT, 'безработица')

            case RAGCategoryGroup.inner_info:
                msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.INNER_INFO, main_menu(message))

            case RAGCategoryGroup.investment:
                msg_text = await send_weekly_pulse(bot, chat_id, session)

            case RAGCategoryGroup.inflation:
                cor = send_eco_rus_influence(message)
                msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.INFLATION, cor)

            case RAGCategoryGroup.mortgage:
                msg_text = await send_eco_marks(bot, chat_id, texts_manager.MORTGAGE, 'по кредитам')

            case RAGCategoryGroup.world_cb_rates:
                cor = send_eco_global_stake_img(message, session, with_reports=False)
                msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.WORLD_CB_RATES, cor)

            case RAGCategoryGroup.current_rate:
                msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.CURRENT_RATE, send_eco_stake(message))

            case RAGCategoryGroup.exchange_rates:
                cor = exchange_info_command(message, session, with_reports=False)
                msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.EXCHANGE_RATES, cor)

            case RAGCategoryGroup.macro_analytics:
                msg_text = await send_eco_research_reports(bot, chat_id, session)

            case RAGCategoryGroup.macro_e_countries:
                msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.MACRO_E_COUNTRIES)

            case RAGCategoryGroup.taxes:
                msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.TAXES)

            case RAGCategoryGroup.bond_market:
                cor = bonds_info_command(message, session, with_reports=False)
                msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.BOND_MARKET, cor)

            case RAGCategoryGroup.commodity_price:
                cor = metal_info_command(message, session, with_reports=False)
                msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.COMMODITY_PRICE, cor)

            case RAGCategoryGroup.stock_market:
                msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.STOCK_MARKET)

            case RAGCategoryGroup.etc:
                msg_text = await send_text_msg_and_cor(bot, chat_id, texts_manager.ETC)

            case _:
                msg_text = await answer_by_gigachat(question, bot, chat_id)

    return msg_text


async def call_gag(question: str, bot: Bot, message: Message, session: AsyncSession) -> str:
    """Вызов метода с заглушками."""
    try:
        return await send_gag(question, bot, message, session)
    except Exception as e:
        logger.exception(f'*{message.chat.id}* возникла ошибка при создании заглушки для вопроса "{question}": {e}')
        await bot.send_message(message.chat.id, text=DEFAULT_RAG_ANSWER)
        return DEFAULT_RAG_ANSWER
