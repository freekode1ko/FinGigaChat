"""Файл хендлеров котировок"""
import re
from datetime import datetime

import numpy as np
import pandas as pd
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

import utils.base
from configs import config
from constants import enums, quotes as callback_prefixes
from constants.constants import sample_of_img_title
from constants.texts import texts_manager
from db.api.exc import exc_db
from db.database import engine
from handlers.quotes.research_utils import get_part_from_start_to_end, get_reports_for_quotes, get_until_upper_case
from keyboards.quotes import callbacks, constructors as keyboards
from log.bot_logger import user_logger
from module import data_transformer as dt
from utils import decorators, weekly_pulse

router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message for admin commands use chat action 'typing'


@router.callback_query(F.data.startswith(callback_prefixes.END_MENU))
async def menu_end(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Завершает работу с меню Котировки

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Состояние FSM
    """
    await state.clear()
    await callback_query.message.edit_reply_markup()
    await callback_query.message.edit_text(text='Завершена работа с меню "Котировки"')


async def main_menu(message: types.CallbackQuery | types.Message) -> None:
    """
    Формирует меню Котировки

    :param message: types.CallbackQuery | types.Message
    """
    keyboard = keyboards.get_menu_kb()
    msg_text = (
        'Выберите интересующий вас рынок, чтобы получить актуальные котировки:\n\n'
        'FX - валютный рынок. Курсы основных валют и анализ валютных пар.\n\n'
        'FI - долговой рынок.\n\n'
        # 'Equity - рынок акций.\n\n'
        'Commodities - товарный рынок. Узнайте последние цены на сырьевые товары (нефть, золото, медь и пр.)\n\n'
        'Ставки - актуальные процентные ставки\n\n'
    )
    await utils.base.send_or_edit(message, msg_text, keyboard)


@router.callback_query(callbacks.QuotesMenu.filter())
async def main_menu_callback(callback_query: types.CallbackQuery, callback_data: callbacks.QuotesMenu) -> None:
    """
    Получение меню котировки

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    await main_menu(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.message(Command(callbacks.QuotesMenu.__prefix__))
@decorators.has_access_to_feature(enums.FeatureType.quotes_menu)
async def main_menu_command(message: types.Message) -> None:
    """
    Получение меню котировки

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    await main_menu(message)


@router.callback_query(callbacks.FX.filter())
async def exchange_info(callback_query: types.CallbackQuery, callback_data: callbacks.FX, session: AsyncSession) -> None:
    """
    Вывод в чат информации по котировкам связанной с валютой и их курсом

    Отправляет копию меню в конце, если были отправлены данные

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:  Содержит дополнительную информацию
    :param session:        Сессия с бд
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    await exchange_info_command(callback_query.message, session)
    await utils.base.send_full_copy_of_message(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@decorators.has_access_to_feature(enums.FeatureType.quotes_menu)
async def exchange_info_command(message: types.Message, session: AsyncSession) -> None:
    """Вывод в чат информации по котировкам связанной с валютой и их курсом"""
    exc_data = await exc_db.get_all()
    df = pd.DataFrame([
        [i.name, i.value, i.display_order, i.exc_type.name, i.exc_type.display_order]
        for i in exc_data
    ], columns=['name', 'value', 'display_order', 'exc_type_name', 'exc_type_display_order'])
    exc_data.sort(
        key=lambda x: x.parser_source.last_update_datetime if x.parser_source.last_update_datetime else datetime.min,
        reverse=True,
    )
    curr_date = exc_data[0].parser_source.last_update_datetime.strftime(config.BASE_DATETIME_FORMAT)

    header_color = '#E2EFDA'
    default_color = '#ffffff'
    cells_counter = 1
    last_exc_type = ''
    row_colors, text_props, data = [], [], []
    for _, row in df.sort_values(['exc_type_display_order', 'display_order']).iterrows():
        if last_exc_type != row['exc_type_name']:
            last_exc_type = row['exc_type_name']
            data.append([last_exc_type, ''])
            row_colors.append(header_color)
            text_props.append((cells_counter, 0, dict(fontstyle='italic', fontweight='bold')))
            cells_counter += 1
        try:
            row['value'] = f'{float(row["value"]):_}'.replace('_', ' ')
        except ValueError:
            pass

        data.append([row['name'], row['value']])
        row_colors.append(default_color)
        cells_counter += 1

    png_path = dt.Transformer.draw_table(
        data=pd.DataFrame(data, columns=['Валютная пара', 'Значение']),
        png_name='exc',
        col_width=3,
        header_color=header_color,
        row_colors=row_colors,
        font_size=16,
        text_color='black',
        text_props=text_props,
    )

    await utils.base.__sent_photo_and_msg(
        message,
        photo=types.FSInputFile(png_path),
        reports=await get_reports_for_quotes(session, report_key=enums.QuotesType.FX, format_func=get_part_from_start_to_end),
        title=sample_of_img_title.format('Курсы валют', 'investing.com, ru.tradingview.com, finam.ru, cbr.ru', curr_date)
    )
    await weekly_pulse.exc_rate_prediction_table(message.bot, message.chat.id)


@router.callback_query(callbacks.FI.filter())
async def fin_indicators(callback_query: types.CallbackQuery, callback_data: callbacks.FI) -> None:
    """
    Меню по фин показателям

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    item_df = pd.DataFrame(
        [
            [_id, i.title, i.value]
            for _id, i in enumerate(enums.FIGroupType)
        ],
        columns=['id', 'name', 'type'],
    )
    keyboard = keyboards.get_sub_menu_kb(item_df, callbacks.GetFIItemData)
    msg_text = 'Выберите финансовый инструмент, по которому вы хотели бы получить информацию'
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')

    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.Equity.filter())
async def equity(callback_query: types.CallbackQuery, callback_data: callbacks.Equity) -> None:
    """
    Меню по работе с тикерами и клиентами

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    await not_realized_function(callback_query)  # TODO: когда будет реализовано, добавить ограничения по правам доступа
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


def format_cell_in_commodity_df(value: str | float | None) -> str | None:
    """Преобразование показателя в нужный формат"""
    if not value:
        return

    try:
        frmt_value = str(value).replace(',', '.')
        frmt_value = utils.base.__replacer(frmt_value)
        frmt_value = re.sub(r'[%s–]', '', frmt_value)
        frmt_value = '{0:,}'.format(round(float(frmt_value))).replace(',', ' ')
        frmt_value = re.sub(r'-?0.0', '0', frmt_value)
    except Exception as e:
        print(e)
        frmt_value = None

    return frmt_value


@router.callback_query(callbacks.Commodities.filter())
async def metal_info(callback_query: types.CallbackQuery, callback_data: callbacks.Commodities, session: AsyncSession) -> None:
    """
    Вывод в чат информации по котировкам связанной с сырьем (комодами)

    Отправляет копию меню в конце, если были отправлены данные

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению.
    :param callback_data:  Содержит дополнительную информацию.
    :param session:        Асинхронная сессия к бд.
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    await metal_info_command(callback_query.message, session)
    await utils.base.send_full_copy_of_message(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@decorators.has_access_to_feature(enums.FeatureType.quotes_menu)
async def metal_info_command(message: types.Message, session: AsyncSession) -> None:
    """Вывод в чат информации по котировкам связанной с сырьем (комодами)."""
    query = text(
        'SELECT sub_name, unit, "Price", "%", "Weekly", "Monthly", "YoY" FROM metals '
        'JOIN relation_commodity_metals rcm ON rcm.name_from_source=metals."Metals" '
        f'WHERE sub_name IN {callback_prefixes.COMMODITY_TABLE_ELEMENTS} ORDER BY sub_name'
    )
    res = await session.execute(query)
    commodities = res.fetchall()
    number_columns = list(callback_prefixes.COMMODITY_MARKS.values())
    materials_df = pd.DataFrame(commodities, columns=['Сырье', 'Ед. изм.', *number_columns])
    materials_df[number_columns] = materials_df[number_columns].applymap(format_cell_in_commodity_df)
    materials_df[number_columns[1:]] = materials_df[number_columns[1:]].applymap(lambda x: x + '%' if x else '-')

    png_path = dt.Transformer.render_mpl_table(materials_df, 'metal', header_columns=0, col_width=1.5)
    await utils.base.__sent_photo_and_msg(
        message,
        photo=types.FSInputFile(png_path),
        reports=await get_reports_for_quotes(session, enums.QuotesType.COMMODITIES, get_until_upper_case),
        title=sample_of_img_title.format('Сырьевые товары', 'LME, Bloomberg, investing.com', utils.base.read_curdatetime())
    )


async def not_realized_function(callback_query: types.CallbackQuery) -> None:
    """Выводит сообщение, что функция будет реализована позднее"""
    await callback_query.message.answer(
        texts_manager.COMMON_FEATURE_WILL_APPEAR.strip(),
        # protect_content=texts_manager.PROTECT_CONTENT,
        parse_mode='HTML'
    )


@router.callback_query(callbacks.GetFIItemData.filter())
async def get_fi_item_data(callback_query: types.CallbackQuery, callback_data: callbacks.GetFIItemData, session: AsyncSession) -> None:
    """
    Данные по фин показателю.

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению.
    :param callback_data:  Содержит дополнительную информацию.
    :param session:        Асинхронная сессия к бд.
    """
    _type = callback_data.type

    match _type:
        case enums.FIGroupType.bonds.value:
            await bonds_info(callback_query, callback_data, session)
        case _:
            await not_realized_function(callback_query)


async def bonds_info(callback_query: types.CallbackQuery, callback_data: callbacks.GetFIItemData, session: AsyncSession) -> None:
    """
    Вывод в чат информации по котировкам связанной с облигациями

    Отправляет копию меню в конце, если были отправлены данные

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению.
    :param callback_data:  Содержит дополнительную информацию.
    :param session:        Асинхронная сессия к бд.
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    await bonds_info_command(callback_query.message, session)
    await utils.base.send_full_copy_of_message(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@decorators.has_access_to_feature(enums.FeatureType.quotes_menu)
async def bonds_info_command(message: types.Message, session: AsyncSession) -> None:
    """Вывод в чат информации по котировкам связанной с облигациями"""
    columns = ['Название', 'Доходность', 'Изм, %']
    bonds = pd.read_sql_query('SELECT * FROM "bonds"', con=engine)
    bonds = bonds[columns].dropna(axis=0)
    bond_ru = bonds.loc[bonds['Название'].str.contains(r'Россия')].round(2)
    bond_ru = bond_ru.rename(columns={'Название': 'Cрок до погашения', 'Доходность': 'Доходность, %', 'Изм, %': 'Изм, % за день'})
    years = ['1 год', '2 года', '3 года', '5 лет', '7 лет', '10 лет', '15 лет', '20 лет']
    for num, name in enumerate(bond_ru['Cрок до погашения'].values):
        bond_ru['Cрок до погашения'].values[num] = years[num]
    png_path = dt.Transformer.render_mpl_table(bond_ru, 'bonds', header_columns=0, col_width=2.5)

    await utils.base.__sent_photo_and_msg(
        message,
        photo=types.FSInputFile(png_path),
        reports=await get_reports_for_quotes(session, report_key=enums.QuotesType.FI, format_func=get_part_from_start_to_end),
        title=sample_of_img_title.format('Доходность ОФЗ', 'investing.com', utils.base.read_curdatetime())
    )


@router.callback_query(callbacks.Eco.filter())
async def economy_info(callback_query: types.CallbackQuery, callback_data: callbacks.Eco, session: AsyncSession) -> None:
    """
    Вывод в чат информации по котировкам связанной с экономикой (ключевая ставка)

    Отправляет копию меню в конце, если были отправлены данные

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению.
    :param callback_data:  Содержит дополнительную информацию.
    :param session:        Асинхронная сессия к бд.
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    await economy_info_command(callback_query.message, session)
    await utils.base.send_full_copy_of_message(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@decorators.has_access_to_feature(enums.FeatureType.quotes_menu)
async def economy_info_command(message: types.Message, session: AsyncSession) -> None:
    """Вывод в чат информации по котировкам связанной с экономикой (ключевая ставка)"""
    world_bet = pd.read_sql_query('SELECT * FROM "eco_global_stake"', con=engine)
    rus_infl = pd.read_sql_query('SELECT * FROM "eco_rus_influence"', con=engine)
    rus_infl = rus_infl[['Дата', 'Инфляция, % г/г']]
    world_bet = world_bet.rename(columns={'Country': 'Страна', 'Last': 'Ставка, %', 'Previous': 'Предыдущая, %'})
    countries = {
        'Japan': 'Япония',
        'Switzerland': 'Швейцария',
        'South Korea': 'Южная Корея',
        'Singapore': 'Сингапур',
        'China': 'Китай',
        'Euro Area': 'Еврозона',
        'Australia': 'Австралия',
        'Canada': 'Канада',
        'United Kingdom': 'Великобритания',
        'United States': 'США',
        'Indonesia': 'Индонезия',
        'Saudi Arabia': 'Саудовская Аравия',
        'India': 'Индия',
        'Russia': 'Россия',
        'South Africa': 'ЮАР',
        'Mexico': 'Мексика',
        'Brazil': 'Бразилия',
        'Turkey': 'Турция',
        'Argentina': 'Аргентина',
    }
    world_bet = world_bet[['Страна', 'Ставка, %', 'Предыдущая, %']]
    for num, country in enumerate(world_bet['Страна'].values):
        world_bet.Страна[world_bet.Страна == country] = countries[country]

    png_path = dt.Transformer.render_mpl_table(world_bet.round(2), 'world_bet', header_columns=0, col_width=2.2)
    curdatetime = utils.base.read_curdatetime()
    await utils.base.__sent_photo_and_msg(
        message,
        photo=types.FSInputFile(png_path),
        reports=await get_reports_for_quotes(session, report_key=enums.QuotesType.ECO),
        title=sample_of_img_title.format('Ключевые ставки ЦБ мира', 'ЦБ стран мира', curdatetime)
    )

    month_dict = {
        1: 'Январь',
        2: 'Февраль',
        3: 'Март',
        4: 'Апрель',
        5: 'Май',
        6: 'Июнь',
        7: 'Июль',
        8: 'Август',
        9: 'Сентябрь',
        10: 'Октябрь',
        11: 'Ноябрь',
        12: 'Декабрь',
    }
    for num, date in enumerate(rus_infl['Дата'].values):
        cell = str(date).split('.')
        rus_infl.Дата[rus_infl.Дата == date] = '{} {}'.format(month_dict[int(cell[0])], cell[1])

    png_path = dt.Transformer.render_mpl_table(rus_infl.round(2), 'rus_infl', header_columns=0, col_width=2)
    await message.answer_photo(
        photo=types.FSInputFile(png_path),
        caption=sample_of_img_title.format('Инфляция в России', 'ЦБ РФ', curdatetime),
        parse_mode='HTML',
        # protect_content=texts_manager.PROTECT_CONTENT,
    )
    # сообщение с текущими ставками
    stat = pd.read_sql_query('SELECT * FROM "eco_stake"', con=engine)

    stat_order = {
        'Текущая ключевая ставка Банка России': 0,
        'Текущая ставка RUONIA': 1,
        'LPR Китай': 2,
    }

    stat['order'] = stat['0'].apply(lambda x: stat_order.get(x, np.inf))
    stat = stat.set_index('order', drop=True).sort_index().reset_index(drop=True)

    rates = [f"{rate[0]}: {str(rate[1]).replace('%', '').replace(',', '.')}%" for rate in stat.values.tolist()[:3]]
    rates_message = f'<b>{rates[0]}</b>\n{rates[1]}\n{rates[2]}'
    await message.answer(
        rates_message,
        parse_mode='HTML',
        # protect_content=texts_manager.PROTECT_CONTENT,
    )
    await weekly_pulse.key_rate_dynamics_table(message.bot, message.chat.id)
    msg_text = f'<a href="{config.ECO_INAVIGATOR_URL}" >Актуальные ETC</a>'
    await message.answer(
        msg_text,
        parse_mode='HTML',
        # protect_content=texts_manager.PROTECT_CONTENT,
    )
