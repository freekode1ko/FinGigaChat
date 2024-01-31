# import logging
from datetime import date, timedelta
from typing import List, Dict, Union

import pandas as pd
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionMiddleware
from sqlalchemy import text

import database
from bot_logger import user_logger
from constants.bot.industry import SELECTED_INDUSTRY_TOKEN, MY_TG_CHANNELS_CALLBACK_TEXT, ALL_TG_CHANNELS_CALLBACK_TEXT, \
    BACK_TO_MENU
from keyboards.industry.callbacks import SelectNewsPeriod, GetNewsDaysCount
from keyboards.industry.constructors import get_industry_kb, get_select_period_kb
from utils.bot_utils import user_in_whitelist

# logger = logging.getLogger(__name__)
router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message for admin commands use chat action 'typing'


def get_industries() -> pd.DataFrame:
    query = 'SELECT id, name FROM industry ORDER BY name;'
    industry_df = pd.read_sql(query, con=database.engine)
    return industry_df


async def list_industries(message: Union[types.CallbackQuery, types.Message]) -> None:
    msg_text = 'Выберите отрасль для получения краткой сводки новостей из telegram каналов по ней'
    industry_df = get_industries()
    keyboard = get_industry_kb(industry_df)

    # Проверяем, что за тип апдейта. Если Message - отправляем новое сообщение
    if isinstance(message, types.Message):
        await message.answer(msg_text, reply_markup=keyboard)

    # Если CallbackQuery - изменяем это сообщение
    elif isinstance(message, types.CallbackQuery):
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
        f'<b>{industry_name.title()}</b>\n\n'
        f'Для получения новостей из telegram каналов, на которые вы подписались в боте, выберите '
        f'<b>"{MY_TG_CHANNELS_CALLBACK_TEXT}"</b>\n'
        f'Для получения новостей из всех telegram каналов, связанных с отраслью, выберите '
        f'<b>"{ALL_TG_CHANNELS_CALLBACK_TEXT}"</b>'
    )
    keyboard = get_select_period_kb(industry_id, my_subs)

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}" : Выбрал отрасль с id {industry_id}')


def get_industry_name(industry_id: int) -> str:
    with database.engine.connect() as conn:
        query = text('SELECT name FROM industry WHERE id=:industry_id')
        industry_name = conn.execute(query.bindparams(industry_id=industry_id)).scalar_one()

    return industry_name


def get_industry_tg_news(industry_id: int, my_subscriptions: bool, days: int) -> pd.DataFrame:
    # FIXME пока что выдает по всем тг каналам, позже добавлю таблицу подписок
    query = text(
        'SELECT tg.name as telegram_channel_name, a.link as telegram_article_link, a.text_sum, a.date '
        'FROM article a '
        'JOIN relation_telegram_article ra ON a.id=ra.article_id '
        'JOIN tg_channels tg ON ra.telegram_id=tg.id '
        'WHERE tg.industry_id=:industry_id AND '
        'DATE(a.date) BETWEEN :before_date AND :now_date '
        'ORDER BY a.date DESC, ra.telegram_score DESC'
    )
    now_date = date.today()
    before_date = now_date - timedelta(days=days)

    with database.engine.connect() as conn:
        data = conn.execute(query.bindparams(industry_id=industry_id, before_date=before_date, now_date=now_date)).all()
        data_df = pd.DataFrame(data, columns=['telegram_channel_name', 'telegram_article_link', 'text_sum', 'date'])

    return data_df


@router.callback_query(GetNewsDaysCount.filter())
async def get_industry_summary_tg_news(callback_query: types.CallbackQuery, callback_data: GetNewsDaysCount) -> None:
    """
    Отправка пользователю сводки новостей по отрасли за указанный период

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Выбранная отрасль, кол-во дней, за которые пользователь хочет получить сводку, способ получения новостей
    """
    chat_id = callback_query.message.chat.id
    user_msg = SELECTED_INDUSTRY_TOKEN
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    industry_id = callback_data.industry_id
    my_subs = callback_data.my_subscriptions
    days = callback_data.days_count

    industry_name = get_industry_name(industry_id)
    news = get_industry_tg_news(industry_id, my_subs, days)
    msg_text = f'Сводка новостей по <b>{"подпискам" if my_subs else "всем telegram каналам"}</b> по отрасли ' \
               f'<b>{industry_name.title()}</b>\n\n'

    if not news.empty:
        for index, article in news.iterrows():
            article = (
                f'<b>{article["telegram_channel_name"]}</b>\n'
                f'{article["text_sum"]}\n'  # FIXME слишком большой объект краткого изложения
                f'<b>Ссылка на новость</b>: {article["telegram_article_link"]}\n'
                f'<b>Дата получения новости</b>: {article["date"].strftime("%d.%m.%Y %H:%M")}\n\n'
            )

            msg_text += article

    else:
        msg_text += 'За выбранный период новых новостей не нашлось'

    await callback_query.message.answer(msg_text, parse_mode='HTML')  # FIXME MessageIsTooLong
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}" : получил новости по отрасли с id {industry_id} за {days} дней')
