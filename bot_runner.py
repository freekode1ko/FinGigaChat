import re
import os
import json
import asyncio
import warnings
import textwrap
import numpy as np
import pandas as pd
from typing import Dict
from urllib.parse import urlparse
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
from pathlib import Path

from aiogram.utils.exceptions import MessageIsTooLong, ChatNotFound
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext

from module.article_process import ArticleProcess, ArticleProcessAdmin
from module.model_pipe import summarization_by_chatgpt
import module.data_transformer as dt
import module.gigachat as gig
from module.logger_base import get_db_logger, get_handler, selector_logger
import config

path_to_source = config.path_to_source
psql_engine = config.psql_engine
API_TOKEN = config.api_token

articles_l5 = ''
token = ''
chat = ''

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

bonds_aliases = ['облигации', 'бонды', 'офз', 'бонлы', 'доходность офз']
eco_aliases = ['экономика', 'ставки', 'ключевая ставка', 'кс', 'монетарная политика', 'макро',
               'макроэкономика', 'ключевая ставка', 'кс', 'ставка цб', 'ruonia', 'lpr', 'инфляция']
exchange_aliases = ['курсы валют', 'курсы', 'валюты', 'рубль', 'доллар', 'юань', 'евро', 'fx', 'валютный рынок',
                    'валюта', 'курс доллара', 'курс евро', 'курс юаня', 'курс рубля', 'доллар к рублю',
                    'прогноз валютных курсов', 'прогнозы курса', 'прогнозы курса рубля', 'прогнозы курса доллара',
                    'прогнозы курса юаня', 'мягкие валюты', 'рупии', 'лиры', 'тенге']
metal_aliases = ['металлы', 'сырьевые товары', 'commodities', 'сырьевые рынки', 'сырье', 'цены на commodities',
                 'ценны на металлы']
view_aliases = ['ввп', 'бюджет', 'баланс бюджета', 'денежное предложение', 'проценстная ставка по кредитам',
                'проценстная ставка по депозитам', 'безработица', 'платежный баланс', 'экспорт', 'импорт',
                'торговый баланс', 'счет текущих операций', 'международные резервы', 'внешний долг', 'госдолг']

sample_of_news_title = '<b>{}</b>\n<a href="{}">{}</a>\n\n'
sample_of_img_title = '<b>{}</b>\nИсточник: {}\nДанные на <i>{}</i>'
sample_of_img_title_view = '<b>{}\n{}</b>\nДанные на <i>{}</i>'
PATH_TO_COMMODITY_GRAPH = 'sources/img/{}_graph.png'

research_footer = 'Источник: Sber Analytical Research. Распространение материалов за пределами Сбербанка запрещено'
giga_ans_footer = 'Ответ сгенерирован Gigachat. Информация требует дополнительной верификации'


# States
class Form(StatesGroup):
    link = State()
    link_change_summary = State()
    link_to_delete = State()
    permission_to_delete = State()
    user_subscriptions = State()
    send_to_users = State()


def read_curdatetime():
    """
    Чтение даты последней сборки из базы данных

    return Дата последней сборки
    """
    engine = create_engine(psql_engine)
    curdatetime = pd.read_sql_query('SELECT * FROM "date_of_last_build"', con=engine)
    return curdatetime['date_time'][0]


async def __text_splitter(message: types.Message, text: str, name: str, date: str, batch_size: int = 2048):
    """
    Разбиение сообщения на части по количеству символов

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param text: Содержание отчета
    :param name: Заголовок отчета
    :param date: Дата сборки отчета
    :param batch_size: Размер сообщения в символах. По стандарту это значение равно 2048 символов на сообщение
    return None
    """
    text_group = []
    # import dateutil.parser as dparser
    # date = dparser.parse(date, fuzzy=True)

    # uncommet me if need summory #TODO: исправить порядок параметров и промпт
    # ****************************
    # giga_ans = await giga_ask(message, prompt='{}\n {}'.format(summ_prompt, text), return_ans=True)
    # ****************************
    # giga_ans = text.replace('\n', '\n\n')
    # giga_ans = text.replace('>', '\n\n')

    giga_ans = text
    if len(giga_ans) > batch_size:
        for batch in range(0, len(giga_ans), batch_size):
            text_group.append(text[batch:batch + batch_size])
        for summ_part in text_group:
            await message.answer('<b>{}</b>\n\n{}\n\n<i>{}</i>'.format(name, summ_part, research_footer, date),
                                 parse_mode="HTML", protect_content=True)
    else:
        await message.answer('<b>{}</b>\n\n{}\n\n{}\n\n<i>{}</i>'.format(name, giga_ans, research_footer, date),
                             parse_mode="HTML", protect_content=True)


async def __sent_photo_and_msg(message: types.Message, photo, day: str = '',
                               month: str = '', title: str = '', source: str = '',
                               protect_content: bool = True):
    """
    Отправка в чат пользователю сообщение с текстом и/или изображения

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param photo: Фотокарточка для отправки
    :param day: Дневной отчет в формате текста
    :param month: Месячный отчет в формате текста
    :param title: Подпись к фотокарточке
    :param source: Не используется на данный момент
    :param protect_content: Булевое значение отвечающее за защиту от копирования сообщения и его текста/фотокарточки
    return None
    """
    batch_size = 3500
    if month:  # 'Публикация месяца
        for month_rev in month[::-1]:
            month_rev_text = month_rev[1].replace('Сегодня', 'Сегодня ({})'.format(month_rev[2]))
            month_rev_text = month_rev_text.replace('cегодня', 'cегодня ({})'.format(month_rev[2]))
            await __text_splitter(message, month_rev_text, month_rev[0], month_rev[2], batch_size)
    if day:  # Публикация дня
        for day_rev in day[::-1]:
            day_rev_text = day_rev[1].replace('Сегодня', 'Сегодня ({})'.format(day_rev[2]))
            day_rev_text = day_rev_text.replace('cегодня', 'cегодня ({})'.format(day_rev[2]))
            await __text_splitter(message, day_rev_text, day_rev[0], day_rev[2], batch_size)
    await bot.send_photo(message.chat.id, photo, caption=title, parse_mode='HTML', protect_content=protect_content)


@dp.message_handler(commands=['start', 'help'])
async def help_handler(message: types.Message):
    """
    Вывод приветственного окна, с описанием бота и лицами для связи

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    return None
    """
    help_text = config.help_text
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.as_json()):
        to_pin = await bot.send_message(chat_id, help_text, protect_content=False)
        msg_id = to_pin.message_id
        await bot.pin_chat_message(chat_id=chat_id, message_id=msg_id)

        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


# ['облигации', 'бонды', 'офз']
@dp.message_handler(commands=['bonds'])
async def bonds_info(message: types.Message):
    """
    Вывод в чат информации по котировкам связанной с облигациями

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    return None
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.as_json()):
        columns = ['Название', 'Доходность', 'Изм, %']
        engine = create_engine(psql_engine)
        bonds = pd.read_sql_query('SELECT * FROM "bonds"', con=engine)
        bonds = bonds[columns].dropna(axis=0)
        bond_ru = bonds.loc[bonds['Название'].str.contains(r'Россия')].round(2)
        bond_ru = bond_ru.rename(columns={'Название': 'Cрок до погашения', 'Доходность': 'Доходность, %'})
        years = ['1 год', '2 года', '3 года', '5 лет',
                 '7 лет', '10 лет', '15 лет', '20 лет']
        for num, name in enumerate(bond_ru['Cрок до погашения'].values):
            bond_ru['Cрок до погашения'].values[num] = years[num]

        transformer = dt.Transformer()
        png_path = '{}/img/{}_table.png'.format(path_to_source, 'bonds')
        transformer.render_mpl_table(bond_ru, 'bonds', header_columns=0, col_width=2.5, title='Доходности ОФЗ.')
        photo = open(png_path, 'rb')
        day = pd.read_sql_query('SELECT * FROM "report_bon_day"', con=engine).values.tolist()
        month = pd.read_sql_query('SELECT * FROM "report_bon_mon"', con=engine).values.tolist()
        title = 'ОФЗ'
        data_source = 'investing.com'
        await __sent_photo_and_msg(message, photo, day, month, protect_content=False,
                                   title=sample_of_img_title.format(title, data_source, read_curdatetime()))

        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


# ['экономика', 'ставки', 'ключевая ставка', 'кс', 'монетарная политика']
@dp.message_handler(commands=['eco'])
async def economy_info(message: types.Message):
    """
    Вывод в чат информации по котировкам связанной с экономикой (ключевая ставка)

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    return None
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.as_json()):
        engine = create_engine(psql_engine)
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
            'Argentina': 'Аргентина'
        }
        world_bet = world_bet[['Страна', 'Ставка, %', 'Предыдущая, %']]
        for num, country in enumerate(world_bet['Страна'].values):
            world_bet.Страна[world_bet.Страна == country] = countries[country]
        transformer = dt.Transformer()
        png_path = '{}/img/{}_table.png'.format(path_to_source, 'world_bet')
        world_bet = world_bet.round(2)
        transformer.render_mpl_table(world_bet, 'world_bet', header_columns=0,
                                     col_width=2.2, title='Ключевые ставки ЦБ мира.')
        photo = open(png_path, 'rb')
        day = pd.read_sql_query('SELECT * FROM "report_eco_day"', con=engine).values.tolist()
        month = pd.read_sql_query('SELECT * FROM "report_eco_mon"', con=engine).values.tolist()
        title = 'Ключевые ставки ЦБ мира'
        data_source = 'ЦБ стран мира'
        curdatetime = read_curdatetime()
        await __sent_photo_and_msg(message, photo, day, month, protect_content=False,
                                   title=sample_of_img_title.format(title, data_source, curdatetime))

        month_dict = {
            1: "Январь", 2: "Февраль", 3: "Март",
            4: "Апрель", 5: "Май", 6: "Июнь",
            7: "Июль", 8: "Август", 9: "Сентябрь",
            10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }
        for num, date in enumerate(rus_infl['Дата'].values):
            cell = str(date).split('.')
            rus_infl.Дата[rus_infl.Дата == date] = '{} {}'.format(month_dict[int(cell[0])], cell[1])
        transformer.render_mpl_table(rus_infl.round(2), 'rus_infl', header_columns=0,
                                     col_width=2, title='Ежемесячная инфляция в России.')
        png_path = '{}/img/{}_table.png'.format(path_to_source, 'rus_infl')
        photo = open(png_path, 'rb')
        title = 'Инфляция в России'
        data_source = 'ЦБ РФ'
        await bot.send_photo(message.chat.id, photo,
                             caption=sample_of_img_title.format(title, data_source, curdatetime),
                             parse_mode='HTML', protect_content=False)
        # сообщение с текущими ставками
        stat = pd.read_sql_query('SELECT * FROM "eco_stake"', con=engine)
        rates = [f"{rate[0]}: {str(rate[1]).replace('%', '').replace(',', '.')}%" for rate in stat.values.tolist()[:3]]
        rates_message = f'<b>{rates[0]}</b>\n{rates[1]}\n{rates[2]}'
        await message.answer(rates_message, parse_mode='HTML', protect_content=False)

        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


@dp.message_handler(commands=['view'])
async def data_mart(message: types.Message):
    """
    Вывод в чат информации по ключевым экономическим показателям

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    return None
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.as_json()):
        transformer = dt.Transformer()
        engine = create_engine(psql_engine)
        key_eco_table = pd.read_sql_query('SELECT * FROM key_eco', con=engine)
        split_numbers = key_eco_table.groupby('alias')['id'].max().reset_index().sort_values('id', ascending=True)
        key_eco_table = key_eco_table.rename(columns=({'name': 'Экономические показатели'}))

        spld_keys_eco = np.split(key_eco_table, split_numbers['id'])
        title = '<b>Динамика и прогноз основных макроэкономических показателей</b>'
        await bot.send_message(message.chat.id, text=title, parse_mode='HTML', protect_content=True)

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
            'Обменный курс': 6
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
            table.loc[table['alias'].str.contains('Денежное предложение'), 'Экономические показатели'] = \
                'Денежное предложение ' + table.loc[table['alias'].str.contains('Денежное предложение'),
                                                    'Экономические показатели'].str.lower()
        # Средняя процентная ставка
        for table in tables:
            condition = table['alias'].str.contains('Средняя процентная ставка')
            values_to_update = table.loc[condition, 'Экономические показатели']
            values_to_update = values_to_update.apply(lambda x: '\n'.join(textwrap.wrap(x, width=30)))
            updated_values = 'Средняя ставка ' + values_to_update.str.lower()
            table.loc[condition, 'Экономические показатели'] = updated_values

        # рубль/доллар
        for table in tables:
            table.loc[table['alias'].str.contains('рубль/доллар'), 'Экономические показатели'] = \
                table.loc[table['alias'].str.contains('рубль/доллар'), 'Экономические показатели'] + ', $/руб'
        # ИПЦ
        for table in tables:
            table.loc[table['alias'].str.contains('ИПЦ'), 'Экономические показатели'] = \
                table.loc[table['alias'].str.contains('ИПЦ'), 'Экономические показатели'] + ', ИПЦ'
        # ИЦП
        for table in tables:
            table.loc[table['alias'].str.contains('ИЦП'), 'Экономические показатели'] = \
                table.loc[table['alias'].str.contains('ИЦП'), 'Экономические показатели'] + ', ИЦП'
        # Юралз
        for table in tables:
            condition = table['alias'].str.contains('рубль/евро') & \
                        ~table['Экономические показатели'].str.contains('Юралз')
            table.loc[condition, 'Экономические показатели'] = \
                table.loc[condition, 'Экономические показатели'] + ', €/руб'

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

                transformer.render_mpl_table(key_eco, 'key_eco', header_columns=0, col_width=4,
                                             title=title, alias=titles[i])
                png_path = '{}/img/{}_table.png'.format(path_to_source, 'key_eco')

                with open(png_path, "rb") as photo:
                    await __sent_photo_and_msg(message, photo, title="")

        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


# ['Курсы валют', 'курсы', 'валюты', 'рубль', 'доллар', 'юань', 'евро']
@dp.message_handler(commands=['fx'])
async def exchange_info(message: types.Message):
    """
    Вывод в чат информации по котировкам связанной с валютой и их курсом

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    return None
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.as_json()):
        png_path = '{}/img/{}_table.png'.format(path_to_source, 'exc')
        engine = create_engine(psql_engine)
        exc = pd.read_sql_query('SELECT * FROM exc', con=engine)
        exc['Курс'] = exc['Курс'].apply(lambda x: round(float(x), 2) if x is not None else x)

        transformer = dt.Transformer()
        for num, currency in enumerate(exc['Валюта'].values):
            if currency.lower() == 'usdollar':
                exc['Валюта'].values[num] = 'Индекс DXY'
            else:
                cur = currency.upper().split('-')
                exc['Валюта'].values[num] = '/'.join(cur).replace('CNY', 'CNH')
        exc = exc.sort_index().reset_index(drop=True)

        transformer.render_mpl_table(exc.round(2), 'exc', header_columns=0,
                                     col_width=2, title='Текущие курсы валют')
        day = pd.read_sql_query('SELECT * FROM "report_exc_day"', con=engine).values.tolist()
        month = pd.read_sql_query('SELECT * FROM "report_exc_mon"', con=engine).values.tolist()
        photo = open(png_path, 'rb')
        title = 'Курсы валют'
        data_source = 'investing.com'
        curdatetime = read_curdatetime()
        await __sent_photo_and_msg(message, photo, day, month, protect_content=False,
                                   title=sample_of_img_title.format(title, data_source, curdatetime))

        fx_predict = pd.read_excel('{}/tables/fx_predict.xlsx'.format(path_to_source)).rename(
            columns={'базовый сценарий': ' '})
        title = 'Прогноз валютных курсов'
        data_source = 'Sber analytical research'
        transformer.render_mpl_table(fx_predict, 'fx_predict', header_columns=0,
                                     col_width=1.5, title=title)
        png_path = '{}/img/{}_table.png'.format(path_to_source, 'fx_predict')
        photo = open(png_path, 'rb')
        await __sent_photo_and_msg(message, photo, title=sample_of_img_title.format(title, data_source, curdatetime))

        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


# ['Металлы', 'сырьевые товары', 'commodities']
@dp.message_handler(commands=['commodities'])
async def metal_info(message: types.Message):
    """
    Вывод в чат информации по котировкам связанной с сырьем (комодами)

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    return None
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.as_json()):
        transformer = dt.Transformer()
        engine = create_engine(psql_engine)
        metal = pd.read_sql_query('SELECT * FROM metals', con=engine)
        metal = metal[['Metals', 'Price', 'Weekly', 'Monthly', 'YoY']]
        metal = metal.rename(columns=({'Metals': 'Сырье', 'Price': 'Цена', 'Weekly': 'Δ Неделя',
                                       'Monthly': 'Δ Месяц', 'YoY': 'Δ Год'}))

        order = {'Медь': ['Медь', '$/т', '0'],
                 'Aluminum USD/T': ['Алюминий', '$/т', '1'],
                 'Nickel USD/T': ['Никель', '$/т', '2'],
                 'Lead USD/T': ['Cвинец', '$/т', '3'],
                 'Zinc USD/T': ['Цинк', '$/т', '4'],
                 'Gold USD/t,oz': ['Золото', '$/унц', '5'],
                 'Silver USD/t,oz': ['Cеребро', '$/унц', '6'],
                 'Palladium USD/t,oz': ['Палладий', '$/унц', '7'],
                 'Platinum USD/t,oz': ['Платина', '$/унц', '8'],
                 'Lithium CNY/T': ['Литий', 'CNH/т', '9'],
                 'Cobalt USD/T': ['Кобальт', '$/т', '10'],
                 'Iron Ore 62% fe USD/T': ['ЖРС (Китай)', '$/т', '11'],
                 'Эн. уголь': ['Эн. уголь\n(Au)', '$/т', '12'],
                 'кокс. уголь': ['Кокс. уголь\n(Au)', '$/т', '13']
                 }

        metal['ind'] = None
        metal.insert(1, 'Ед. изм.', None)
        for num, commodity in enumerate(metal['Сырье'].values):
            if commodity in order:
                metal.Сырье[metal.Сырье == commodity] = '<>'.join(order[commodity])
            else:
                metal.drop(num, inplace=True)
        metal[['Сырье', 'Ед. изм.', 'ind']] = metal['Сырье'].str.split('<>', expand=True)
        metal.set_index('ind', drop=True, inplace=True)
        metal.sort_index(inplace=True)
        metal = metal.replace(['', 'None', 'null'], [np.nan, np.nan, np.nan])
        for key in metal.columns[2:]:
            metal[key] = metal[key].apply(lambda x: str(x).replace(",", "."))
            metal[key] = metal[key].apply(lambda x: __replacer(x))
            metal[key] = metal[key].apply(lambda x: str(x).replace("s", ""))
            metal[key] = metal[key].apply(lambda x: str(x).replace("%", ""))
            metal[key] = metal[key].apply(lambda x: str(x).replace('–', '-'))

            metal[key] = metal[key].apply(lambda x: '{}'.format(np.nan) if str(x) == 'None' else '{}'.format(x))
            metal[key] = metal[key].astype('float')
            metal[key] = metal[key].round()
            metal[key] = metal[key].apply(lambda x: "{:,.0f}".format(x).replace(',', ' '))
            metal[key] = metal[key].apply(lambda x: '{}%'.format(x) if x != 'nan' and key != 'Цена'
            else str(x).replace("nan", "-"))

        metal.index = metal.index.astype('int')
        metal.sort_index(inplace=True)
        transformer.render_mpl_table(metal, 'metal', header_columns=0,
                                     col_width=1.5, title='Цены на ключевые сырьевые товары.')

        png_path = '{}/img/{}_table.png'.format(path_to_source, 'metal')
        day = pd.read_sql_query('SELECT * FROM "report_met_day"', con=engine).values.tolist()
        photo = open(png_path, 'rb')
        title = ' Сырьевые товары'
        data_source = 'LME, Bloomberg, investing.com'
        await __sent_photo_and_msg(message, photo, day, protect_content=False,
                                   title=sample_of_img_title.format(title, data_source, read_curdatetime()))

        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


def __replacer(data: str):
    """
    Если '.' больше чем 1 в числовом значении фин.показателя
    и первый объект равен 0, то форматируем так '{}.{}{}'(*data_list)

    :param data: Значение из ячейки таблицы с фин.показателями
    return Форматированный текст
    """
    data_list = data.split('.')
    if len(data_list) > 2:
        if data_list[0] == '0':
            return '{}.{}{}'.format(*data_list)
        else:
            return '{}{}.{}'.format(*data_list)
    return data


@dp.message_handler(commands=['sendtoall'])
async def message_to_all(message: types.Message):
    """
    Входная точка для ручной рассылки новостей на всех пользователей

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    return None
    """
    user_str = message.from_user.as_json()
    user = json.loads(message.from_user.as_json())
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(user_str):
        if await check_your_right(user):
            await Form.send_to_users.set()
            await message.answer('Сформируйте сообщение для всех пользователей в следующем своем сообщении\n'
                                 'или, если передумали, напишите слово "Отмена".')
            user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
        else:
            await message.answer('Недостаточно прав для этой команды!')
            user_logger.warning(f'*{chat_id}* {full_name} - {user_msg} : недостаточно прав для команды')
    else:
        await message.answer('Неавторизованный пользователь')
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


@dp.message_handler(state=Form.send_to_users, content_types=types.ContentTypes.ANY)
async def get_msg_from_admin(message, state: FSMContext):
    """
    Обработка сообщения и/или файла от пользователя и рассылка их на всех пользователей

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: конечный автомат о состоянии
    return None
    """
    if message.text and (message.text.strip().lower() == 'отмена'):
        await state.finish()
        await message.answer('Рассылка успешно отменена.')
        user_logger.info('Отмена действия - /sendtoall')
        return None
    message_jsn = json.loads(message.as_json())
    if 'text' in message_jsn:
        file_type = 'text'
        file_name = None
        msg = message.text
    elif 'document' in message_jsn:
        file_type = 'document'
        file_name = message.document.file_name
        msg = message.caption
        await message.document.download(destination_file='sources/{}'.format(file_name))
    elif 'photo' in message_jsn:
        file_type = 'photo'
        best_photo = message.photo[0]
        for photo_file in message.photo[1:]:
            if best_photo.file_size < photo_file.file_size:
                best_photo = photo_file
        file_name = best_photo.file_id
        await best_photo.download(destination_file='sources/{}.jpg'.format(file_name))
        msg = message.caption
    else:
        await state.finish()
        await message.answer('Отправка не удалась')
        return None

    await state.finish()
    engine = create_engine(psql_engine)
    users = pd.read_sql_query('SELECT * FROM whitelist', con=engine)
    users_ids = users['user_id'].tolist()
    for user_id in users_ids:
        await send_msg_to(user_id, msg, file_name, file_type)
        user_logger.debug(f'*{user_id}* Пользователю пришло сообщение от админа')

    await message.answer('Рассылка на {} пользователей успешно отправлена'.format(len(users_ids)))
    logger.info('Рассылка на {} пользователей успешно отправлена'.format(len(users_ids)))

    file_cleaner('sources/{}'.format(file_name))
    file_cleaner('sources/{}.jpg'.format(file_name))


async def send_msg_to(user_id, message_text, file_name, file_type):
    """
    Рассылка текста и/или файлов(документы и фотокарточки) на выбранного пользователя

    :param user_id: ID пользователя для которого будет произведена отправка
    :param message_text: Текст для отправки или подпись к файлу
    :param file_name: Текст содержащий в себе название сохраненного файла
    :param file_type: Тип файла для отправки. Может быть None, str("Document") и str("Picture")
    return None
    """
    if file_name:
        if file_type == 'photo':
            file = types.InputFile('sources/{}.jpg'.format(file_name))
            await bot.send_photo(photo=file, chat_id=user_id,
                                 caption=message_text, parse_mode='HTML', protect_content=True)
        elif file_type == 'document':
            file = types.InputFile('sources/{}'.format(file_name))
            await bot.send_document(document=file, chat_id=user_id,
                                    caption=message_text, parse_mode='HTML', protect_content=True)
    else:
        await bot.send_message(user_id, message_text, parse_mode='HTML', protect_content=True)


def file_cleaner(filename):
    """
    Удаление файла по относительному или абсолютному пути

    :param filename: Путь от исполняемого файла (если он не рядом) и имя файла для удаления
    return None
    """
    try:
        os.remove(filename)
    except OSError:
        pass


@dp.message_handler(commands=['addnewsubscriptions'])
async def add_new_subscriptions(message: types.Message):
    """
    Входная точка для добавления подписок на новостные объекты себе для получения новостей

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    return None
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    if await user_in_whitelist(message.from_user.as_json()):
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
        await Form.user_subscriptions.set()
        await message.answer('Сформируйте полный список интересующих клиентов или сырья для подписки на '
                             'пассивную отправку новостей по ним.\n'
                             'Перечислите их в одном сообщении каждую с новой строки.\n'
                             'Если передумали, то напишите "Отмена" в чат.')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')
        await message.answer('Вы не зарегистрированы в этом боте')


@dp.message_handler(state=Form.user_subscriptions)
async def set_user_subscriptions(message: types.Message, state: FSMContext):
    """
    Обработка сообщения от пользователя и запись известных объектов новостей в подписки

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: конечный автомат о состоянии
    return None
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    if message.text.strip().lower() == 'отмена':
        user_logger.info('Отмена действия - /addnewsubscriptions')
        await state.finish()
        await message.answer('Изменение списка подписок успешно отменено.')
        return None
    await state.finish()
    subscriptions = []
    quotes = ['\"', '«', '»']

    engine = create_engine(psql_engine)
    user_id = json.loads(message.from_user.as_json())['id']
    com_df = pd.read_sql_query('SELECT * FROM "client_alternative"', con=engine)
    client_df = pd.read_sql_query('SELECT * FROM "commodity_alternative"', con=engine)
    df_all = pd.concat([client_df['other_names'], com_df['other_names']], ignore_index=True, sort=False).fillna('-')
    df_all = pd.DataFrame(df_all)  # pandas.core.series.Series -> pandas.core.frame.DataFrame

    message_text = message.text
    for quote in quotes:
        message_text = message_text.replace(quote, '')
    user_request = [i.strip().lower() for i in message_text.split('\n')]

    for subscription in user_request:
        for index, row in df_all.iterrows():
            # if subscription in row.split(';') - из-за разрядности такой вариант не всегда находит совпадение
            for other_name in row['other_names'].split(';'):
                if subscription == other_name:
                    subscriptions.append(other_name)

    if (len(subscriptions) < len(user_request)) and subscriptions:
        list_of_unknown = f'{", ".join(list(set(user_request) - set(subscriptions)))}'
        user_logger.debug(f'*{user_id}* Запросил неизвестные новостные объекты на подписку: {list_of_unknown}')
        await message.reply(f'{list_of_unknown} - Эти объекты новостей нам неизвестны')
    if subscriptions:
        subscriptions = ", ".join(subscriptions)
        with engine.connect() as conn:
            conn.execute(text(f"UPDATE whitelist SET subscriptions = '{subscriptions}' WHERE user_id = '{user_id}'"))
            conn.commit()
        await message.reply(f'{subscriptions} \n\nВаш новый список подписок')
        user_logger.info(f'*{user_id}* Подписался на : {subscriptions}')
    else:
        await message.reply('Перечисленные выше объекты не были найдены')
        user_logger.info(f'Для пользователя *{user_id}* запрошенные объекты не были найдены')


@dp.message_handler(commands=['myactivesubscriptions'])
async def get_user_subscriptions(message: types.Message):
    """
    Получение сообщением информации о своих подписках

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    return None
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    user_id = json.loads(message.from_user.as_json())['id']  # Get user_ID from message
    engine = create_engine(psql_engine)
    subscriptions = pd.read_sql_query(f"SELECT subscriptions FROM whitelist WHERE user_id = '{user_id}'",
                                      con=engine)['subscriptions'].values.tolist()
    if not subscriptions:
        keyboard = types.ReplyKeyboardRemove()
        msg_txt = 'Нет активных подписок'
        user_logger.info(f'Пользователь *{chat_id}* запросил список своих подписок - но их нет')
    else:
        buttons = []
        for subscription in subscriptions[0].split(', '):
            buttons.append([types.KeyboardButton(text=subscription)])
        msg_txt = 'Выберите подписку'
        keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True,
                                             input_field_placeholder=msg_txt)
    await message.answer(msg_txt, reply_markup=keyboard)


async def user_in_whitelist(user: str):
    """
    Проверка, пользователя на наличие в списках на доступ

    :param user: Строковое значение по пользователю в формате json. message.from_user.as_json()
    return Булево значение на наличие пользователя в списке
    """
    user_json = json.loads(user)
    user_id = user_json['id']
    engine = create_engine(psql_engine)
    whitelist = pd.read_sql_query('SELECT * FROM "whitelist"', con=engine)
    if len(whitelist.loc[whitelist['user_id'] == user_id]) >= 1:
        return True
    else:
        return False


@dp.message_handler(commands=['addmetowhitelist'])
async def user_to_whitelist(message: types.Message):
    """
    Добавление нового пользователя в список на доступ

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    return None
    """
    user_raw = json.loads(message.from_user.as_json())
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if not await user_in_whitelist(message.from_user.as_json()):
        if 'username' in user_raw:
            user_username = user_raw['username']
        else:
            user_username = 'Empty_username'
        user_id = user_raw['id']
        user = pd.DataFrame([[user_id, user_username, full_name, 'user', 'active', None]],
                            columns=['user_id', 'username', 'full_name', 'user_type', 'user_status', 'subscriptions'])
        try:
            engine = create_engine(psql_engine)
            user.to_sql('whitelist', if_exists='append', index=False, con=engine)
            await message.answer(f'Добро пожаловать, {full_name}!', protect_content=False)
            user_logger.info(f"*{chat_id}* {full_name} - {user_msg}: новый пользователь")
        except Exception as e:
            await message.answer(f'Во время авторизации произошла ошибка, попробуйте позже. '
                                 f'\n\n{e}', protect_content=False)
            user_logger.critical(f'*{chat_id}* {full_name} - {user_msg} : ошибка авторизации ({e})')
    else:
        await message.answer(f'{full_name}, Вы уже наш пользователь!', protect_content=False)
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}: уже добавлен')


async def check_your_right(user: dict):
    """
    Проверка прав пользователя

    :param user: Словарь с информацией о пользователе
    return Булевое значение на наличие прав администратора и выше
    """
    user_id = user['id']
    engine = create_engine(config.psql_engine)
    user_series = pd.read_sql_query(f"SELECT user_type FROM whitelist WHERE user_id='{user_id}'", con=engine)
    user_type = user_series.values.tolist()[0][0]
    if user_type == 'admin' or user_type == 'owner':
        return True
    else:
        return False


async def __create_fin_table(message, client_name, client_fin_table):
    """
    Формирование таблицы под финансовые показатели и запись его изображения

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param client_name: Наименование клиента финансовых показателей
    :param client_fin_table: Таблица финансовых показателей
    return None
    """
    transformer = dt.Transformer()
    client_fin_table = client_fin_table.rename(columns={'name': 'Финансовые показатели'})
    transformer.render_mpl_table(client_fin_table,
                                 'financial_indicator', header_columns=0, col_width=4, title='',
                                 alias=client_name.strip().upper(), fin=True)
    png_path = '{}/img/{}_table.png'.format(path_to_source, 'financial_indicator')
    with open(png_path, "rb") as photo:
        await bot.send_photo(message.chat.id, photo, caption='', parse_mode='HTML', protect_content=True)


@dp.message_handler(commands=['admin_help'])
async def admin_help(message: types.Message):
    """
    Вывод в чат подсказки по командам для администратора

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    return None
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    user = json.loads(message.from_user.as_json())
    admin_flag = await check_your_right(user)

    if admin_flag:
        # TODO: '<b>/analyse_bad_article</b> - показать возможные нерелевантные новости\n'
        help_msg = ('<b>/show_article</b> - показать детальную информацию о новости\n'
                    '<b>/change_summary</b> - поменять саммари новости с помощью LLM\n'
                    '<b>/delete_article</b> - удалить новость из базы данных\n'
                    '<b>/sendtoall</b> - Сделать рассылку сообщения на всех пользователей бота')
        await message.answer(help_msg, protect_content=False, parse_mode='HTML')
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        await message.answer('У Вас недостаточно прав для использования данной команды.', protect_content=False)
        user_logger.warning(f'*{chat_id}* {full_name} - {user_msg} : недостаточно прав для команды')


@dp.message_handler(commands=['show_article'])
async def show_article(message: types.Message):
    """
    Вывод в чат новости по ссылке

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    return None
    """
    await types.ChatActions.typing()
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    user = json.loads(message.from_user.as_json())
    admin_flag = await check_your_right(user)

    if admin_flag:
        ask_link = 'Вставьте ссылку на новость, которую хотите получить.'
        await Form.link.set()
        await bot.send_message(chat_id=message.chat.id, text=ask_link, parse_mode='HTML',
                               protect_content=False, disable_web_page_preview=True)
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        await message.answer('У Вас недостаточно прав для использования данной команды.', protect_content=False)
        user_logger.warning(f'*{chat_id}* {full_name} - {user_msg} : недостаточно прав для команды')


@dp.message_handler(state=Form.link)
async def continue_show_article(message: types.Message, state: FSMContext):
    """
    Вывод новости по ссылке от пользователя

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: конечный автомат о состоянии
    return None
    """
    await types.ChatActions.typing()
    await state.update_data(link=message.text)
    data = await state.get_data()

    apd_obj = ArticleProcessAdmin()
    full_text, old_text_sum = apd_obj.get_article_text_by_link(data['link'])
    if not full_text:
        await message.answer('Извините, не могу найти новость. Попробуйте в другой раз.', protect_content=False)
        await state.finish()
        user_logger.warning(f"/show_article : не получилось найти новость по ссылке {data['link']}")
        return

    data_article_dict = apd_obj.get_article_by_link(data['link'])
    if not isinstance(data_article_dict, dict):
        await message.answer(f'Извините, произошла ошибка: {data_article_dict}.\nПопробуйте в другой раз.',
                             protect_content=False)
        user_logger.critical(f'/show_article : {data_article_dict}')
        return

    format_msg = ''
    for key, val in data_article_dict.items():
        format_msg += f'<b>{key}</b>: {val}\n'

    await message.answer(format_msg, parse_mode='HTML', protect_content=False, disable_web_page_preview=True)
    await state.finish()


@dp.message_handler(commands=['change_summary'])
async def change_summary(message: types.Message):
    """
    Получение ссылки на новость для изменения ее короткой версии

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    return None
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if not config.api_key_gpt:
        await message.answer('Данная команда пока недоступна.', protect_content=False)
        user_logger.critical('Нет токена доступа к chatGPT')
        return

    await types.ChatActions.typing()

    user = json.loads(message.from_user.as_json())
    admin_flag = await check_your_right(user)

    if admin_flag:
        ask_link = 'Вставьте ссылку на новость, которую хотите изменить.'
        await Form.link_change_summary.set()
        await bot.send_message(chat_id=message.chat.id, text=ask_link, parse_mode='HTML',
                               protect_content=False, disable_web_page_preview=True)
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        await message.answer('У Вас недостаточно прав для использования данной команды.', protect_content=False)
        user_logger.warning(f'*{chat_id}* {full_name} - {user_msg} : недостаточно прав для команды')


@dp.message_handler(state=Form.link_change_summary)
async def continue_change_summary(message: types.Message, state: FSMContext):
    """
    Изменение краткой версии новости

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: конечный автомат о состоянии
    return None
    """
    await state.update_data(link_change_summary=message.text)
    data = await state.get_data()
    await state.finish()

    apd_obj = ArticleProcessAdmin()
    full_text, old_text_sum = apd_obj.get_article_text_by_link(data['link_change_summary'])

    if not full_text:
        await message.answer('Извините, не могу найти новость. Попробуйте в другой раз.', protect_content=False)
        user_logger.warning(f"/change_summary : не получилось найти новость по ссылке - {data['link_change_summary']}")
        return

    await message.answer('Создание саммари может занять некоторое время. Ожидайте.', protect_content=False)
    await types.ChatActions.typing()

    try:
        new_text_sum = summarization_by_chatgpt(full_text)
        apd_obj.insert_new_gpt_summary(new_text_sum, data['link_change_summary'])
        await message.answer(f"<b>Старое саммари:</b> {old_text_sum}", parse_mode='HTML', protect_content=False)

    except MessageIsTooLong:
        await message.answer(f"<b>Старое саммари не помещается в одно сообщение.</b>", parse_mode='HTML')
        user_logger.critical(f"/change_summary : старое саммари оказалось слишком длинным "
                             f"({data['link_change_summary']}\n{old_text_sum})")

    except:
        user_logger.critical(f'/change_summary : ошибка при создании саммари с помощью chatGPT')
        await message.answer('Произошла ошибка при создании саммари. Разработчики уже решают проблему.',
                             protect_content=False)

    else:
        await message.answer(f"<b>Новое саммари:</b> {new_text_sum}", parse_mode='HTML', protect_content=False)


# TODO: Убрать проверку удаления новости
@dp.message_handler(commands=['delete_article'])
async def delete_article(message: types.Message):
    """
    Получение ссылки на новость от пользователя для ее удаления

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    return None
    """
    await types.ChatActions.typing()
    user = json.loads(message.from_user.as_json())
    admin_flag = await check_your_right(user)

    if admin_flag:
        ask_link = 'Вставьте ссылку на новость, которую хотите удалить.'
        await Form.link_to_delete.set()
        await bot.send_message(chat_id=message.chat.id, text=ask_link, parse_mode='HTML',
                               protect_content=False, disable_web_page_preview=True)
    else:
        await message.answer('У Вас недостаточно прав для использования данной команды.', protect_content=False)


@dp.message_handler(state=Form.link_to_delete)
async def continue_delete_article(message: types.Message, state: FSMContext):
    """
    Проверка, что действие по удалению новости не случайное

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: конечный автомат о состоянии
    return None
    """
    await types.ChatActions.typing()
    await state.update_data(link_to_delete=message.text)
    data = await state.get_data()

    apd_obj = ArticleProcessAdmin()
    full_text, old_text_sum = apd_obj.get_article_text_by_link(data['link_to_delete'])
    if not full_text:
        await message.answer('Извините, не могу найти новость. Попробуйте в другой раз.', protect_content=False)
        await state.finish()
        return
    else:
        permission_answer = f'Вы уверены, что хотите удалить данную новость ?\nЕсли да, то напишите: "Удалить новость".'
        await Form.permission_to_delete.set()
        await message.reply(permission_answer, protect_content=False)


@dp.message_handler(state=Form.permission_to_delete)
async def finish_delete_article(message: types.Message, state: FSMContext):
    """
    Удаление новости

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: конечный автомат о состоянии
    return None
    """
    await types.ChatActions.typing()
    await state.update_data(permission_to_delete=message.text)
    data = await state.get_data()

    apd_obj = ArticleProcessAdmin()
    if data["permission_to_delete"].lower().strip().replace('"', '').replace('.', '') == 'удалить новость':
        apd_obj.delete_article_by_link(data['link_to_delete'])
        await message.answer('Новость удалена.', protect_content=False)
    else:
        await message.answer('Хорошо, удалим в следующий раз.', protect_content=False)

    await state.finish()


@dp.callback_query_handler(text='next_5_news')
async def send_next_five_news(call: types.CallbackQuery):
    """
    Вывод 5 новостей пользователю в чат

    :param call: Объект(сообщение) для ответа
    return None
    """
    try:
        await call.message.answer(articles_l5, parse_mode='HTML',
                                  protect_content=False, disable_web_page_preview=True)
    except MessageIsTooLong:
        articles = articles_l5.split('\n\n')
        for article in articles:
            await call.message.answer(article, parse_mode='HTML',
                                      protect_content=False, disable_web_page_preview=True)
    finally:
        await call.message.edit_reply_markup()


async def show_client_fin_table(message: types.Message, s_id: int, msg_text: str, ap_obj: ArticleProcess) -> bool:
    """
    Вывод таблицы с финансовыми показателями в виде фотокарточки

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param s_id: ID клиента или комоды
    :param msg_text: Текст сообщения
    :param ap_obj: экземпляр класса ArticleProcess
    return Булевое значение об успешности создания таблицы
    """
    client_name, client_fin_table = ap_obj.get_client_fin_indicators(s_id, msg_text.strip().lower())
    if not client_fin_table.empty:
        await types.ChatActions.upload_photo()
        await __create_fin_table(message, client_name, client_fin_table)
        return True
    else:
        return False


@dp.message_handler(commands=['dailynews'])
async def dailynews(message: types.Message):
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    user_logger.critical(f'*{chat_id}* {full_name} - {user_msg}. МЕТОД НЕ РАЗРЕШЕН!')
    await send_daily_news(20, 20, 20, 1)


@dp.message_handler(commands=['newsletter'])
async def show_newsletter_buttons(message: types.Message):
    """ Отображает кнопки с доступными рассылками """

    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.as_json()):
        newsletter_dict = dt.Newsletter.get_newsletter_dict()  # {тип рассылки: заголовок рассылки}
        callback_func = 'send_newsletter_by_button'  # функция по отображению рассылки

        keyboard = types.InlineKeyboardMarkup()
        for type_, title in newsletter_dict.items():
            callback = f'{callback_func}:{type_}'
            keyboard.add(types.InlineKeyboardButton(text=title, callback_data=callback))

        await message.answer("Какую информацию вы хотите получить?", reply_markup=keyboard)

        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


@dp.callback_query_handler(lambda c: c.data.startswith('send_newsletter_by_button'))
async def send_newsletter_by_button(callback_query: types.CallbackQuery):
    """ Отправляет рассылку по кнопке """
    # получаем данные
    newsletter_type = callback_query.data.split(':')[1]
    data_callback = dict(callback_query.values['from'])

    # получаем текст рассылки
    if newsletter_type == 'weekly_result':
        title, newsletter, img_path_list = dt.Newsletter.make_weekly_result()
    elif newsletter_type == 'weekly_event':
        title, newsletter, img_path_list = dt.Newsletter.make_weekly_event()
    else:
        return

    await types.ChatActions.typing()
    media = types.MediaGroup()
    for path in img_path_list:
        media.attach_photo(types.InputFile(path))
    await bot.send_message(data_callback['id'], text=newsletter, parse_mode='HTML', protect_content=True)
    await bot.send_media_group(data_callback['id'], media=media, protect_content=True)
    user_logger.debug(f'*{data_callback["id"]}* Пользователю пришла рассылка "{title}" по кнопке')


@dp.message_handler()
async def giga_ask(message: types.Message, prompt: str = '', return_ans: bool = False):
    """ Обработка пользовательского сообщения """

    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    msg = '{} {}'.format(prompt, message.text)
    msg = msg.replace('/bonds', '')
    msg = msg.replace('/eco', '')
    msg = msg.replace('/commodities', '')
    msg = msg.replace('/fx', '')

    if await user_in_whitelist(message.from_user.as_json()):
        await types.ChatActions.typing()
        ap_obj = ArticleProcess(logger)
        msg_text = message.text.replace('«', '"').replace('»', '"')
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')

        # проверка пользовательского сообщения на запрос новостей по отраслям
        subject_ids, subject = ap_obj.find_subject_id(msg_text, 'industry'), 'industry'
        if subject_ids:
            industry_id = subject_ids[0]
            not_use, reply_msg, not_use_ = ap_obj.process_user_alias(industry_id, subject)
            try:
                await message.answer(reply_msg, parse_mode='HTML', protect_content=False, disable_web_page_preview=True)
            except MessageIsTooLong:
                articles = reply_msg.split('\n\n')
                for article in articles:
                    await message.answer(article, parse_mode='HTML', protect_content=False, disable_web_page_preview=True)
            return

        # проверка пользовательского сообщения на запрос новостей по клиентам/товарам
        subject_ids, subject = ap_obj.find_subject_id(msg_text, 'client'), 'client'
        if not subject_ids:
            subject_ids, subject = ap_obj.find_subject_id(msg_text, 'commodity'), 'commodity'

        for subject_id in subject_ids:
            com_price, reply_msg, img_name_list = ap_obj.process_user_alias(subject_id, subject)

            return_ans = await show_client_fin_table(message, subject_id, '', ap_obj)

            if reply_msg:

                if img_name_list:
                    await types.ChatActions.upload_photo()
                    media = types.MediaGroup()
                    for name in img_name_list:
                        media.attach_photo(types.InputFile(PATH_TO_COMMODITY_GRAPH.format(name)))
                    await bot.send_media_group(message.chat.id, media=media, protect_content=False)

                if com_price:
                    await message.answer(com_price, parse_mode='HTML', protect_content=False,
                                         disable_web_page_preview=True)

                if isinstance(reply_msg, str):
                    global articles_l5
                    articles_all = reply_msg.split('\n\n', 6)
                    if len(articles_all) > 5:
                        articles_f5 = '\n\n'.join(articles_all[:6])
                        articles_l5 = articles_all[-1]
                        keyboard = types.InlineKeyboardMarkup()
                        keyboard.add(types.InlineKeyboardButton(text='Еще новости', callback_data='next_5_news'))
                    else:
                        articles_f5 = reply_msg
                        keyboard = None

                    try:
                        await message.answer(articles_f5, parse_mode='HTML', protect_content=False,
                                             disable_web_page_preview=True, reply_markup=keyboard)
                    except MessageIsTooLong:
                        articles = articles_f5.split('\n\n')
                        for article in articles:
                            if len(article) < 4050:
                                await message.answer(article, parse_mode='HTML', protect_content=False,
                                                     disable_web_page_preview=True)
                            else:
                                logger.error(f"MessageIsTooLong ERROR: {article}")

                return_ans = True

        if not return_ans:
            return_ans = await show_client_fin_table(message, 0, msg_text, ap_obj)

        if not return_ans:
            await types.ChatActions.typing()
            global chat
            global token
            aliases_dict = {
                **{alias: bonds_info for alias in bonds_aliases},
                **{alias: economy_info for alias in eco_aliases},
                **{alias: metal_info for alias in metal_aliases},
                **{alias: exchange_info for alias in exchange_aliases},
                **{alias: data_mart for alias in view_aliases}
            }
            message_text = message.text.lower().strip()
            function_to_call = aliases_dict.get(message_text)
            if function_to_call:
                await function_to_call(message)
            else:
                try:
                    giga_answer = chat.ask_giga_chat(token=token, text=msg)
                    giga_js = giga_answer.json()['choices'][0]['message']['content']
                except AttributeError:
                    chat = gig.GigaChat()
                    token = chat.get_user_token()
                    logger.debug(f'*{chat_id}* {full_name} : перевыпуск токена для общения с GigaChat')
                    giga_answer = chat.ask_giga_chat(token=token, text=msg)
                    giga_js = giga_answer.json()['choices'][0]['message']['content']
                except KeyError:
                    giga_answer = chat.ask_giga_chat(token=token, text=msg)
                    giga_js = giga_answer.json()
                    user_logger.critical(f'*{chat_id}* {full_name} - {user_msg} :'
                                         f' KeyError (некорректная выдача ответа GigaChat)')

                response = '{}\n\n{}'.format(giga_js, giga_ans_footer)
                await message.answer(response, protect_content=False)
                user_logger.debug(f'*{chat_id}* {full_name} - "{user_msg}" : На запрос GigaChat ответил: "{giga_js}"')

    else:
        await message.answer('Неавторизованный пользователь. Отказано в доступе.', protect_content=False)
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


async def get_waiting_time(weekday_to_send: int, hour_to_send: int, minute_to_send: int = 0):
    """
    Рассчитываем время ожидания перед отправкой рассылки

    :param weekday_to_send: день недели, в который нужно отправить рассылку
    :param hour_to_send: час, в который нужно отправить рассылку
    :param minute_to_send: минуты, в которые нужно отправить рассылку
    return время ожидания перед рассылкой
    """

    # получаем текущее датувремя и день недели
    current_datetime = datetime.now()
    current_weekday = current_datetime.isoweekday()

    # рассчитываем разницу до дня недели, в который нужно отправить рассылку
    days_until_sending = (weekday_to_send - current_weekday + 7) % 7

    # определяем следующую дату рассылки
    datetime_ = datetime(current_datetime.year, current_datetime.month,
                         current_datetime.day, hour_to_send, minute_to_send)
    datetime_for_sending = datetime_ + timedelta(days=days_until_sending)

    # добавляем неделю, если дата прошла
    if datetime_for_sending <= current_datetime:
        datetime_for_sending += timedelta(weeks=1)

    # определяем время ожидания
    time_to_wait = datetime_for_sending - current_datetime

    return time_to_wait


async def send_newsletter(newsletter_data: Dict):
    """  Отправляет рассылку  """

    newsletter_type, sending_weekday, sending_hour, sending_minute = tuple(newsletter_data.values())

    # ждем наступления нужной даты
    time_to_wait = await get_waiting_time(sending_weekday, sending_hour, sending_minute)
    await asyncio.sleep(time_to_wait.total_seconds())

    # получаем текст рассылки
    if newsletter_type == 'weekly_result':
        title, newsletter, img_path_list = dt.Newsletter.make_weekly_result()
    elif newsletter_type == 'weekly_event':
        title, newsletter, img_path_list = dt.Newsletter.make_weekly_event()
    else:
        return

    # отправляем пользователям
    engine = create_engine(psql_engine)
    with engine.connect() as conn:
        users_data = conn.execute(text('SELECT user_id, username FROM whitelist')).fetchall()
    for user_data in users_data:
        user_id, user_name = user_data[0], user_data[1]
        media = types.MediaGroup()
        for path in img_path_list:
            media.attach_photo(types.InputFile(path))
        await bot.send_message(user_id, text=newsletter, parse_mode='HTML', protect_content=True)
        await bot.send_media_group(user_id, media=media, protect_content=True)
        user_logger.debug(f'*{user_id}* Пользователю {user_name} пришла рассылка "{title}"')

    logger.info(f'{len(users_data)} пользователям пришла рассылка "{title}"')

    await asyncio.sleep(100)
    return await send_newsletter(newsletter_data)


def translate_subscriptions_to_object_id(CAI_dict: dict, subscriptions: list):
    """
    Получает id объектов (клиента/комоды/отрасли) по названиям объектов из подписок пользователя

    :param CAI_dict: Словарь объектов {ObjectType_ObjectID: [Object_Names], ...}
    :param subscriptions: Список подписок пользователя. Могут быть как названия, так и альтернативные названия
    return Список id объектов
    """
    return [key for word in subscriptions for key in CAI_dict if word in CAI_dict[key]]


async def news_prep(subject_ids: list, news: pd.DataFrame, subject_type: str):
    """
    Подготовка новостей для отправки их пользователю.
    Включает в себя: получение id новостей и разделение на блоки по темам

    :param subject_ids: Список id интересных пользователю
    :param news: Дата Фрейм с новостями за период времени
    :param subject_type: Тип новости по направлению (клиенты/комоды/отрасли).
    Может иметь 3 значения: 'client', 'commodity', *'industry' текст должен быть обязательно в нижнем регистре
    return Список Дата Фраймов, где каждый ДФ относится к одной конкретной теме.
    """
    requested_news_id = [int(news.split('_')[1]) for news in subject_ids if news.split('_')[0] == subject_type]

    # Получить список новостей по id объекту
    news_sorted = news.loc[news['{}_id'.format(subject_type)].isin(requested_news_id)]

    # Разбить список новостей на блоки по объекту
    news_splitted = [part for _, part in news_sorted.groupby(news_sorted['{}_id'.format(subject_type)])]
    return news_splitted


async def newsletter_scheduler(time_to_wait: int = 0, first_time_to_send: int = 37800, last_time_to_send: int = 61200):
    """
    Функция для расчета времени ожидания

    :param time_to_wait: Параметр для пропуска ожидания. Для пропуска можно передать любое int значение кроме 0
    :param first_time_to_send: Время для отправки первой рассылки. Время в секундах. Default = 37800  # 10:30
    :param last_time_to_send: Время для отправки последней рассылки. Время в секундах. Default = 61200  # 17:00
    return None
    """
    if time_to_wait != 0:
        user_logger.critical(f'Ручная рассылка')
        return None
    end_of_the_day = 86400  # 86400(всего секунд)/3600(секунд в одном часе) = 24 (00:00 или 24:00)
    current_day = datetime.now()
    current_hour = current_day.hour
    current_minute = current_day.minute
    current_sec = current_day.second

    current_time = (current_hour * 3600) + (current_minute * 60) + current_sec  # Настоящее Время в секундах
    if first_time_to_send <= current_time <= last_time_to_send:
        time_to_wait = last_time_to_send - current_time
        next_send_time = str(timedelta(seconds=last_time_to_send))
    elif current_time > last_time_to_send:
        time_to_wait = (end_of_the_day - current_time) + first_time_to_send
        next_send_time = str(timedelta(seconds=first_time_to_send))
    elif first_time_to_send > current_time:
        time_to_wait = (first_time_to_send - current_time)
        next_send_time = str(timedelta(seconds=first_time_to_send))

    user_logger.info(f'В ожидании рассылки в {next_send_time}.'
                     f' До следующей отправки: {str(timedelta(seconds=time_to_wait))}')
    await asyncio.sleep(time_to_wait)
    return None


# TODO: Добавить синхронизацию времени с методом на ожидание (newsletter_scheduler)
# TODO: Учитывать, что временные интервалы могут быть не равны между first.start -> first.last -> second.first
async def send_daily_news(client_hours: int = 7, commodity_hours: int = 7, industry_hours: int = 7, schedule: int = 0):
    """
    Рассылка новостей по часам и выбранным темам (объектам новостей: клиенты/комоды/отрасли)

    :param client_hours: За какой период нужны новости по клиентам
    :param commodity_hours: За какой период нужны новости по комодам
    :param industry_hours: За какой период нужны новости по отраслям
    :param schedule: Запуск без ожидания
    return None
    """
    await newsletter_scheduler(schedule)  # Ожидание рассылки
    user_logger.info(f'Начинается ежедневная рассылка новостей по подпискам...')
    row_number = 0
    ap_obj = ArticleProcess(logger)
    engine = create_engine(psql_engine)
    # Словарь новостных объектов {тип_id: [альтернатив. названия], ...}
    CAI_dict = ap_obj.get_client_comm_industry_dictionary()
    clients_news = ap_obj.get_news_by_time(client_hours, 'client')
    commodity_news = ap_obj.get_news_by_time(commodity_hours, 'commodity')
    # db_df_all = pd.DataFrame(pd.concat([clients_news, commodity_news]))
    # TODO: Добавить в обработку industry
    # db_df_all.sort_values(by='date', ascending=False, inplace=True)
    users = pd.read_sql_query('SELECT user_id, username, subscriptions FROM whitelist '
                              'WHERE subscriptions IS NOT NULL', con=engine)
    for index, user in users.iterrows():
        row_number += 1
        user_id = user['user_id']
        user_name = user['username']
        subscriptions = user['subscriptions'].split(', ')
        # translate_subscriptions_to_id(CAI_dict, subscriptions)
        user_logger.debug(f'Отправка подписок для: {user_name}({user_id}). {row_number}/{users.shape[0]}')
        # print(f'Отправка подписок для: {user_name}({user_id}). {row_number}/{users.shape[0]}')

        # Получить список интересующих id объектов
        user_logger.debug(f'Подготовка новостей для отправки их пользователю {user_name}({user_id})')
        news_id = translate_subscriptions_to_object_id(CAI_dict, subscriptions)
        news_client_splited = await news_prep(news_id, clients_news, 'client')
        news_comm_splited = await news_prep(news_id, commodity_news, 'commodity')
        if news_client_splited or news_comm_splited:
            try:
                await bot.send_message(user_id, text='Ваша новостная подборка по подпискам:',
                                       parse_mode='HTML', protect_content=True)
            except ChatNotFound:
                user_logger.error(f'Чата с пользователем {user_id} {user_name} - не существует')
                # print(f'Чата с пользователем {user_id} {user_name} - не существует')
                continue
        else:
            user_logger.info(f'Нет новых новостей по подпискам для: {user_name}({user_id})')
            # print(f'Нет новых новостей по подпискам для: {user_name}({user_id})')
        # Вывести новости пользователю по клиентам и комодам
        for news in (news_client_splited, news_comm_splited):
            for news_block in news:
                message_block = f"<b>{news_block['name'].values.tolist()[0]}</b>\n\n".upper()
                for df_index, row in news_block.head(20).iterrows():
                    base_url = urlparse(row['link']).netloc.split('www.')[-1]  # Базовая ссылка на источник
                    message_block += sample_of_news_title.format(row['title'], row['link'], base_url)
                await bot.send_message(user_id, text=message_block, parse_mode='HTML',
                                       protect_content=False, disable_web_page_preview=True)
        user_logger.debug(f"({user_id}){user_name} - получил свои подписки ({subscriptions})")
        # print(f"({user_id}){user_name} - получил свои подписки ({subscriptions})")
    user_logger.info('Рассылка успешно завершена. Все пользователи получили свои новости. '
                     '\nПереходим в ожидание следующей рассылки.')
    # print('Рассылка успешно завершена. Все пользователи получили свои новости. '
    #       '\nПереходим в ожидание следующей рассылки.')
    await asyncio.sleep(100)
    return await send_daily_news(client_hours, commodity_hours, industry_hours)


if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    # инициализируем обработчик и логгер
    handler = get_handler(psql_engine)
    user_logger = get_db_logger(Path(__file__).stem, handler)  # логгер для сохранения пользовательских действий
    logger = selector_logger(Path(__file__).stem, 20)  # логгер для сохранения действий программы + пользователей

    # запускам рассылки
    loop = asyncio.get_event_loop()
    loop.create_task(send_newsletter(dict(name='weekly_result', weekday=5, hour=18, minute=0)))
    loop.create_task(send_newsletter(dict(name='weekly_event', weekday=1, hour=10, minute=30)))
    loop.create_task(send_daily_news())

    # запускаем бота
    executor.start_polling(dp, skip_updates=True)
