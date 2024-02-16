# import logging
from datetime import timedelta
from typing import Union

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionMiddleware

from bot_logger import user_logger
from constants.bot.industry import SELECTED_INDUSTRY_TOKEN, MY_TG_CHANNELS_CALLBACK_TEXT, ALL_TG_CHANNELS_CALLBACK_TEXT, \
    BACK_TO_MENU, GET_INDUSTRY_TG_NEWS
from keyboards.industry.callbacks import SelectNewsPeriod, GetNewsDaysCount
from keyboards.industry.constructors import get_industry_kb, get_select_period_kb
from utils.bot.base import user_in_whitelist, bot_send_msg
from utils.bot.industry import get_msg_text_for_tg_newsletter

from utils.db_api.industry import get_industry_name, get_industries_with_tg_channels, get_industry_tg_news

# logger = logging.getLogger(__name__)
router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message for admin commands use chat action 'typing'


async def list_industries(message: Union[types.CallbackQuery, types.Message]) -> None:
    msg_text = 'Выберите отрасль для получения краткой сводки новостей из telegram каналов по ней'
    industry_df = get_industries_with_tg_channels()
    keyboard = get_industry_kb(industry_df)

    # Проверяем, что за тип апдейта. Если Message - отправляем новое сообщение
    if isinstance(message, types.Message):
        await message.answer(msg_text, reply_markup=keyboard)

    # Если CallbackQuery - изменяем это сообщение
    else:
        call = message
        await call.message.edit_text(msg_text, reply_markup=keyboard)


@router.message(Command('industry_tgnews'))
async def select_industry_to_get_tg_articles(message: types.Message) -> None:
    """
    Получение списка отраслей для получения по ним сводки новостей из тг-каналов

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        await list_industries(message)
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


@router.callback_query(F.data.startswith(BACK_TO_MENU))
async def back_to_menu(callback_query: types.CallbackQuery) -> None:
    chat_id = callback_query.message.chat.id
    user_msg = BACK_TO_MENU
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    await list_industries(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(SelectNewsPeriod.filter())
async def select_news_period(callback_query: types.CallbackQuery, callback_data: SelectNewsPeriod) -> None:
    """
    Изменяет сообщение, предлагая пользователю выбрать период, за который он хочет получить сводку новостей

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Выбранная отрасль и способ получения новостей (по подпискам или по всем каналам)
    """
    chat_id = callback_query.message.chat.id
    user_msg = SELECTED_INDUSTRY_TOKEN
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    industry_id = callback_data.industry_id
    my_subs = callback_data.my_subscriptions
    industry_name = get_industry_name(industry_id)

    msg_text = (
        f'Выберите период, за который хотите получить сводку новостей из telegram каналов по отрасли '
        f'<b>{industry_name.capitalize()}</b>\n\n'
        f'Для получения новостей из telegram каналов, на которые вы подписались в боте, выберите '
        f'<b>"{MY_TG_CHANNELS_CALLBACK_TEXT}"</b>\n'
        f'Для получения новостей из всех telegram каналов, связанных с отраслью, выберите '
        f'<b>"{ALL_TG_CHANNELS_CALLBACK_TEXT}"</b>'
    )
    keyboard = get_select_period_kb(industry_id, my_subs)

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}" : Выбрал отрасль с id {industry_id}')


@router.callback_query(GetNewsDaysCount.filter())
async def get_industry_summary_tg_news(callback_query: types.CallbackQuery, callback_data: GetNewsDaysCount) -> None:
    """
    Отправка пользователю сводки новостей по отрасли за указанный период

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Выбранная отрасль, кол-во дней, за которые пользователь хочет получить сводку, способ получения новостей
    """
    chat_id = callback_query.message.chat.id
    user_msg = GET_INDUSTRY_TG_NEWS
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    user_id = callback_query.from_user.id
    industry_id = callback_data.industry_id
    days = callback_data.days_count
    by_my_subs = callback_data.my_subscriptions

    news = get_industry_tg_news(industry_id, by_my_subs, user_id, timedelta(days=days))
    msg_text = await get_msg_text_for_tg_newsletter(industry_id, news, callback_data.my_subscriptions)

    await bot_send_msg(callback_query.message.bot, user_id, msg_text)
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}" : получил новости по отрасли с id {industry_id} за {days} дней')
