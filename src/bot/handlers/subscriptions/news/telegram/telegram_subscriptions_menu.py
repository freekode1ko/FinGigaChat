from typing import Union

from aiogram import F, types
from aiogram.filters import Command

from log.bot_logger import user_logger
from constants import subscriptions as callback_prefixes
from constants.constants import DELETE_CROSS, UNSELECTED, SELECTED
from db.industry import get_industries_with_tg_channels, get_industry_name
from db.subscriptions import (
    get_user_tg_subscriptions_df,
    delete_user_telegram_subscription,
    delete_all_user_telegram_subscriptions,
    get_industry_tg_channels_df,
    get_telegram_channel_info,
    add_user_telegram_subscription,
)
from keyboards.subscriptions.telegram import callbacks
from keyboards.subscriptions.telegram import constructors as keyboards
from handlers.subscriptions.handler import router
from utils.base import user_in_whitelist, get_page_data_and_info, send_or_edit


@router.callback_query(callbacks.UserTGSubs.filter())
async def get_my_tg_subscriptions(callback_query: types.CallbackQuery, callback_data: callbacks.UserTGSubs) -> None:
    """
    Изменяет сообщение, отображая информацию о подписках на тг каналы пользователя

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Содержит информацию о текущей странице, id удаляемой подписки (0 - не удаляем)
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_prefixes.USER_TG_SUBS
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    user_id = callback_query.from_user.id
    page = callback_data.page
    delete_tg_sub_id = callback_data.delete_tg_sub_id

    if delete_tg_sub_id:
        delete_user_telegram_subscription(user_id, delete_tg_sub_id)

    user_tg_subs_df = get_user_tg_subscriptions_df(user_id)
    page_data, page_info, max_pages = get_page_data_and_info(user_tg_subs_df, page)
    msg_text = (
        f'Ваш список подписок на telegram каналы\n<b>{page_info}</b>\n'
        f'Для получения более детальной информации о канале - нажмите на него\n\n'
        f'Для удаления канала из подписок - нажмите на "{DELETE_CROSS}" рядом с каналом'
    )
    keyboard = keyboards.get_tg_subs_watch_kb(page_data, page, max_pages)

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


async def show_tg_channel_more_info(
        callback_query: types.CallbackQuery, telegram_id: int, is_subscribed: bool, back: str, user_msg: str
) -> None:
    """"""
    chat_id = callback_query.message.chat.id
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    telegram_channel_info = get_telegram_channel_info(telegram_id)

    msg_text = (
        f'Название: <b>{telegram_channel_info["name"]}</b>\n'
        # f'Description: {}\n'
        f'Ссылка: {telegram_channel_info["link"]}\n'
        f'Отрасль: <b>{telegram_channel_info["industry_name"]}</b>\n'
    )
    keyboard = keyboards.get_tg_info_kb(telegram_id, is_subscribed, back)

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.TGSubAction.filter())
async def update_sub_on_tg_channel(callback_query: types.CallbackQuery, callback_data: callbacks.TGSubAction) -> None:
    """
    Предоставляет инфу о тг канале

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Хранит атрибут с telegram_id
    """
    telegram_id = callback_data.telegram_id
    need_add = callback_data.need_add
    user_id = callback_query.from_user.id

    if need_add:
        # add sub
        add_user_telegram_subscription(user_id, telegram_id)
    else:
        # delete sub on tg channel
        delete_user_telegram_subscription(user_id, telegram_id)

    await show_tg_channel_more_info(
        callback_query, telegram_id, need_add, callback_data.back, callback_prefixes.TG_SUB_ACTION
    )


@router.callback_query(callbacks.TGChannelMoreInfo.filter())
async def get_tg_channel_more_info(callback_query: types.CallbackQuery, callback_data: callbacks.TGChannelMoreInfo) -> None:
    """
    Предоставляет инфу о тг канале

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Хранит атрибут с telegram_id
    """
    await show_tg_channel_more_info(
        callback_query,
        callback_data.telegram_id,
        callback_data.is_subscribed,
        callback_data.back,
        callback_prefixes.TG_CHANNEL_INFO,
    )


@router.callback_query(callbacks.IndustryTGChannels.filter())
async def get_industry_tg_channels(callback_query: types.CallbackQuery, callback_data: callbacks.IndustryTGChannels) -> None:
    """
    Предоставляет подборку тг каналов по отрасли

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Хранит атрибут с industry_id
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_prefixes.INDUSTRY_TG_CHANNELS
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    user_id = callback_query.from_user.id
    industry_id = callback_data.industry_id
    telegram_id = callback_data.telegram_id
    need_add = callback_data.need_add

    if telegram_id:
        if need_add:
            add_user_telegram_subscription(user_id, telegram_id)
        else:
            delete_user_telegram_subscription(user_id, telegram_id)

    industry_name = get_industry_name(industry_id)
    tg_channel_df = get_industry_tg_channels_df(industry_id, user_id)
    msg_text = (
        f'Подборка telegram каналов по отрасли "{industry_name}"\n\n'
        f'Для добавления/удаления подписки на telegram канала нажмите на {UNSELECTED}/{SELECTED} соответственно\n\n'
        f'Для получения более детальной информации о канале - нажмите на него'
    )
    keyboard = keyboards.get_industry_tg_channels_kb(industry_id, tg_channel_df)
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(F.data.startswith(callback_prefixes.TG_SUBS_INDUSTRIES_MENU))
async def get_tg_subs_industries_menu(callback_query: types.CallbackQuery) -> None:
    """
    Отображает список отраслей, которые связаны с какими-либо telegram каналами

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_prefixes.TG_SUBS_INDUSTRIES_MENU
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    industry_df = get_industries_with_tg_channels()
    msg_text = 'Выберите подборку telegram каналов по отраслям'
    keyboard = keyboards.get_tg_subs_industries_menu_kb(industry_df)
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(F.data.startswith(callback_prefixes.TG_SUBS_DELETE_ALL_DONE))
async def delete_all_tg_subs_done(callback_query: types.CallbackQuery) -> None:
    """
    Удаляет подписки пользователя на тг каналы
    Уведомляет пользователя, что удаление всех подписок завершено

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_prefixes.TG_SUBS_DELETE_ALL_DONE
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    user_id = callback_query.from_user.id
    delete_all_user_telegram_subscriptions(user_id)

    msg_text = 'Ваши подписки на telegram каналы были удалены'
    keyboard = keyboards.get_back_to_tg_subs_menu_kb()
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(F.data.startswith(callback_prefixes.TG_SUBS_DELETE_ALL))
async def delete_all_tg_subs(callback_query: types.CallbackQuery) -> None:
    """
    Подтвреждение действия

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_prefixes.TG_SUBS_DELETE_ALL
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    user_id = callback_query.from_user.id

    user_tg_subs = get_user_tg_subscriptions_df(user_id=user_id)

    if user_tg_subs.empty:
        msg_text = 'У вас отсутствуют подписки'
        keyboard = keyboards.get_back_to_tg_subs_menu_kb()
    else:
        msg_text = 'Вы уверены, что хотите удалить все подписки на telegram каналы?'
        keyboard = keyboards.get_prepare_tg_subs_delete_all_kb()

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(F.data.startswith(callback_prefixes.TG_END_WRITE_SUBS))
async def tg_end_write_subs(callback_query: types.CallbackQuery) -> None:
    """
    Завершает работу с меню подписок на тг каналы

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    await callback_query.message.edit_text(text='Формирование подписок завершено')


async def tg_subs_menu(message: Union[types.CallbackQuery, types.Message]) -> None:
    keyboard = keyboards.get_tg_subscriptions_menu_kb()
    msg_text = (
        'Меню управления подписками на telegram каналы\n\n'
        'На основе ваших подписок формируется сводка новостей по отрасли, с которой связаны telegram каналы'
    )
    await send_or_edit(message, msg_text, keyboard)


@router.callback_query(F.data.startswith(callback_prefixes.TG_MENU))
async def back_to_tg_subs_menu(callback_query: types.CallbackQuery) -> None:
    """
    Фозвращает пользователя в меню (меняет сообщение, с которым связан колбэк)

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_prefixes.TG_MENU
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    await tg_subs_menu(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.message(Command(callback_prefixes.TG_MENU))
async def tg_subscriptions_menu(message: types.Message) -> None:
    """
    Получение меню для взаимодействия с подписками на telegram каналы (влияет на сводку новостей по отрасли)

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        await tg_subs_menu(message)
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')
