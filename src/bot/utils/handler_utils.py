"""Общий доп функционал для обработчиков тг бота"""
from aiogram import types
from aiogram.enums import ChatAction

from constants import enums
from db.api.client import client_db
from log.bot_logger import logger, user_logger
from module.article_process import ArticleProcess
from utils.base import process_fin_table


async def get_client_financial_indicators(
        callback_query: types.CallbackQuery,
        client_id: int,
        fin_indicator_type: enums.FinancialIndicatorsType,
) -> None:
    """
    Отправка пользователю фин показателей по клиенту

    :param callback_query:      Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param client_id:           Выбранный клиент
    :param fin_indicator_type:  Выбранный тип фин показателей
    """
    chat_id = callback_query.message.chat.id
    user_msg = f'get_client_financial_indicators:{client_id}:{fin_indicator_type.value}'
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    client = await client_db.get(client_id)

    ap_obj = ArticleProcess(logger)
    client_fin_tables = await ap_obj.get_client_fin_indicators(client_id)
    if not client_fin_tables.empty:
        await callback_query.bot.send_chat_action(chat_id, ChatAction.UPLOAD_PHOTO)

        # Создание и отправка таблицы
        await process_fin_table(
            callback_query,
            client['name'],
            fin_indicator_type.table_name,
            client_fin_tables[fin_indicator_type.name][0],
            logger,
        )
    else:
        msg_text = f'По клиенту {client["name"]} отсутствуют финансовые показатели'
        await callback_query.message.answer(msg_text, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}"')
