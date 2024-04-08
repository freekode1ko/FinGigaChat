import datetime

from aiogram import types

from db import subscriptions as subscriptions_db_api
from handlers.analytics.handler import router
from keyboards.analytics.analytics_sell_side import callbacks, constructors as kb_maker
from log.bot_logger import user_logger
from utils.newsletter import send_researches_to_user


@router.callback_query(callbacks.Menu.filter())
async def get_research_groups_menu(callback_query: types.CallbackQuery) -> None:
    """
    Отображает список групп, выделенных среди разделов CIB Research

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = callbacks.Menu.__prefix__
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    group_df = subscriptions_db_api.get_research_groups_df()  # id, name
    msg_text = (
        'Аналитика sell-side\n'
        'Группы:'
    )
    keyboard = kb_maker.get_menu_kb(group_df)
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.GetCIBGroupSections.filter())
async def get_group_sections_menu(
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

    group_info = subscriptions_db_api.get_cib_group_info(group_id)
    section_df = subscriptions_db_api.get_cib_sections_by_group_df(group_id, user_id)

    msg_text = (
        f'Аналитика sell-side\n'
        f'Группа "{group_info["name"]}":\n'
    )
    keyboard = kb_maker.get_sections_by_group_menu_kb(section_df)

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.GetCIBSectionResearches.filter())
async def get_section_research_types_menu(
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
    section_id = callback_data.section_id

    section_info = subscriptions_db_api.get_cib_section_info(section_id)
    research_type_df = subscriptions_db_api.get_cib_research_types_by_section_df(section_id, user_id)

    msg_text = (
        f'Аналитика sell-side\n'
        f'Раздел "{section_info["name"]}":'
    )
    keyboard = kb_maker.get_research_types_by_section_menu_kb(section_info['research_group_id'], research_type_df)

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.GetCIBResearchType.filter())
async def select_period_to_get_researches(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBResearchType,
) -> None:
    """
    Изменяет сообщение, предлагая пользователю выбрать период, за который он хочет получить сводку новостей

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Выбранная отрасль и способ получения новостей (по подпискам или по всем каналам)
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    research_type_id = callback_data.research_type_id

    research_info = subscriptions_db_api.get_research_type_info(research_type_id)

    msg_text = (
        f'Выберите период, за который хотите получить отчеты по '
        f'<b>{research_info["name"]}</b>\n\n'
    )
    keyboard = kb_maker.get_select_period_kb(research_type_id, research_info['research_section_id'])

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}"')


@router.callback_query(callbacks.GetResearchesOverDays.filter())
async def get_researches_over_period(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetResearchesOverDays,
) -> None:
    """
    Отправка пользователю сводки новостей по отрасли за указанный период

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Выбранный тип отчета, кол-во дней, за которые пользователь хочет получить сводку
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    user_id = callback_query.from_user.id

    research_type_id = callback_data.research_type_id
    days = callback_data.days_count

    to_date = datetime.date.today()
    from_date = to_date - datetime.timedelta(days=days)

    researches_df = subscriptions_db_api.get_researches_over_period(from_date, to_date, [research_type_id])
    await send_researches_to_user(callback_query.bot, user_id, full_name, researches_df)

    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}" : получил отчеты с {research_type_id=:} за {days} дней')
