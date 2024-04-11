import datetime
import re
import textwrap
from typing import Optional, Type

import numpy as np
import pandas as pd
from aiogram import types
from aiogram.filters.callback_data import CallbackData

from configs import config
from constants import enums
from constants.analytics import analytics_sell_side
from db import subscriptions as subscriptions_db_api, database
from handlers.analytics.handler import router
from keyboards.analytics.analytics_sell_side import callbacks, constructors as keyboards
from log.bot_logger import user_logger
from module import data_transformer as dt
from utils import weekly_pulse
from utils.base import __sent_photo_and_msg
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
        'Группы:'  # FIXME text
    )

    section_group_id = int(group_df[group_df['name'] == 'Разделы'].loc[0, 'id'])
    group_df = group_df[group_df['name'] != 'Разделы']

    section_df = subscriptions_db_api.get_cib_sections_by_group_df(section_group_id, from_user.id)

    section_df['callback_data'] = section_df['id'].apply(lambda x: callbacks.GetCIBSectionResearches(section_id=x).pack())
    group_df['callback_data'] = group_df['id'].apply(lambda x: callbacks.GetCIBGroupSections(group_id=x).pack())

    keyboard = keyboards.get_menu_kb(pd.concat([section_df, group_df]))
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

    section_df = subscriptions_db_api.get_cib_sections_by_group_df(group_id, user_id)

    msg_text = 'Выберете отрасль клиента, по которому вы хотели бы получить данные из SberCIB Investment Research'
    keyboard = keyboards.get_sections_by_group_menu_kb(section_df)

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

    group_df = subscriptions_db_api.get_research_groups_df()  # id, name
    section_group_id = int(group_df[group_df['name'] == 'Разделы'].loc[0, 'id'])

    section_info = subscriptions_db_api.get_cib_section_info(section_id)
    research_type_df = subscriptions_db_api.get_cib_research_types_by_section_df(section_id, user_id)

    back_callback_data = (
        callbacks.GetCIBGroupSections(group_id=section_info['research_group_id']).pack()
        if section_info['research_group_id'] != section_group_id else callbacks.Menu().pack()
    )

    msg_text = (
        f'Аналитика sell-side\n'
        f'Раздел "{section_info["name"]}":'  # FIXME text
    )
    keyboard = keyboards.get_research_types_by_section_menu_kb(section_info, research_type_df, back_callback_data)

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.GetCIBResearchData.filter())
async def get_cib_research_data(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBResearchData,
) -> None:
    """
    Изменяет сообщение, предлагая пользователю выбрать период, за который он хочет получить сводку новостей

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Выбранная отрасль и способ получения новостей (по подпискам или по всем каналам)
    """
    summary_type = callback_data.summary_type

    match summary_type:
        case enums.ResearchSummaryType.periodic.value:
            await select_period_to_get_researches(callback_query, callback_data)
        case enums.ResearchSummaryType.last_actual.value:
            await get_last_actual_research(callback_query, callback_data)
        case enums.ResearchSummaryType.analytical_indicators.value:
            await cib_client_analytical_indicators(callback_query, callback_data)
        case enums.ResearchSummaryType.exc_rate_prediction_table.value:
            await exc_rate_weekly_pulse_table(callback_query, callback_data)
        case enums.ResearchSummaryType.key_rate_dynamics_table.value:
            await key_rate_weekly_pulse_table(callback_query, callback_data)
        case enums.ResearchSummaryType.data_mart.value:
            await data_mart_callback(callback_query, callback_data)
        case enums.ResearchSummaryType.economy_daily.value:
            await ecomony_daily_callback(callback_query, callback_data)
        case enums.ResearchSummaryType.economy_monthly.value:
            await ecomony_monthly_callback(callback_query, callback_data)
        case _:
            pass


async def select_period_to_get_researches(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBResearchData,
        callback_factory: Optional[Type[CallbackData]] = callbacks.GetResearchesOverDays,
) -> None:
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
    keyboard = keyboards.get_select_period_kb(
        research_type_id,
        research_info['research_section_id'],
        callback_factory,
    )

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}"')


async def get_last_actual_research(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBResearchData,
) -> None:
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    research_type_id = callback_data.research_type_id

    research_df = subscriptions_db_api.get_researches_by_type(research_type_id)
    if not research_df.empty:
        last_research = research_df[research_df['publication_date'] == max(research_df['publication_date'])]
        await send_researches_to_user(callback_query.bot, from_user.id, full_name, last_research)
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}"')


async def cib_client_analytical_indicators(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBResearchData,
) -> None:
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
    keyboard = keyboards.get_select_period_kb(research_type_id, research_info['research_section_id'], callbacks.GetResearchesOverDays)

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}"')


async def exc_rate_weekly_pulse_table(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBResearchData,
) -> None:
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
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    await weekly_pulse.key_rate_dynamics_table(callback_query.bot, chat_id)
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}"')


async def _data_mart_body(message: types.Message) -> None:
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
    await message.answer(text=title, parse_mode='HTML', protect_content=True)

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
                'Денежное предложение '
                + table.loc[table['alias'].str.contains('Денежное предложение'), 'Экономические показатели'].str.lower()
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

            transformer.render_mpl_table(key_eco, 'key_eco', header_columns=0, col_width=4, title=title,
                                         alias=titles[i])
            png_path = config.PATH_TO_SOURCES / 'img' / 'key_eco_table.png'

            photo = types.FSInputFile(png_path)
            await __sent_photo_and_msg(message, photo, title='')


async def data_mart_callback(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBResearchData,
) -> None:
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    await _data_mart_body(callback_query.message)
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}"')


async def ecomony_monthly_callback(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBResearchData,
) -> None:
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    research_type_id = callback_data.research_type_id

    research_df = subscriptions_db_api.get_researches_by_type(research_type_id)
    if not research_df.empty:
        research_df = research_df[
            research_df['header'].str.contains(analytics_sell_side.ECONOMY_MONTHLY_HEADER_CONTAINS, case=False)
        ]
        last_research = research_df[research_df['publication_date'] == max(research_df['publication_date'])]
        await send_researches_to_user(callback_query.bot, from_user.id, full_name, last_research)
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}"')


async def ecomony_daily_callback(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetCIBResearchData,
) -> None:
    await select_period_to_get_researches(callback_query, callback_data, callbacks.GetEconomyDailyResearchesOverDays)


@router.callback_query(callbacks.GetResearchesOverDays.filter())
async def get_researches_over_period(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetResearchesOverDays,
        header_not_contains: Optional[str] = '',
) -> None:
    """
    Отправка пользователю сводки отчетов по отрасли за указанный период

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Выбранный тип отчета, кол-во дней, за которые пользователь хочет получить сводку
    :param header_not_contains: фильтрация полученных отчетов по header
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
    if header_not_contains:
        researches_df = researches_df[~researches_df['header'].str.contains(header_not_contains, case=False)]
    await send_researches_to_user(callback_query.bot, user_id, full_name, researches_df)

    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}" : получил отчеты с {research_type_id=:} за {days} дней')


@router.callback_query(callbacks.GetEconomyDailyResearchesOverDays.filter())
async def get_economy_daily_researches_over_period(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetResearchesOverDays,
) -> None:
    """
    Отправка пользователю сводки ежедневных отчетов по экономике РФ за указанный период

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Выбранный тип отчета, кол-во дней, за которые пользователь хочет получить сводку
    """
    await get_researches_over_period(
        callback_query,
        callback_data,
        header_not_contains=analytics_sell_side.ECONOMY_MONTHLY_HEADER_CONTAINS,
    )
