"""
Обработчик меню сырьевые товары.

Позволяет получить различную информацию о комодах:
- новости
- котировки
"""
import datetime

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.chat_action import ChatActionMiddleware

import utils
from db import models
from db.api.commodity import commodity_db
from handlers.commodity.callbacks import CommodityMenuData, CommodityMenusEnum
from handlers.commodity.keyboards import get_menu_kb, get_period_kb
from handlers.quotes import metal_info_command
from log.bot_logger import user_logger
from module.article_process import FormatText

router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message use chat action 'typing'


@router.callback_query(CommodityMenuData.filter(F.menu == CommodityMenusEnum.commodity_menu))
async def commodity_menu(
        callback_query: CallbackQuery,
        callback_data: CommodityMenuData,
) -> None:
    """
    Входная точка для новостей и котировок по комодам

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Объект, содержащий дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    commodity_info = await commodity_db.get(callback_data.commodity_id)
    keyboard = get_menu_kb(callback_data.commodity_id)
    msg_text = f'Выберите раздел для получения данных по клиенту <b>{commodity_info["name"].capitalize()}</b>'

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')

    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(CommodityMenuData.filter(F.menu == CommodityMenusEnum.choice_period))
async def commodity_choice_news_menu(
        callback_query: CallbackQuery,
        callback_data: CommodityMenuData,
) -> None:
    """
    Выбор периода для получения новостей

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Объект, содержащий дополнительную информацию
    """
    commodity_info = await commodity_db.get(callback_data.commodity_id)
    msg_text = f'Выберите период для получения новостей по клиенту <b>{commodity_info["name"].capitalize()}</b>'

    await callback_query.message.edit_text(msg_text, reply_markup=get_period_kb(callback_data.commodity_id), parse_mode='HTML')

    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(CommodityMenuData.filter(F.menu == CommodityMenusEnum.news))
async def commodity_news_menu(
        callback_query: CallbackQuery,
        callback_data: CommodityMenuData,
) -> None:
    """
    Функция для отправки новостей

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Объект, содержащий дополнительную информацию
    """
    commodity_id = callback_data.commodity_id
    days = callback_data.days_count
    commodity_info = await commodity_db.get(commodity_id)

    to_date = datetime.datetime.now()
    from_date = to_date - datetime.timedelta(days=days)

    msg_text = f'Новости по клиенту <b>{commodity_info["name"].capitalize()}</b> за {days} дней\n'
    articles = await commodity_db.get_articles_by_subject_ids(commodity_id, from_date, to_date, order_by=models.Article.date.desc())

    if not articles:
        msg_text += 'отсутствуют'
        await callback_query.message.answer(msg_text, parse_mode='HTML')
    else:
        frmt_msg = f'<b>{commodity_info["name"].capitalize()}</b>'

        all_articles = '\n\n'.join(
            FormatText(
                title=article.title, date=article.date, link=article.link, text_sum=article.text_sum
            ).make_subject_text()
            for article, _ in articles
        )
        frmt_msg += f'\n\n{all_articles}'
        await callback_query.message.answer(msg_text, parse_mode='HTML')
        await utils.base.bot_send_msg(callback_query.bot, callback_query.from_user.id, frmt_msg)
        await utils.base.send_full_copy_of_message(callback_query)

    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(CommodityMenuData.filter(F.menu == CommodityMenusEnum.quotes))
async def commodity_quotes_menu(
        callback_query: CallbackQuery,
        callback_data: CommodityMenuData,
) -> None:
    """
    Отправка котировок

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Объект, содержащий дополнительную информацию
    """
    await metal_info_command(callback_query.message)
    await utils.base.send_full_copy_of_message(callback_query)

    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(CommodityMenuData.filter(F.menu == CommodityMenusEnum.close))
async def commodity_close_menu(
        callback_query: CallbackQuery,
        callback_data: CommodityMenuData,
) -> None:
    """
    Закрыть меню

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Объект, содержащий дополнительную информацию
    """
    await callback_query.message.edit_text(
        text='Просмотр по сырьевому товару завершен',
        reply_markup=None,
    )

    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
