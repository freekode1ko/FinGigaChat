"""
Обработчик для меню аналитики публичный рынков.

Позволяет выгрузить отчеты по разделам и клиентам с CIB Research,
а также макроэкономические показатели, прогноз валютных курсов и прогноз по ключевой ставке
"""
import datetime
import logging
import re
import textwrap
from typing import Optional, Type

import numpy as np
import pandas as pd
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from sqlalchemy import orm
from sqlalchemy.ext.asyncio import AsyncSession

from configs import config
from constants import enums
from constants.analytics import analytics_sell_side
from constants.texts import texts_manager
from db import database
from db.api import client as client_db_api
from db.api.client import client_db
from db.api.research import research_db
from db.api.research_group import research_group_db
from db.api.research_section import research_section_db
from db.api.research_type import research_type_db
from db.api.user_research_subscription import user_research_subscription_db
from db.user import get_user
from handlers.analytics.handler import router
from keyboards.analytics.analytics_sell_side import callbacks, constructors as keyboards
from log.bot_logger import user_logger
from module import data_transformer as dt
from module.article_process import ArticleProcess
from utils import weekly_pulse
from utils.base import __sent_photo_and_msg, send_full_copy_of_message
from utils.handler_utils import get_client_financial_indicators
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

    group_df = await research_group_db.get_all()
    section_group_id = int(group_df[group_df['name'] == 'Разделы'].loc[0, 'id'])
    group_df = group_df[group_df['name'] != 'Разделы']

    section_df = await research_section_db.get_research_sections_df_by_group_id(section_group_id, from_user.id)

    section_df['callback_data'] = section_df['id'].apply(lambda x: callbacks.GetCIBSectionResearches(section_id=x).pack())
    group_df['callback_data'] = group_df['id'].apply(lambda x: callbacks.GetCIBGroupSections(group_id=x).pack())

    keyboard = keyboards.get_menu_kb(pd.concat([section_df, group_df]))
    await callback_query.message.edit_text(texts_manager.ANAL_CHOOSE_PUBLIC_MARKET, reply_markup=keyboard)
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

    section_df = await research_section_db.get_research_sections_df_by_group_id(group_id, user_id)
    keyboard = keyboards.get_sections_by_group_menu_kb(section_df)

    await callback_query.message.edit_text(texts_manager.ANAL_CHOOSE_INDUSTRY, reply_markup=keyboard)
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

    group_df = await research_group_db.get_all()
    section_group_id = int(group_df[group_df['name'] == 'Разделы'].loc[0, 'id'])

    section_info = await research_section_db.get(section_id)
    research_type_df = await user_research_subscription_db.get_subject_df_by_section_id(user_id, section_id)

    back_callback_data = (
        callbacks.GetCIBGroupSections(group_id=section_info.research_group_id).pack()
        if section_info.research_group_id != section_group_id else callbacks.Menu().pack()
    )
    keyboard = keyboards.get_research_types_by_section_menu_kb(section_info, research_type_df, back_callback_data)

    await callback_query.message.edit_text(
        texts_manager.ANAL_SHOW_PUBLIC_MARKET.format(section=section_info.name),
        reply_markup=keyboard
    )
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.GetCIBResearchData.filter())
async def get_cib_research_data(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBResearchData,
        logger: logging.Logger,
        session: AsyncSession,
) -> None:
    """
    Изменяет сообщение, предлагая пользователю выбрать период, за который он хочет получить сводку новостей

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:   Выбранный тип отчета и способ получения новостей (по подпискам или по всем каналам)
    :param logger:          логгер
    :param session:         Асинхронная сессия базы данных.
    """
    summary_type = callback_data.summary_type

    match summary_type:
        case enums.ResearchSummaryType.periodic.value:
            await select_period_to_get_researches(callback_query, callback_data)
        case enums.ResearchSummaryType.last_actual.value:
            await get_last_actual_research(callback_query, callback_data, session)
        case enums.ResearchSummaryType.analytical_indicators.value:
            await cib_client_analytical_indicators(callback_query, callback_data, logger)
        case enums.ResearchSummaryType.exc_rate_prediction_table.value:
            await exc_rate_weekly_pulse_table(callback_query, callback_data)
        case enums.ResearchSummaryType.key_rate_dynamics_table.value:
            await key_rate_weekly_pulse_table(callback_query, callback_data)
        case enums.ResearchSummaryType.data_mart.value:
            await data_mart_callback(callback_query, callback_data)
        case enums.ResearchSummaryType.economy_daily.value:
            await economy_daily_callback(callback_query, callback_data)
        case enums.ResearchSummaryType.economy_monthly.value:
            await economy_monthly_callback(callback_query, callback_data, session)
        case _:
            pass


async def select_period_to_get_researches(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBResearchData | callbacks.SelectClientResearchesGettingPeriod,
        callback_factory: Optional[Type[CallbackData]] = callbacks.GetResearchesOverDays,
        back_callback: Optional[str] = None,
) -> None:
    """
    Меню выбора периода, за который выгружаются отчеты

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Выбранный тип отчета и способ получения новостей (по подпискам или по всем каналам)
    :param callback_factory: Фабрика создания callback_data для выгрузки отчетов за период
    :param back_callback: callback_data для кнопки Назад
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    research_type_id = callback_data.research_type_id
    research_info = await research_type_db.get(research_type_id)

    back_callback = (
        back_callback or callbacks.GetCIBSectionResearches(section_id=research_info.research_section_id).pack()
    )

    keyboard = keyboards.get_select_period_kb(
        research_type_id,
        callback_factory,
        back_callback,
    )

    await callback_query.message.edit_text(
        texts_manager.ANAL_CHOOSE_PERIOD.format(research=research_info.name),
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}"')


async def get_last_actual_research(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBResearchData,
        session: AsyncSession,
) -> None:
    """
    Получение последнего актуального отчета

    Отправляет копию меню в конце, если были отправлены отчеты

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:   Выбранный тип отчета и способ получения новостей (по подпискам или по всем каналам)
    :param session:         Асинхронная сессия базы данных.
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    research_type_id = callback_data.research_type_id

    research_df = await research_db.get_researches_by_type(research_type_id)
    if not research_df.empty:
        user = await get_user(session, from_user.id)
        last_research = research_df[research_df['publication_date'] == max(research_df['publication_date'])]
        await send_researches_to_user(callback_query.bot, user, last_research)
        await send_full_copy_of_message(callback_query)
    else:
        await callback_query.message.answer(texts_manager.ANAL_NOT_REPORT)
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}"')


async def cib_client_analytical_indicators(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBResearchData,
        logger: logging.Logger,
) -> None:
    """
    Меню аналитических показателей по клиенту

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:   Выбранный тип отчета и способ получения новостей (по подпискам или по всем каналам)
    :param logger:          логгер
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    research_type_id = callback_data.research_type_id

    research_info = await research_type_db.get(research_type_id)

    client_id = 0
    # Ищем клиента по имени отчета
    try:
        client = await client_db.get_by_name(research_info.name)
    except orm.exc.NoResultFound:
        logger.warning(f'Не удалось найти клиента {research_info.name} ({research_type_id}) в таблице clients')
    else:
        # Проверяем, что есть фин показатели для клиента
        ap_obj = ArticleProcess(logger)
        client_fin_tables = await ap_obj.get_client_fin_indicators(client['id'])
        client_id = 0 if client_fin_tables.empty else client['id']

    keyboard = keyboards.client_analytical_indicators_kb(research_info, client_id)

    await callback_query.message.edit_text(
        texts_manager.ANAL_WHAT_DATA.format(research=research_info.name),
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}"')


async def exc_rate_weekly_pulse_table(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBResearchData,
) -> None:
    """
    Получение курса валют (слайд из викли пульс)

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Выбранный тип отчета и способ получения новостей (по подпискам или по всем каналам)
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    await weekly_pulse.exc_rate_prediction_table(callback_query.bot, chat_id)
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}"')


async def key_rate_weekly_pulse_table(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBResearchData,
) -> None:
    """
    Получение ключевой ставки (слайд из викли пульс)

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Выбранный тип отчета и способ получения новостей (по подпискам или по всем каналам)
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    await weekly_pulse.key_rate_dynamics_table(callback_query.bot, chat_id)
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}"')


async def data_mart_body(message: types.Message) -> None:
    """
    Отправка витрины данных

    :param message: Объект, содержащий инфу о пользователе, чате, сообщении
    """
    transformer = dt.Transformer()
    key_eco_table = pd.read_sql_query('SELECT * FROM key_eco', con=database.engine)
    split_numbers = key_eco_table.groupby('alias')['id'].max().reset_index().sort_values('id', ascending=True)
    key_eco_table = key_eco_table.rename(columns=({'name': 'Экономические показатели'}))

    spld_keys_eco = np.split(key_eco_table, split_numbers['id'])
    title = '<b>Динамика и прогноз основных макроэкономических показателей</b>'
    await message.answer(text=title, parse_mode='HTML', protect_content=texts_manager.PROTECT_CONTENT)

    for table in spld_keys_eco:
        table.reset_index(drop=True, inplace=True)
    spld_keys_eco = [table for table in spld_keys_eco if not table.empty]

    groups = {
        'Национальные счета': 1,
        'Бюджет': 1,
        'Внешний долг': 1,
        'ИПЦ': 2,
        'ИЦП': 2,
        'Денежное предложение': 3,
        'Средняя процентная ставка': 3,
        'Социальный сектор': 4,
        'Норма сбережений': 4,
        'Платежный баланс': 5,
        'Обменный курс': 6,
    }
    groups_dict = {group: [] for group in range(1, 7)}

    for table in spld_keys_eco:
        table_group = None
        for condition, group in groups.items():
            if condition in table['alias'].iloc[0]:
                table_group = group
                break
        if table_group:
            groups_dict[table_group].append(table)

    tables = [pd.concat([df for df in groups_dict[group]]) for group in groups_dict.keys()]
    # Денежное предложение
    for table in tables:
        table.loc[table['alias'].str.contains('Денежное предложение'), 'Экономические показатели'] = (
            'Денежное предложение ' +
            table.loc[table['alias'].str.contains('Денежное предложение'), 'Экономические показатели'].str.lower()
        )
    # Средняя процентная ставка
    for table in tables:
        condition = table['alias'].str.contains('Средняя процентная ставка')
        values_to_update = table.loc[condition, 'Экономические показатели']
        values_to_update = values_to_update.apply(lambda x: '\n'.join(textwrap.wrap(x, width=30)))
        updated_values = 'Средняя ставка ' + values_to_update.str.lower()
        table.loc[condition, 'Экономические показатели'] = updated_values

    # рубль/доллар
    for table in tables:
        table.loc[table['alias'].str.contains('рубль/доллар'), 'Экономические показатели'] = (
            table.loc[table['alias'].str.contains('рубль/доллар'), 'Экономические показатели'] + ', $/руб'
        )
    # ИПЦ
    for table in tables:
        table.loc[table['alias'].str.contains('ИПЦ'), 'Экономические показатели'] = (
            table.loc[table['alias'].str.contains('ИПЦ'), 'Экономические показатели'] + ', ИПЦ'
        )
    # ИЦП
    for table in tables:
        table.loc[table['alias'].str.contains('ИЦП'), 'Экономические показатели'] = (
            table.loc[table['alias'].str.contains('ИЦП'), 'Экономические показатели'] + ', ИЦП'
        )
    # Юралз
    for table in tables:
        condition = table['alias'].str.contains('рубль/евро') & ~table['Экономические показатели'].str.contains('Юралз')
        table.loc[condition, 'Экономические показатели'] = table.loc[condition, 'Экономические показатели'] + ', €/руб'

    titles = []
    for key_eco in tables:
        title = key_eco['alias'].unique()
        title = ', '.join(title)
        if 'рубль/доллар' in title:
            title = 'Курсы валют и нефть Urals'
        titles.append(title)

    for i, key_eco in enumerate(tables):
        if not key_eco.empty:
            key_eco.reset_index(inplace=True, drop=True)
            key_eco = key_eco.drop(['id', 'alias'], axis=1)

            cols_to_keep = [col for col in key_eco.columns if re.match(r'\d{4}', col) and col != 'alias'][-4:]
            cols_to_keep.insert(0, 'Экономические показатели')
            key_eco = key_eco.loc[:, cols_to_keep]

            transformer.render_mpl_table(key_eco, 'key_eco', header_columns=0, col_width=4, alias=titles[i], font_size=16)
            png_path = config.PATH_TO_SOURCES / 'img' / 'key_eco_table.png'

            photo = types.FSInputFile(png_path)
            await __sent_photo_and_msg(message, photo, title='')


async def data_mart_callback(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBResearchData,
) -> None:
    """
    Получение витрины данных

    Отправляет копию меню в конце, если были отправлены данные

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Выбранный тип отчета и способ получения новостей (по подпискам или по всем каналам)
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    await data_mart_body(callback_query.message)
    await send_full_copy_of_message(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}"')


async def economy_monthly_callback(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBResearchData,
        session: AsyncSession,
) -> None:
    """
    Получение последнего актуального ежемесячного отчета по Экономике РФ

    Отправляет копию меню в конце, если были отправлены отчеты

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:   Выбранный тип отчета и способ получения новостей (по подпискам или по всем каналам)
    :param session:         Асинхронная сессия базы данных.
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    research_type_id = callback_data.research_type_id

    research_df = await research_db.get_researches_by_type(research_type_id)
    last_research = pd.DataFrame()
    if not research_df.empty:
        research_df = research_df[
            research_df['header'].str.contains(analytics_sell_side.ECONOMY_MONTHLY_HEADER_CONTAINS, case=False)
        ]
        last_research = research_df[research_df['publication_date'] == max(research_df['publication_date'])]

    if not last_research.empty:
        user = await get_user(session, from_user.id)
        await send_researches_to_user(callback_query.bot, user, last_research)
        await send_full_copy_of_message(callback_query)
    else:
        await callback_query.message.answer(texts_manager.ANAL_NOT_REPORT)
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}"')


async def economy_daily_callback(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBResearchData,
) -> None:
    """
    Меню выбора периода для выгрузки ежедневных отчетов по Экономике РФ

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Выбранный тип отчета и способ получения новостей (по подпискам или по всем каналам)
    """
    await select_period_to_get_researches(callback_query, callback_data, callbacks.GetEconomyDailyResearchesOverDays)


@router.callback_query(callbacks.GetResearchesOverDays.filter())
async def get_researches_over_period(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetResearchesOverDays,
        session: AsyncSession,
        header_not_contains: Optional[str] = '',
) -> None:
    """
    Отправка пользователю сводки отчетов по отрасли за указанный период

    Отправляет копию меню в конце, если были отправлены отчеты

    :param callback_query:      Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:       Выбранный тип отчета, кол-во дней, за которые пользователь хочет получить сводку
    :param session:             Асинхронная сессия базы данных.
    :param header_not_contains: фильтрация полученных отчетов по header
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    research_type_id = callback_data.research_type_id
    days = callback_data.days_count

    to_date = datetime.date.today()
    from_date = to_date - datetime.timedelta(days=days)

    researches_df = await research_db.get_researches_over_period(from_date, to_date, [research_type_id])
    if header_not_contains:
        researches_df = researches_df[~researches_df['header'].str.contains(header_not_contains, case=False)]

    if not researches_df.empty:
        user = await get_user(session, from_user.id)
        await send_researches_to_user(callback_query.bot, user, researches_df)
        await send_full_copy_of_message(callback_query)
    else:
        await callback_query.message.answer(texts_manager.ANAL_NOT_REPORT)

    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}" : получил отчеты с {research_type_id=:} за {days} дней')


@router.callback_query(callbacks.GetEconomyDailyResearchesOverDays.filter())
async def get_economy_daily_researches_over_period(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetResearchesOverDays,
        session: AsyncSession,
) -> None:
    """
    Отправка пользователю сводки ежедневных отчетов по экономике РФ за указанный период

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:   Выбранный тип отчета, кол-во дней, за которые пользователь хочет получить сводку
    :param session:         Асинхронная сессия базы данных.
    """
    await get_researches_over_period(
        callback_query,
        callback_data,
        session=session,
        header_not_contains=analytics_sell_side.ECONOMY_MONTHLY_HEADER_CONTAINS,
    )


@router.callback_query(callbacks.GetINavigatorSource.filter())
async def get_client_inavigator_source(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetINavigatorSource,
) -> None:
    """
    Отправка пользователю сводки ежедневных отчетов по экономике РФ за указанный период

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Выбранный тип отчета
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    research_type_id = callback_data.research_type_id

    research_info = await research_type_db.get(research_type_id)
    navi_link = client_db_api.get_client_navi_link_by_name(research_info.name)

    if navi_link:
        msg_text = texts_manager.ANAL_NAVI_LINK.format(link=navi_link, research=research_info.name)
    else:
        msg_text = texts_manager.ANAL_NOT_NAVI_LINK.format(research=research_info.name)

    await callback_query.message.answer(msg_text, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}"')


@router.callback_query(callbacks.SelectClientResearchesGettingPeriod.filter())
async def select_client_period(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.SelectClientResearchesGettingPeriod,
) -> None:
    """
    Отправка пользователю сводки ежедневных отчетов по экономике РФ за указанный период

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Выбранный тип отчета и способ получения новостей
    """
    await select_period_to_get_researches(
        callback_query,
        callback_data,
        back_callback=callbacks.GetCIBResearchData(
            research_type_id=callback_data.research_type_id,
            summary_type=callback_data.summary_type,
        ).pack(),
    )


@router.callback_query(callbacks.GetFinancialIndicators.filter())
async def get_financial_indicators(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetFinancialIndicators,
) -> None:
    """
    Отправка пользователю фин показателей по клиенту

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:   Выбранный тип фин показателей и клиент
    """
    await get_client_financial_indicators(callback_query, callback_data.client_id, callback_data.fin_indicator_type)


@router.callback_query(callbacks.NotImplementedFunctionality.filter())
async def not_implemented_functionality(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.NotImplementedFunctionality,
) -> None:
    """
    Сообщение, что функционал не реализован

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Выбранный тип отчета
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    await callback_query.message.answer(texts_manager.COMMON_FEATURE_WILL_APPEAR.strip(), parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}"')
