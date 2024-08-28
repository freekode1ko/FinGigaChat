"""
Обработчик действий пользователя для меню подписок на отчеты CIB Resarch.

Главное меню.
Просмотр своих подписок.
Изменение подписок.
Удаление подписок.
"""

from aiogram import F, types

from constants.constants import DELETE_CROSS, SELECTED, UNSELECTED
from constants.subscriptions import research as callback_prefixes
from db import models
from db.api.research_group import research_group_db
from db.api.research_section import research_section_db
from db.api.research_type import research_type_db
from db.api.user_client_subscription import user_client_subscription_db
from db.api.user_industry_subscription import user_industry_subscription_db
from db.api.user_research_subscription import user_research_subscription_db
from handlers.subscriptions.handler import router
from keyboards.subscriptions.research import callbacks, constructors as keyboards
from log.bot_logger import user_logger
from utils.base import get_page_data_and_info


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
        await user_research_subscription_db.delete_subscription(user_id, del_sub_id)

    user_subs = await user_research_subscription_db.get_subscription_df(user_id=user_id)
    page_data, page_info, max_pages = get_page_data_and_info(user_subs, page)
    msg_text = (
        f'Ваш список подписок\n<b>{page_info}</b>\n'
        f'Для получения более детальной информации об отчете - нажмите на него\n\n'
        f'Для удаления подписки - нажмите на "{DELETE_CROSS}"'
    )
    keyboard = keyboards.get_user_research_subs_kb(page_data, page, max_pages, action=callback_data.action)

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


async def show_cib_research_type_more_info(
        callback_query: types.CallbackQuery, research_id: int, is_subscribed: bool, back: str, user_msg: str
) -> None:
    """Формирует сообщение с доп инфо по отчету"""
    chat_id = callback_query.message.chat.id
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    research_info = await research_type_db.get(research_id)

    msg_text = (
        f'Название отчета: <b>{research_info.name}</b>\n'
        f'Описание: {research_info.description}\n'
    )
    keyboard = keyboards.get_research_type_info_kb(research_id, is_subscribed, back)

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


async def subscribe_on_news_source_with_same_name(user_id: int, research_id: int) -> None:
    """
    Подписка на клиента или отрасль, если имя отчета совпадает с именем клиента/отрасли

    :param user_id: телеграм id пользователя
    :param research_id: id отчета cib research, на который подписывается пользователь
    """
    await user_client_subscription_db.subscribe_on_news_source_with_same_name(user_id, models.ResearchType, research_id)
    await user_industry_subscription_db.subscribe_on_news_source_with_same_name(user_id, models.ResearchType, research_id)


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
        await user_research_subscription_db.add_subscription(user_id, research_id)
        await subscribe_on_news_source_with_same_name(user_id, research_id)
    else:
        # delete sub
        await user_research_subscription_db.delete_subscription(user_id, research_id)

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
            await user_research_subscription_db.add_subscription(user_id, research_id)
            await subscribe_on_news_source_with_same_name(user_id, research_id)
        else:
            # delete sub on research CIB
            await user_research_subscription_db.delete_subscription(user_id, research_id)

    section_info = await research_section_db.get(section_id)
    research_type_df = await user_research_subscription_db.get_subject_df_by_section_id(user_id, section_id)
    msg_text = (
        f'Подборка отчетов по разделу "{section_info.name}"\n\n'
        f'Для добавления/удаления подписки на отчет нажмите на {UNSELECTED}/{SELECTED} соответственно'
    )

    keyboard = keyboards.get_research_types_by_section_menu_kb(group_id, section_id, research_type_df)
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


async def make_cib_group_sections_menu(callback_query: types.CallbackQuery, group_id: int, user_id: int) -> None:
    """Формирует сообщение с подборкой отчетов по разделу"""
    group_info = await research_group_db.get(group_id)
    section_df = await research_section_db.get_research_sections_df_by_group_id(group_id, user_id)
    msg_text = 'Выберите разделы, на которые вы хотите подписаться.\n\n'

    if not section_df[~section_df['dropdown_flag']].empty:
        msg_text += f'Для добавления/удаления подписки на раздел нажмите на {UNSELECTED}/{SELECTED} соответственно'

    keyboard = keyboards.get_research_sections_by_group_menu_kb(group_info, section_df)
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
            await user_research_subscription_db.add_subscriptions_by_section_id(user_id, section_id)
        else:
            # delete sub
            await user_research_subscription_db.delete_all_by_section_id(user_id, section_id)

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

    group_df = await research_group_db.get_all()
    msg_text = (
        'Изменить подписки\n\n'
        'Выберете категорию материалов аналитики'
    )
    keyboard = keyboards.get_research_groups_menu_kb(group_df)
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
    await user_research_subscription_db.delete_all(user_id)

    msg_text = 'Ваши подписки были удалены'
    keyboard = keyboards.get_back_to_research_subs_main_menu_kb()
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

    user_subs = await user_research_subscription_db.get_subscription_df(user_id=user_id)

    if user_subs.empty:
        msg_text = 'У вас отсутствуют подписки на аналитические отчеты'
        keyboard = keyboards.get_back_to_research_subs_main_menu_kb()
    else:
        msg_text = 'Вы уверены, что хотите удалить все подписки на аналитические отчеты?'
        keyboard = keyboards.get_research_subs_approve_delete_all_kb()

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(F.data.startswith(callback_prefixes.CIB_RESEARCH_END_WRITE_SUBS))
async def research_subs_menu_end(callback_query: types.CallbackQuery) -> None:
    """
    Завершает работу с меню подписок на cib research

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    await callback_query.message.edit_text(text='Формирование подписок завершено')
