# import logging
import re
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionMiddleware
from sqlalchemy import text

from log.bot_logger import user_logger
from configs.config import path_to_source
from constants.constants import sample_of_img_title
from constants.quotes import COMMODITY_TABLE_ELEMENTS, COMMODITY_MARKS
from db.database import engine
from module import data_transformer as dt
from utils.base import (
    __replacer,
    __sent_photo_and_msg,
    read_curdatetime,
    user_in_whitelist,
)

# logger = logging.getLogger(__name__)
router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message for admin commands use chat action 'typing'


# ['облигации', 'бонды', 'офз']
@router.message(Command('bonds'))
async def bonds_info(message: types.Message) -> None:
    """
    Вывод в чат информации по котировкам связанной с облигациями

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        columns = ['Название', 'Доходность', 'Изм, %']
        bonds = pd.read_sql_query('SELECT * FROM "bonds"', con=engine)
        bonds = bonds[columns].dropna(axis=0)
        bond_ru = bonds.loc[bonds['Название'].str.contains(r'Россия')].round(2)
        bond_ru = bond_ru.rename(columns={'Название': 'Cрок до погашения', 'Доходность': 'Доходность, %', 'Изм, %': 'Изм, % за день'})
        years = ['1 год', '2 года', '3 года', '5 лет', '7 лет', '10 лет', '15 лет', '20 лет']
        for num, name in enumerate(bond_ru['Cрок до погашения'].values):
            bond_ru['Cрок до погашения'].values[num] = years[num]

        transformer = dt.Transformer()
        png_path = '{}/img/{}_table.png'.format(path_to_source, 'bonds')
        transformer.render_mpl_table(bond_ru, 'bonds', header_columns=0, col_width=2.5, title='Доходности ОФЗ.')
        photo = types.FSInputFile(png_path)
        day = pd.read_sql_query('SELECT * FROM "report_bon_day"', con=engine).values.tolist()
        month = pd.read_sql_query('SELECT * FROM "report_bon_mon"', con=engine).values.tolist()
        title = 'Доходность ОФЗ'
        data_source = 'investing.com'
        await __sent_photo_and_msg(
            message, photo, day, month, protect_content=False, title=sample_of_img_title.format(title, data_source, read_curdatetime())
        )

        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


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
        png_path = '{}/img/{}_table.png'.format(path_to_source, 'world_bet')
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
        png_path = '{}/img/{}_table.png'.format(path_to_source, 'rus_infl')
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
        title = 'Прогноз динамики ключевой ставки'
        data_source = 'Sber analytical research'
        png_path = Path(path_to_source) / 'weeklies' / 'key_rate_dynamics_table.png'

        photo = types.FSInputFile(png_path)
        await __sent_photo_and_msg(message, photo, title=sample_of_img_title.format(title, data_source, curdatetime))
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


@router.message(Command('view'))
async def data_mart(message: types.Message) -> None:
    """
    Вывод в чат информации по ключевым экономическим показателям

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        transformer = dt.Transformer()
        key_eco_table = pd.read_sql_query('SELECT * FROM key_eco', con=engine)
        split_numbers = key_eco_table.groupby('alias')['id'].max().reset_index().sort_values('id', ascending=True)
        key_eco_table = key_eco_table.rename(columns=({'name': 'Экономические показатели'}))

        spld_keys_eco = np.split(key_eco_table, split_numbers['id'])
        title = '<b>Динамика и прогноз основных макроэкономических показателей</b>'
        await message.answer(text=title, parse_mode='HTML', protect_content=True)

        for table in spld_keys_eco:
            table = table.reset_index(drop=True, inplace=True)
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

                transformer.render_mpl_table(key_eco, 'key_eco', header_columns=0, col_width=4, title=title, alias=titles[i])
                png_path = '{}/img/{}_table.png'.format(path_to_source, 'key_eco')

                photo = types.FSInputFile(png_path)
                await __sent_photo_and_msg(message, photo, title='')

        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


# ['Курсы валют', 'курсы', 'валюты', 'рубль', 'доллар', 'юань', 'евро']
@router.message(Command('fx'))
async def exchange_info(message: types.Message) -> None:
    """
    Вывод в чат информации по котировкам связанной с валютой и их курсом

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        png_path = '{}/img/{}_table.png'.format(path_to_source, 'exc')
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
            message, photo, day, month, protect_content=False, title=sample_of_img_title.format(title, data_source, curdatetime)
        )

        fx_predict = pd.read_excel('{}/tables/fx_predict.xlsx'.format(path_to_source)).rename(columns={'базовый сценарий': ' '})
        title = 'Прогноз валютных курсов'
        data_source = 'Sber analytical research'
        transformer.render_mpl_table(fx_predict, 'fx_predict', header_columns=0, col_width=1.5, title=title)
        png_path = Path('{}/weeklies/{}.png'.format(path_to_source, 'exc_rate_prediction_table'))
        photo = types.FSInputFile(png_path)
        await __sent_photo_and_msg(message, photo, title=sample_of_img_title.format(title, data_source, curdatetime))

        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


# ['Металлы', 'сырьевые товары', 'commodities']
@router.message(Command('commodities'))
async def metal_info(message: types.Message) -> None:
    """
    Вывод в чат информации по котировкам связанной с сырьем (комодами)

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):

        materials = []
        query = text('select sub_name, unit, "Price", "%", "Weekly", "Monthly", "YoY" from metals '
                     'join relation_commodity_metals rcm on rcm.name_from_source=metals."Metals" '
                     'where sub_name=:sub_name')
        with engine.connect() as conn:
            for element in COMMODITY_TABLE_ELEMENTS:
                element_data = conn.execute(query.bindparams(sub_name=element)).fetchall()
                if element_data:
                    materials.append(*element_data)

        number_columns = list(COMMODITY_MARKS.values())
        materials_df = pd.DataFrame(materials, columns=['Сырье', 'Ед. изм.', *number_columns])
        # materials_df = materials_df.replace(['', 'None', 'null'], [np.nan, np.nan, np.nan])

        materials_df[number_columns] = materials_df[number_columns].applymap(format_cell_in_commodity_df)
        materials_df[number_columns[1:]] = materials_df[number_columns[1:]].applymap(
            lambda x: x + '%' if x else x.replace('', '-')
        )

        transformer = dt.Transformer()
        transformer.render_mpl_table(
            materials_df,
            'metal',
            header_columns=0,
            col_width=1.5,
            title='Цены на ключевые сырьевые товары.'
        )

        png_path = '{}/img/{}_table.png'.format(path_to_source, 'metal')
        day = pd.read_sql_table('report_met_day', con=engine).values.tolist()
        photo = types.FSInputFile(png_path)
        title = 'Сырьевые товары'
        data_source = 'LME, Bloomberg, investing.com'
        await __sent_photo_and_msg(
            message, photo, day, title=sample_of_img_title.format(title, data_source, read_curdatetime())
        )

        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


def format_cell_in_commodity_df(value) -> str | None:
    try:
        result = str(value).replace(',', '.')
        result = __replacer(result)
        result = result.replace('s', '')
        result = result.replace('%', '')
        result = result.replace('–', '-')
        result = '{0:,}'.format(round(float(result))).replace(',', ' ')
        result = result.replace('-0.0', '0')
        result = result.replace('0.0', '0')
    except Exception as e:
        print(e)
        result = None

    return result
