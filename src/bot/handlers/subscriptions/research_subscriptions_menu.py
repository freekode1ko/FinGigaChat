from typing import Union

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionMiddleware

from log.bot_logger import user_logger
from constants import subscriptions as callback_prefixes
from constants.constants import DELETE_CROSS, UNSELECTED, SELECTED
from keyboards.subscriptions.research import callbacks
from keyboards.subscriptions.research import constructors as kb_maker
from utils.base import user_in_whitelist, get_page_data_and_info, send_or_edit
from db import subscriptions as subscriptions_db_api


router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message for admin commands use chat action 'typing'


@router.callback_query(callbacks.GetUserCIBResearchSubs.filter())
async def get_my_tg_subscriptions(callback_query: types.CallbackQuery, callback_data: callbacks.GetUserCIBResearchSubs) -> None:
    """
    Изменяет сообщение, отображая информацию о подписках на тг каналы пользователя

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Содержит информацию о текущей странице, id удаляемой подписки (0 - не удаляем)
    """
    chat_id = callback_query.message.chat.id
    user_msg = callbacks.GetUserCIBResearchSubs.__prefix__
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    user_id = callback_query.from_user.id
    page = callback_data.page
    del_sub_id = callback_data.del_sub_id

    if del_sub_id:
        subscriptions_db_api.delete_user_research_subscription(user_id, del_sub_id)

    user_tg_subs_df = subscriptions_db_api.get_user_research_subscriptions_df(user_id)
    page_data, page_info, max_pages = get_page_data_and_info(user_tg_subs_df, page)
    msg_text = (
        f'Ваш список подписок\n<b>{page_info}</b>\n'
        f'Для получения более детальной информации об отчете - нажмите на него\n\n'
        f'Для удаления подписки - нажмите на "{DELETE_CROSS}"'
    )
    keyboard = kb_maker.get_user_research_subs_kb(page_data, page, max_pages)

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


async def show_tg_channel_more_info(
        callback_query: types.CallbackQuery, cib_type_id: int, is_subscribed: bool, back: str, user_msg: str
) -> None:
    """Формирует сообщение с доп инфо по отчету"""
    chat_id = callback_query.message.chat.id
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    research_info = subscriptions_db_api.get_research_info(cib_type_id)

    msg_text = (
        f'Раздел: <b>{research_info["domain_name"]}</b>\n'
        f'Название отчета: <b>{research_info["name"]}</b>\n'
        f'Ссылка: {research_info["description"]}\n'
    )
    keyboard = kb_maker.get_research_type_info_kb(cib_type_id, is_subscribed, back)

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.CIBResearchSubAction.filter())
async def update_sub_on_research(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.CIBResearchSubAction,
) -> None:
    """
    Предоставляет инфу об отчете

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Хранит атрибут с telegram_id
    """
    cib_type_id = callback_data.cib_type_id
    need_add = callback_data.need_add
    user_id = callback_query.from_user.id

    if need_add:
        # add sub
        subscriptions_db_api.add_user_research_subscription(user_id, cib_type_id)
    else:
        # delete sub on tg channel
        subscriptions_db_api.delete_user_research_subscription(user_id, cib_type_id)

    await show_tg_channel_more_info(
        callback_query,
        cib_type_id,
        need_add,
        callback_data.back,
        callbacks.CIBResearchSubAction.__prefix__,
    )


@router.callback_query(callbacks.GetCIBResearchTypeMoreInfo.filter())
async def get_research_more_info(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBResearchTypeMoreInfo,
) -> None:
    """
    Предоставляет инфу об отчете

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Хранит атрибут с telegram_id
    """
    await show_tg_channel_more_info(
        callback_query,
        callback_data.cib_type_id,
        callback_data.is_subscribed,
        callback_data.back,
        callbacks.GetCIBResearchTypeMoreInfo.__prefix__,
    )


async def make_domain_research_types_menu(callback_query: types.CallbackQuery, domain_id: int, user_id: int) -> None:
    """Формирует сообщен с подборкой отчетов по разделу"""
    domain_name = subscriptions_db_api.get_domain_name(domain_id)
    research_types_df = subscriptions_db_api.get_research_types_by_domain_df(domain_id, user_id)
    msg_text = (
        f'Подборка отчетов по разделу "{domain_name}"\n\n'
        f'Для добавления/удаления подписки на отчет нажмите на {UNSELECTED}/{SELECTED} соответственно\n\n'
        f'Для получения более детальной информации об отчете - нажмите на него'
    )
    keyboard = kb_maker.get_research_types_by_domain_kb(domain_id, research_types_df)
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)


@router.callback_query(callbacks.GetCIBDomainResearchTypes.filter())
async def get_domain_research_types_menu(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBDomainResearchTypes,
) -> None:
    """
    Предоставляет подборку отчетов по разделу

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Хранит атрибут с domain_id
    """
    chat_id = callback_query.message.chat.id
    user_msg = callbacks.GetCIBDomainResearchTypes.__prefix__
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    user_id = callback_query.from_user.id
    domain_id = callback_data.domain_id

    cib_type_id = callback_data.cib_type_id
    need_add = callback_data.need_add

    if cib_type_id:
        if need_add:
            # add sub
            subscriptions_db_api.add_user_research_subscription(user_id, cib_type_id)
        else:
            # delete sub on tg channel
            subscriptions_db_api.delete_user_research_subscription(user_id, cib_type_id)

    await make_domain_research_types_menu(callback_query, domain_id, user_id)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.UpdateSubOnCIBDomain.filter())
async def update_sub_on_domain(callback_query: types.CallbackQuery, callback_data: callbacks.UpdateSubOnCIBDomain) -> None:
    """
    Подписка на раздел или на все разделы
    Отрисовка страницы с разделами или страницы с отчетами для раздела
    """
    pass


@router.callback_query(callbacks.GetCIBDomains.filter())
async def get_research_domains_menu(callback_query: types.CallbackQuery) -> None:
    """
    Отображает список разделов

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = callbacks.GetCIBDomains.__prefix__
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    domain_df = subscriptions_db_api.get_research_domains_df()
    msg_text = 'Список разделов'
    keyboard = kb_maker.get_research_domains_menu_kb(domain_df)
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(F.data.startswith(callback_prefixes.CIB_RESEARCH_SUBS_DELETE_ALL))
async def delete_all_research_subs(callback_query: types.CallbackQuery) -> None:
    """
    Удаляет подписки пользователя на тг каналы
    Уведомляет пользователя, что удаление всех подписок завершено

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_prefixes.CIB_RESEARCH_SUBS_DELETE_ALL
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    user_id = callback_query.from_user.id
    subscriptions_db_api.delete_all_user_research_subscriptions(user_id)

    msg_text = 'Ваши подписки были удалены'
    keyboard = kb_maker.get_back_to_research_subs_main_menu_kb()
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(F.data.startswith(callback_prefixes.CIB_RESEARCH_SUBS_APPROVE_DELETE_ALL))
async def approve_delete_all_research_subs(callback_query: types.CallbackQuery) -> None:
    """
    Подтвреждение действия

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_prefixes.CIB_RESEARCH_SUBS_APPROVE_DELETE_ALL
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    user_id = callback_query.from_user.id

    user_subs = subscriptions_db_api.get_user_research_subscriptions_df(user_id=user_id)

    if user_subs.empty:
        msg_text = 'У вас отсутствуют подписки'
        keyboard = kb_maker.get_back_to_research_subs_main_menu_kb()
    else:
        msg_text = 'Вы уверены, что хотите удалить все подписки?'
        keyboard = kb_maker.get_research_subs_approve_delete_all_kb()

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(F.data.startswith(callback_prefixes.CIB_RESEARCH_END_WRITE_SUBS))
async def research_subs_menu_end(callback_query: types.CallbackQuery) -> None:
    """
    Завершает работу с меню подписок на cib research

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    await callback_query.message.edit_text(text='Формирование подписок завершено')


async def cib_research_subs_menu(message: Union[types.CallbackQuery, types.Message]) -> None:
    keyboard = kb_maker.get_research_subscriptions_main_menu_kb()
    msg_text = (
        'Подписки на аналитические отчеты'
    )
    await send_or_edit(message, msg_text, keyboard)


@router.callback_query(F.data.startswith(callback_prefixes.BACK_TO_CIB_RESEARCH_MENU))
async def back_to_tg_subs_menu(callback_query: types.CallbackQuery) -> None:
    """
    Фозвращает пользователя в меню (меняет сообщение, с которым связан колбэк)

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_prefixes.BACK_TO_CIB_RESEARCH_MENU
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    await cib_research_subs_menu(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.message(Command(callback_prefixes.GET_RESEARCH_SUBS_MENU))
async def cib_research_subscriptions_menu(message: types.Message) -> None:
    """
    Получение меню для взаимодействия с подписками на cib_research

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        await cib_research_subs_menu(message)
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')
