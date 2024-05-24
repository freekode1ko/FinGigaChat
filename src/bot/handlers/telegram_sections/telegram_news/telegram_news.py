"""
Обработчик тг бота для меню
Сводка новостей из telegram каналов по отраслям
"""
from datetime import timedelta

from aiogram import F, types
from aiogram.filters import Command

from constants.industry import SELECTED_INDUSTRY_TOKEN, MY_TG_CHANNELS_CALLBACK_TEXT, ALL_TG_CHANNELS_CALLBACK_TEXT, \
    BACK_TO_MENU, GET_INDUSTRY_TG_NEWS
from db.api.telegram_section import telegram_section_db
from handlers.telegram_sections.handler import router
from keyboards.telegram_news import callbacks
from keyboards.telegram_news import constructors as keyboards
from log.bot_logger import user_logger
from utils.base import user_in_whitelist, bot_send_msg
from utils.telegram_news import get_msg_text_for_tg_newsletter


async def list_sections(message: types.CallbackQuery | types.Message) -> None:
    """
    Отправка пользователю меню с выбором раздела в разрезе тг каналов
    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    msg_text = 'Выберите раздел для получения краткой сводки новостей из telegram каналов'
    sections = await telegram_section_db.get_all()
    keyboard = keyboards.get_section_kb(sections)

    # Проверяем, что за тип апдейта. Если Message - отправляем новое сообщение
    if isinstance(message, types.Message):
        await message.answer(msg_text, reply_markup=keyboard)

    # Если CallbackQuery - изменяем это сообщение
    else:
        call = message
        await call.message.edit_text(msg_text, reply_markup=keyboard)


@router.message(Command('get_tg_news'))
async def select_section_to_get_tg_articles(message: types.Message) -> None:
    """
    Получение списка разделов для получения по ним сводки новостей из тг-каналов

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        await list_sections(message)
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


@router.callback_query(F.data.startswith(BACK_TO_MENU))
async def back_to_menu(callback_query: types.CallbackQuery) -> None:
    chat_id = callback_query.message.chat.id
    user_msg = BACK_TO_MENU
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    await list_sections(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.SelectNewsPeriod.filter())
async def select_news_period(callback_query: types.CallbackQuery, callback_data: callbacks.SelectNewsPeriod) -> None:
    """
    Изменяет сообщение, предлагая пользователю выбрать период, за который он хочет получить сводку новостей

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Выбранный раздел и способ получения новостей (по подпискам или по всем каналам)
    """
    chat_id = callback_query.message.chat.id
    user_msg = SELECTED_INDUSTRY_TOKEN
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    section_id = callback_data.section_id
    my_subs = callback_data.my_subscriptions
    section_info = await telegram_section_db.get(section_id)

    msg_text = (
        f'Выберите период, за который хотите получить сводку новостей из telegram каналов по разделу '
        f'<b>{section_info.name}</b>\n\n'
        f'Для получения новостей из telegram каналов, на которые вы подписались в боте, выберите '
        f'<b>"{MY_TG_CHANNELS_CALLBACK_TEXT}"</b>\n'
        f'Для получения новостей из всех telegram каналов, связанных с разделом, выберите '
        f'<b>"{ALL_TG_CHANNELS_CALLBACK_TEXT}"</b>'
    )
    keyboard = keyboards.get_select_period_kb(section_id, my_subs)

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}" : Выбрал раздел с id {section_id}')


@router.callback_query(callbacks.GetNewsDaysCount.filter())
async def get_section_summary_tg_news(callback_query: types.CallbackQuery, callback_data: callbacks.GetNewsDaysCount) -> None:
    """
    Отправка пользователю сводки новостей по разделу за указанный период

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Выбранный раздел, кол-во дней, за которые пользователь хочет получить сводку, способ получения новостей
    """
    chat_id = callback_query.message.chat.id
    user_msg = GET_INDUSTRY_TG_NEWS
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    user_id = callback_query.from_user.id
    section_id = callback_data.section_id
    days = callback_data.days_count
    by_my_subs = callback_data.my_subscriptions

    news = await telegram_section_db.get_section_tg_news(section_id, by_my_subs, user_id, timedelta(days=days))
    msg_text = await get_msg_text_for_tg_newsletter(section_id, news, callback_data.my_subscriptions)

    await bot_send_msg(callback_query.message.bot, user_id, msg_text)
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}" : получил новости по отрасли с id {section_id} за {days} дней')
