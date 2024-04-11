import re

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionMiddleware
import numpy as np
import pandas as pd
from sqlalchemy import text

from configs.config import PATH_TO_SOURCES
from constants.constants import sample_of_img_title
from constants import quotes as callback_prefixes, enums
from db.database import engine
from keyboards.quotes import constructors as keyboards, callbacks
from log.bot_logger import user_logger
from module import data_transformer as dt
from utils import weekly_pulse
from utils.base import (
    __replacer,
    __sent_photo_and_msg,
    read_curdatetime,
    user_in_whitelist,
    send_or_edit,
)


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
    """Формирует меню Котировки"""
    keyboard = keyboards.get_menu_kb()
    msg_text = (
        'Выберите интересующий вас рынок, чтобы получить актуальные котировки:\n\n'
        'FX - валютный рынок. Курсы основных валют и анализ валютных пар.\n\n'
        'FI - долговой рынок.\n\n'
        'Equity - рынок акций.\n\n'
        'Commodities - товарный рынок. Узнайте последние цены на сырьевые товары (нефть, золото, медь и пр.)\n\n'
    )
    await send_or_edit(message, msg_text, keyboard)


@router.callback_query(callbacks.QuotesMenu.filter())
async def main_menu_callback(callback_query: types.CallbackQuery, callback_data: callbacks.QuotesMenu) -> None:
    """
    Получение меню котировки

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    await main_menu(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.message(Command(callbacks.QuotesMenu.__prefix__))
async def main_menu_command(message: types.Message) -> None:
    """
    Получение меню котировки

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
        await main_menu(message)
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


# ['Курсы валют', 'курсы', 'валюты', 'рубль', 'доллар', 'юань', 'евро']
@router.callback_query(callbacks.FX.filter())
async def exchange_info(callback_query: types.CallbackQuery, callback_data: callbacks.FX) -> None:
    """
    Вывод в чат информации по котировкам связанной с валютой и их курсом

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    png_path = PATH_TO_SOURCES / 'img' / 'exc_table.png'
    exc = pd.read_sql_query('SELECT * FROM exc', con=engine)
    exc['Курс'] = exc['Курс'].apply(lambda x: round(float(x), 2) if x is not None else x)

    exc_order = {
        'USD/RUB': 0,
        'EUR/RUB': 1,
        'CNH/RUB': 2,
        'Индекс DXY': 3,
        'EUR/USD': 4,
        'USD/CNH': 5,
    }

    for num, currency in enumerate(exc['Валюта'].values):
        if currency.lower() == 'usdollar':
            exc['Валюта'].values[num] = 'Индекс DXY'
        else:
            cur = currency.upper().split('-')
            exc['Валюта'].values[num] = '/'.join(cur).replace('CNY', 'CNH')
    exc['order'] = exc['Валюта'].apply(lambda x: exc_order.get(x, np.inf))
    exc.set_index('order', drop=True, inplace=True)
    exc = exc.sort_index().reset_index(drop=True)

    transformer = dt.Transformer()
    transformer.render_mpl_table(exc.round(2), 'exc', header_columns=0, col_width=2, title='Текущие курсы валют')
    day = pd.read_sql_query('SELECT * FROM "report_exc_day"', con=engine).values.tolist()
    month = pd.read_sql_query('SELECT * FROM "report_exc_mon"', con=engine).values.tolist()
    photo = types.FSInputFile(png_path)
    title = 'Курсы валют'
    data_source = 'investing.com'
    curdatetime = read_curdatetime()
    await __sent_photo_and_msg(
        callback_query.message,
        photo,
        day,
        month,
        protect_content=False,
        title=sample_of_img_title.format(title, data_source, curdatetime),
    )

    fx_predict = pd.read_excel(PATH_TO_SOURCES / 'tables' / 'fx_predict.xlsx').rename(columns={'базовый сценарий': ' '})
    transformer.render_mpl_table(fx_predict, 'fx_predict', header_columns=0, col_width=1.5, title=title)
    await weekly_pulse.exc_rate_prediction_table(callback_query.bot, chat_id)

    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.FI.filter())
async def fin_indicators(callback_query: types.CallbackQuery, callback_data: callbacks.FI) -> None:
    """
    Меню по фин показателям

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
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
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    await not_realized_function(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


def format_cell_in_commodity_df(value: str | float | None) -> str | None:
    """Преобразование показателя в нужный формат"""
    if not value:
        return

    try:
        frmt_value = str(value).replace(',', '.')
        frmt_value = __replacer(frmt_value)
        frmt_value = re.sub(r'[%s–]', '', frmt_value)
        frmt_value = '{0:,}'.format(round(float(frmt_value))).replace(',', ' ')
        frmt_value = re.sub(r'-?0.0', '0', frmt_value)
    except Exception as e:
        print(e)
        frmt_value = None

    return frmt_value


# ['Металлы', 'сырьевые товары', 'commodities']
@router.callback_query(callbacks.Commodities.filter())
async def metal_info(callback_query: types.CallbackQuery, callback_data: callbacks.Commodities) -> None:
    """
    Вывод в чат информации по котировкам связанной с сырьем (комодами)

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    query = text(
        'SELECT sub_name, unit, "Price", "%", "Weekly", "Monthly", "YoY" FROM metals '
        'JOIN relation_commodity_metals rcm ON rcm.name_from_source=metals."Metals" '
        'WHERE sub_name IN :sub_names ORDER BY sub_name'
    )
    with engine.connect() as conn:
        materials = conn.execute(query.bindparams(sub_names=callback_prefixes.COMMODITY_TABLE_ELEMENTS)).fetchall()

    number_columns = list(callback_prefixes.COMMODITY_MARKS.values())
    materials_df = pd.DataFrame(materials, columns=['Сырье', 'Ед. изм.', *number_columns])

    materials_df[number_columns] = materials_df[number_columns].applymap(format_cell_in_commodity_df)
    materials_df[number_columns[1:]] = materials_df[number_columns[1:]].applymap(lambda x: x + '%' if x else '-')

    transformer = dt.Transformer()
    transformer.render_mpl_table(
        materials_df,
        'metal',
        header_columns=0,
        col_width=1.5,
        title='Цены на ключевые сырьевые товары.'
    )

    png_path = PATH_TO_SOURCES / 'img' / 'metal_table.png'
    day = pd.read_sql_table('report_met_day', con=engine).values.tolist()
    photo = types.FSInputFile(png_path)
    title = 'Сырьевые товары'
    data_source = 'LME, Bloomberg, investing.com'
    await __sent_photo_and_msg(
        callback_query.message, photo, day, title=sample_of_img_title.format(title, data_source, read_curdatetime())
    )

    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


async def not_realized_function(callback_query: types.CallbackQuery) -> None:
    """Выводит сообщение, что функция будет реализована позднее"""
    msg_text = 'Данная функциональность будет реализована позднее'
    await callback_query.message.answer(msg_text, protect_content=True, parse_mode='HTML')


@router.callback_query(callbacks.GetFIItemData.filter())
async def get_fi_item_data(callback_query: types.CallbackQuery, callback_data: callbacks.GetFIItemData) -> None:
    """
    Данные по фин показателю

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    _type = callback_data.type

    match _type:
        case enums.FIGroupType.bonds.value:
            await bonds_info(callback_query, callback_data)
        case _:
            await not_realized_function(callback_query)


# ['облигации', 'бонды', 'офз']
async def bonds_info(callback_query: types.CallbackQuery, callback_data: callbacks.GetFIItemData) -> None:
    """
    Вывод в чат информации по котировкам связанной с облигациями

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    columns = ['Название', 'Доходность', 'Изм, %']
    bonds = pd.read_sql_query('SELECT * FROM "bonds"', con=engine)
    bonds = bonds[columns].dropna(axis=0)
    bond_ru = bonds.loc[bonds['Название'].str.contains(r'Россия')].round(2)
    bond_ru = bond_ru.rename(columns={'Название': 'Cрок до погашения', 'Доходность': 'Доходность, %', 'Изм, %': 'Изм, % за день'})
    years = ['1 год', '2 года', '3 года', '5 лет', '7 лет', '10 лет', '15 лет', '20 лет']
    for num, name in enumerate(bond_ru['Cрок до погашения'].values):
        bond_ru['Cрок до погашения'].values[num] = years[num]

    transformer = dt.Transformer()
    png_path = PATH_TO_SOURCES / 'img' / 'bonds_table.png'
    transformer.render_mpl_table(bond_ru, 'bonds', header_columns=0, col_width=2.5, title='Доходности ОФЗ.')
    photo = types.FSInputFile(png_path)
    day = pd.read_sql_query('SELECT * FROM "report_bon_day"', con=engine).values.tolist()
    month = pd.read_sql_query('SELECT * FROM "report_bon_mon"', con=engine).values.tolist()
    title = 'Доходность ОФЗ'
    data_source = 'investing.com'
    await __sent_photo_and_msg(
        callback_query.message,
        photo,
        day,
        month,
        protect_content=False,
        title=sample_of_img_title.format(title, data_source, read_curdatetime()),
    )

    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


# ['экономика', 'ставки', 'ключевая ставка', 'кс', 'монетарная политика']
@router.message(Command('eco'))
async def economy_info(message: types.Message) -> None:
    """
    Вывод в чат информации по котировкам связанной с экономикой (ключевая ставка)

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
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
        transformer = dt.Transformer()
        png_path = PATH_TO_SOURCES / 'img' / 'world_bet_table.png'
        world_bet = world_bet.round(2)
        transformer.render_mpl_table(world_bet, 'world_bet', header_columns=0, col_width=2.2, title='Ключевые ставки ЦБ мира.')
        photo = types.FSInputFile(png_path)
        day = pd.read_sql_query('SELECT * FROM "report_eco_day"', con=engine).values.tolist()
        month = pd.read_sql_query('SELECT * FROM "report_eco_mon"', con=engine).values.tolist()
        title = 'Ключевые ставки ЦБ мира'
        data_source = 'ЦБ стран мира'
        curdatetime = read_curdatetime()
        await __sent_photo_and_msg(
            message, photo, day, month, protect_content=False, title=sample_of_img_title.format(title, data_source, curdatetime)
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
        transformer.render_mpl_table(
            rus_infl.round(2), 'rus_infl', header_columns=0, col_width=2, title='Ежемесячная инфляция в России.'
        )
        png_path = PATH_TO_SOURCES / 'img' / 'rus_infl_table.png'
        photo = types.FSInputFile(png_path)
        title = 'Инфляция в России'
        data_source = 'ЦБ РФ'
        await message.answer_photo(
            photo,
            caption=sample_of_img_title.format(title, data_source, curdatetime),
            parse_mode='HTML',
            protect_content=False,
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
        await message.answer(rates_message, parse_mode='HTML', protect_content=False)
        await weekly_pulse.key_rate_dynamics_table(message.bot, message.chat.id)
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')
