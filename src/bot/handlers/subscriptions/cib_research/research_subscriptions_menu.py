from typing import Union

from aiogram import F, types
from aiogram.filters import Command

from constants import subscriptions as callback_prefixes
from constants.constants import DELETE_CROSS, UNSELECTED, SELECTED
from db import subscriptions as subscriptions_db_api
from handlers.subscriptions.handler import router
from keyboards.subscriptions.research import callbacks
from keyboards.subscriptions.research import constructors as kb_maker
from log.bot_logger import user_logger
from utils.base import user_in_whitelist, get_page_data_and_info, send_or_edit


@router.callback_query(callbacks.GetUserCIBResearchSubs.filter())
async def get_my_research_subscriptions(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetUserCIBResearchSubs,
) -> None:
    """
    Изменяет сообщение, отображая информацию о подписках на отчеты CIB Research пользователя

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Содержит информацию о текущей странице, id удаляемой подписки (0 - не удаляем)
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
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


async def show_cib_research_type_more_info(
        callback_query: types.CallbackQuery, research_id: int, is_subscribed: bool, back: str, user_msg: str
) -> None:
    """Формирует сообщение с доп инфо по отчету"""
    chat_id = callback_query.message.chat.id
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    research_info = subscriptions_db_api.get_research_type_info(research_id)

    msg_text = (
        f'Название отчета: <b>{research_info["name"]}</b>\n'
        f'Описание: {research_info["description"]}\n'
    )
    keyboard = kb_maker.get_research_type_info_kb(research_id, is_subscribed, back)

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
    research_id = callback_data.research_id
    need_add = callback_data.need_add
    user_id = callback_query.from_user.id
    user_msg = callback_data.model_dump_json()

    if need_add:
        # add sub
        subscriptions_db_api.add_user_research_subscription(user_id, research_id)
    else:
        # delete sub
        subscriptions_db_api.delete_user_research_subscription(user_id, research_id)

    await show_cib_research_type_more_info(
        callback_query,
        research_id,
        need_add,
        callback_data.back,
        user_msg,
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
    user_msg = callback_data.model_dump_json()
    await show_cib_research_type_more_info(
        callback_query,
        callback_data.research_id,
        callback_data.is_subscribed,
        callback_data.back,
        user_msg,
    )


@router.callback_query(callbacks.GetCIBSectionResearches.filter())
async def get_cib_section_research_types_menu(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBSectionResearches,
) -> None:
    """
    Предоставляет подборку отчетов по разделу CIB Research

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Хранит атрибут с group_id
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    user_id = callback_query.from_user.id
    group_id = callback_data.group_id
    section_id = callback_data.section_id

    research_id = callback_data.research_id
    need_add = callback_data.need_add

    if research_id:
        if need_add:
            # add sub
            subscriptions_db_api.add_user_research_subscription(user_id, research_id)
        else:
            # delete sub on research CIB
            subscriptions_db_api.delete_user_research_subscription(user_id, research_id)

    section_info = subscriptions_db_api.get_cib_section_info(section_id)
    research_type_df = subscriptions_db_api.get_cib_research_types_by_section_df(section_id, user_id)
    msg_text = (
        f'Подборка отчетов по разделу "{section_info["name"]}"\n\n'
        f'Для добавления/удаления подписки на отчет нажмите на {UNSELECTED}/{SELECTED} соответственно'
    )

    keyboard = kb_maker.get_research_types_by_section_menu_kb(group_id, section_id, research_type_df)
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


async def make_cib_group_sections_menu(callback_query: types.CallbackQuery, group_id: int, user_id: int) -> None:
    """Формирует сообщение с подборкой отчетов по разделу"""
    group_info = subscriptions_db_api.get_cib_group_info(group_id)
    section_df = subscriptions_db_api.get_cib_sections_by_group_df(group_id, user_id)
    msg_text = f'Выберите разделы, на которые вы хотите подписаться.\n\n'

    if not section_df[~section_df['dropdown_flag']].empty:
        msg_text += f'Для добавления/удаления подписки на раздел нажмите на {UNSELECTED}/{SELECTED} соответственно'

    keyboard = kb_maker.get_research_sections_by_group_menu_kb(group_info, section_df)
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)


@router.callback_query(callbacks.GetCIBGroupSections.filter())
async def get_cib_group_sections_menu(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBGroupSections,
) -> None:
    """
    Предоставляет подборку разделов по группе CIB Research

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Хранит атрибут с group_id
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    user_id = callback_query.from_user.id
    group_id = callback_data.group_id

    section_id = callback_data.section_id
    need_add = callback_data.need_add

    if section_id:
        if need_add:
            # add sub
            subscriptions_db_api.add_user_cib_section_subscription(user_id, section_id)
        else:
            # delete sub
            subscriptions_db_api.delete_user_cib_section_subscription(user_id, section_id)

    await make_cib_group_sections_menu(callback_query, group_id, user_id)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.GetCIBGroups.filter())
async def get_research_groups_menu(callback_query: types.CallbackQuery) -> None:
    """
    Отображает список групп, выделенных среди разделов CIB Research

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = callbacks.GetCIBGroups.__prefix__
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    group_df = subscriptions_db_api.get_research_groups_df()  # id, name
    msg_text = 'Изменить подписки'
    keyboard = kb_maker.get_research_groups_menu_kb(group_df)
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
    msg_text = 'Подписки на аналитические отчеты'
    await send_or_edit(message, msg_text, keyboard)


@router.callback_query(F.data.startswith(callback_prefixes.GET_CIB_RESEARCH_SUBS_MENU))
async def back_cib_subs_menu(callback_query: types.CallbackQuery) -> None:
    """
    Фозвращает пользователя в меню (меняет сообщение, с которым связан колбэк)

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_prefixes.GET_CIB_RESEARCH_SUBS_MENU
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    await cib_research_subs_menu(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.message(Command(callback_prefixes.GET_CIB_RESEARCH_SUBS_MENU))
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
