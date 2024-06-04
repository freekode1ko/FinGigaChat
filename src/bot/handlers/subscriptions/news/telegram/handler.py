from typing import Union

from aiogram import F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from constants.constants import DELETE_CROSS, SELECTED, UNSELECTED
from db import models
from db.api.telegram_channel import telegram_channel_db
from db.api.telegram_group import telegram_group_db
from db.api.telegram_section import telegram_section_db
from db.api.user_telegram_subscription import user_telegram_subscription_db
from handlers.subscriptions.handler import router, subs_menu_end
from keyboards.subscriptions.news.telegram import callbacks as callback_factory, constructors as keyboards
from log.bot_logger import user_logger
from utils.base import get_page_data_and_info, send_or_edit, user_in_whitelist


@router.callback_query(callback_factory.TelegramSubsMenuData.filter(
    F.menu == callback_factory.TelegramSubsMenusEnum.end_menu,
))
async def end_menu(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Завершает работу с меню подписок на тг каналы

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Состояние FSM
    """
    await subs_menu_end(callback_query, state)


async def tg_subs_menu(message: Union[types.CallbackQuery, types.Message]) -> None:
    groups = await telegram_group_db.get_all()
    keyboard = keyboards.get_groups_kb(groups)
    msg_text = 'Выберите подборку телеграм-каналов'
    await send_or_edit(message, msg_text, keyboard)


@router.callback_query(callback_factory.TelegramSubsMenuData.filter(
    F.menu == callback_factory.TelegramSubsMenusEnum.main_menu,
))
async def back_to_tg_subs_menu(
        callback_query: types.CallbackQuery,
        callback_data: callback_factory.TelegramSubsMenuData,
) -> None:
    """
    Возвращает пользователя в меню (меняет сообщение, с которым связан колбэк)

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Содержит информацию о текущем меню
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    await tg_subs_menu(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.message(Command(callback_factory.TelegramSubsMenuData.__prefix__))
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


@router.callback_query(callback_factory.TelegramSubsMenuData.filter(
    F.menu == callback_factory.TelegramSubsMenusEnum.group_main_menu,
))
async def group_main_menu(
        callback_query: types.CallbackQuery,
        callback_data: callback_factory.TelegramSubsMenuData,
) -> None:
    """
    Формирует меню управления подписками на тг каналы определенной группы (bot_telegram_group)

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Содержит информацию о текущем меню
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    group_id = callback_data.group_id
    telegram_group_info = await telegram_group_db.get(group_id)

    keyboard = keyboards.get_group_main_menu_kb(group_id)
    msg_text = f'Меню управления подписками на {telegram_group_info.name.lower()}\n\n'
    await send_or_edit(callback_query, msg_text, keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callback_factory.TelegramSubsMenuData.filter(
    F.menu == callback_factory.TelegramSubsMenusEnum.my_subscriptions,
))
async def my_subscriptions(
        callback_query: types.CallbackQuery,
        callback_data: callback_factory.TelegramSubsMenuData,
) -> None:
    """
    Формирует список подписок на тг каналы определенной группы (bot_telegram_group)

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Содержит информацию о текущем меню
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    user_id = callback_query.from_user.id
    group_id = callback_data.group_id
    page = callback_data.page
    telegram_id = callback_data.telegram_id

    telegram_group_info = await telegram_group_db.get(group_id)

    if telegram_id:
        await user_telegram_subscription_db.delete_subscription(user_id, telegram_id)

    user_tg_subs_df = await user_telegram_subscription_db.get_subscription_df_by_group_id(user_id, group_id)
    page_data, page_info, max_pages = get_page_data_and_info(user_tg_subs_df, page)
    msg_text = (
        f'Ваш список подписок на {telegram_group_info.name.lower()}\n'
        f'<b>{page_info}</b>\n'
        f'Для получения более детальной информации о канале - нажмите на него\n\n'
        f'Для удаления канала из подписок - нажмите на "{DELETE_CROSS}" рядом с каналом'
    )
    keyboard = keyboards.get_my_subscriptions_kb(page_data, page, max_pages, group_id=group_id)

    await send_or_edit(callback_query, msg_text, keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callback_factory.TelegramSubsMenuData.filter(
    F.menu == callback_factory.TelegramSubsMenusEnum.change_subscriptions,
))
async def change_subscriptions(
        callback_query: types.CallbackQuery,
        callback_data: callback_factory.TelegramSubsMenuData,
) -> None:
    """
    Формирует меню изменения подписок на тг каналы определенной группы (bot_telegram_group)

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Содержит информацию о текущем меню
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    group_id = callback_data.group_id
    telegram_group_info = await telegram_group_db.get(group_id)

    if telegram_group_info.is_show_all_channels:
        callback_data.back_menu = callback_factory.TelegramSubsMenusEnum.group_main_menu
        await __show_telegram_channels_by_group(callback_query, callback_data, telegram_group_info)
    else:
        await __show_telegram_sections_by_group(callback_query, callback_data, telegram_group_info)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


async def __show_telegram_channels_by_group(
        callback_query: types.CallbackQuery,
        callback_data: callback_factory.TelegramSubsMenuData,
        telegram_group_info: models.TelegramGroup,
) -> None:
    """
    Формирует список тг каналов определенной группы (bot_telegram_group)

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Содержит информацию о текущем меню
    :param telegram_group_info: Объект телеграмм группы
    """
    user_id = callback_query.from_user.id
    telegram_id = callback_data.telegram_id

    if telegram_id:
        if callback_data.is_subscribed:
            await user_telegram_subscription_db.delete_subscription(user_id, telegram_id)
        else:
            await user_telegram_subscription_db.add_subscription(user_id, telegram_id)

    telegram_channels = await user_telegram_subscription_db.get_subject_df_by_group_id(
        user_id=callback_query.from_user.id,
        group_id=telegram_group_info.id,
    )

    msg_text = (
        f'{telegram_group_info.name}\n\n'
        f'Для добавления/удаления подписки на telegram канал нажмите на {UNSELECTED}/{SELECTED} соответственно\n\n'
        f'Для получения более детальной информации о канале - нажмите на него'
    )
    keyboard = keyboards.get_change_subscriptions_kb(telegram_channels, callback_data)
    await send_or_edit(callback_query, msg_text, keyboard)


async def __show_telegram_sections_by_group(
        callback_query: types.CallbackQuery,
        callback_data: callback_factory.TelegramSubsMenuData,
        telegram_group_info: models.TelegramGroup,
) -> None:
    """
    Формирует список тг разделов определенной группы (bot_telegram_group)

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Содержит информацию о текущем меню
    :param telegram_group_info: Объект телеграмм группы
    """
    telegram_sections = await telegram_section_db.get_by_group_id(group_id=telegram_group_info.id)
    msg_text = 'Выберите подборку telegram каналов по отраслям'
    keyboard = keyboards.get_sections_menu_kb(telegram_sections, callback_data.group_id)
    await send_or_edit(callback_query, msg_text, keyboard)


@router.callback_query(callback_factory.TelegramSubsMenuData.filter(
    F.menu == callback_factory.TelegramSubsMenusEnum.telegram_channels_by_section,
))
async def telegram_channels_by_section(
        callback_query: types.CallbackQuery,
        callback_data: callback_factory.TelegramSubsMenuData,
) -> None:
    """
    Формирует список тг каналов определенного раздела (bot_telegram_section)

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Содержит информацию о текущем меню
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    user_id = callback_query.from_user.id
    telegram_id = callback_data.telegram_id

    telegram_group_info = await telegram_group_db.get(callback_data.group_id)
    telegram_section_info = await telegram_section_db.get(callback_data.section_id)

    if telegram_id:
        if callback_data.is_subscribed:
            await user_telegram_subscription_db.delete_subscription(user_id, telegram_id)
        else:
            await user_telegram_subscription_db.add_subscription(user_id, telegram_id)

    telegram_channels = await user_telegram_subscription_db.get_subject_df_by_section_id(
        user_id=callback_query.from_user.id,
        section_id=telegram_section_info.id,
    )

    callback_data.back_menu = callback_factory.TelegramSubsMenusEnum.change_subscriptions
    keyboard = keyboards.get_change_subscriptions_kb(telegram_channels, callback_data)
    msg_text = (
        f'{telegram_group_info.name} по отрасли "{telegram_section_info.name}"\n\n'
        f'Для добавления/удаления подписки на telegram канал нажмите на {UNSELECTED}/{SELECTED} соответственно\n\n'
        f'Для получения более детальной информации о канале - нажмите на него'
    )
    await send_or_edit(callback_query, msg_text, keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


async def show_tg_channel_more_info(
        callback_query: types.CallbackQuery,
        callback_data: callback_factory.TelegramSubsMenuData,
) -> None:
    """
    Отображает инфу о тг канале

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Содержит информацию о текущем меню
    """
    chat_id = callback_query.message.chat.id
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    user_msg = callback_data.pack()

    telegram_id = callback_data.telegram_id

    telegram_ch = await telegram_channel_db.get(telegram_id)

    msg_text = (
        f'Название: <b>{telegram_ch.name}</b>\n'
        f'Ссылка: {telegram_ch.link}\n'
    )
    keyboard = keyboards.get_tg_info_kb(callback_data)

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callback_factory.TelegramSubsMenuData.filter(
    F.menu == callback_factory.TelegramSubsMenusEnum.telegram_channel_info,
))
async def telegram_channel_info(
        callback_query: types.CallbackQuery,
        callback_data: callback_factory.TelegramSubsMenuData,
) -> None:
    """
    Предоставляет инфу о тг канале и делает добавление его в подписки или удаление из подписок

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Содержит информацию о текущем меню
    """
    telegram_id = callback_data.telegram_id
    need_add = callback_data.need_add
    user_id = callback_query.from_user.id

    if need_add is not None:
        if need_add:
            # add sub
            await user_telegram_subscription_db.add_subscription(user_id, telegram_id)
        else:
            # delete sub on tg channel
            await user_telegram_subscription_db.delete_subscription(user_id, telegram_id)

    await show_tg_channel_more_info(callback_query, callback_data)


@router.callback_query(callback_factory.TelegramSubsMenuData.filter(
    F.menu == callback_factory.TelegramSubsMenusEnum.delete_subscriptions_by_group,
))
async def delete_subscriptions_by_group(
        callback_query: types.CallbackQuery,
        callback_data: callback_factory.TelegramSubsMenuData,
) -> None:
    """
    Удаление подписок на все тг каналов определенной группы (bot_telegram_group)

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Содержит информацию о текущем меню
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    user_id = callback_query.from_user.id
    group_id = callback_data.group_id
    telegram_group_info = await telegram_group_db.get(group_id)

    await user_telegram_subscription_db.delete_all_by_group_id(user_id, group_id)

    msg_text = f'Ваши подписки на {telegram_group_info.name.lower()} были удалены'
    keyboard = keyboards.get_back_to_tg_subs_menu_kb(group_id)
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callback_factory.TelegramSubsMenuData.filter(
    F.menu == callback_factory.TelegramSubsMenusEnum.approve_delete_menu,
))
async def approve_delete_menu(
        callback_query: types.CallbackQuery,
        callback_data: callback_factory.TelegramSubsMenuData,
) -> None:
    """
    Меню подтверждения действия по удалению подписок на все тг каналов определенной группы (bot_telegram_group)

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Содержит информацию о текущем меню
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    user_id = callback_query.from_user.id
    group_id = callback_data.group_id
    telegram_group_info = await telegram_group_db.get(group_id)

    user_tg_subs = await user_telegram_subscription_db.get_subscription_df_by_group_id(user_id, group_id)

    if user_tg_subs.empty:
        msg_text = f'У вас отсутствуют подписки на {telegram_group_info.name.lower()}'
        keyboard = keyboards.get_back_to_tg_subs_menu_kb(group_id)
    else:
        msg_text = f'Вы уверены, что хотите удалить все подписки на {telegram_group_info.name.lower()}?'
        keyboard = keyboards.get_prepare_tg_subs_delete_all_kb(group_id)

    await send_or_edit(callback_query, msg_text, keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
