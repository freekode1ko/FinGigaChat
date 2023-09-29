import json
import datetime
import warnings
import re
import numpy as np

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import MessageIsTooLong
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from sqlalchemy import create_engine
import pandas as pd
import ast

import module.data_transformer as dt
import module.gigachat as gig
from module.model_pipe import summarization_by_chatgpt
from module.article_process import ArticleProcess, ArticleProcessAdmin
import config

path_to_source = config.path_to_source
API_TOKEN = config.api_token
psql_engine = config.psql_engine
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

# analysis_text = pd.read_excel('{}/tables/text.xlsx'.format(path_to_source), sheet_name=None)
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


def read_curdatetime():
    with open('sources/tables/time.txt', 'r') as f:
        curdatetime = f.read()
    return curdatetime


async def __text_splitter(message: types.Message, text: str, name: str, date: str, batch_size: int = 2048):
    text_group = []
    # import dateutil.parser as dparser
    # date = dparser.parse(date, fuzzy=True)
    # print(date)

    # uncommet me if need summory #TODO: исправить порядок парметров и промпт
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
                               month: str = '', title: str = '', source: str = ''):
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
    await bot.send_photo(message.chat.id, photo, caption=title, parse_mode='HTML', protect_content=True)

''' deprecated
async def __read_tables_from_companies(message: types.Message, companies: dict):
    company = companies['head'].loc[companies['head']['Name'].str.lower() == message.text.lower()].values.tolist()
    company_name = company[0][2]
    print(company_name)
    company_url = company[0][3]
    transformer = dt.Transformer()
    await message.reply("Ссылка на архивы с результатами:\n{}".format(company_url), protect_content=True)
    await message.answer('Табличные данные по показателям:', protect_content=True)

    for key in companies.keys():
        if str(company_name) in key:
            png_path = '{}/img/{}_table.png'.format(path_to_source, key)
            title = '{}'.format(key.split('_')[1])
            # transformer.save_df_as_png(df=companies[key].drop('Unnamed: 0', axis=1),
            #                            column_width=[0.15] * len(companies[key].columns),
            #                            figure_size=(15, 1.5), path_to_source=path_to_source, name=key)
            transformer.render_mpl_table(companies[key].drop('Unnamed: 0', axis=1), key,
                                         header_columns=0, col_width=2)
            photo = open(png_path, 'rb')
            await __sent_photo_and_msg(message, photo, title=title)
'''


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    global chat
    global token
    if await user_in_whitelist(message.from_user.as_json()):
        chat = gig.GigaChat()
        token = chat.get_user_token()
        print('{}...{} - {}({})'.format(token[:10], token[-10:],
                                        message.from_user.full_name,
                                        message.from_user.username))
        await message.reply("Давай я спрошу GigaChat за тебя", protect_content=True)

''' deprecated
@dp.message_handler(commands=['companies'])
async def company_info(message: types.Message):
    print('{} - {}'.format(message.from_user.full_name, message.text))
    if await user_in_whitelist(message.from_user.as_json()):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ['Полиметалл', 'ММК', 'Норникель', 'Полюс', 'Русал', 'Северсталь']
        keyboard.add(*buttons)
        await message.reply("Выберите компанию для детальной информации по ней", reply_markup=keyboard,
                            protect_content=True)

@dp.message_handler(lambda message: message.text.lower() in ["полиметалл", 'ммк', 'норникель',
                                                             'полюс', 'русал', 'северсталь'])
async def button_polymetal(message: types.Message):
    print('{} - {}'.format(message.from_user.full_name, message.text))
    if await user_in_whitelist(message.from_user.as_json()):
        companies = pd.read_excel('{}/tables/companies.xlsx'.format(path_to_source), sheet_name=None)
        await __read_tables_from_companies(message, companies)
'''


# ['облигации', 'бонды', 'офз']
@dp.message_handler(commands=['bonds'])
async def bonds_info(message: types.Message):
    print('{} - {}'.format(message.from_user.full_name, message.text))
    if await user_in_whitelist(message.from_user.as_json()):
        # bonds = pd.read_excel('{}/tables/bonds.xlsx'.format(path_to_source))
        columns = ['Название', 'Доходность', 'Изм, %']
        engine = create_engine(psql_engine)
        bonds = pd.read_sql_query('select * from "bonds"', con=engine)
        bonds = bonds[columns].dropna(axis=0)
        bond_ru = bonds.loc[bonds['Название'].str.contains(r'Россия')].round(2)
        bond_ru = bond_ru.rename(columns={'Название': 'Cрок до погашения', 'Доходность': 'Доходность, %'})
        years = ['1 год', '2 года', '3 года', '5 лет',
                 '7 лет', '10 лет', '15 лет', '20 лет']
        for num, name in enumerate(bond_ru['Cрок до погашения'].values):
            bond_ru['Cрок до погашения'].values[num] = years[num]

        # df transformation
        transformer = dt.Transformer()
        png_path = '{}/img/{}_table.png'.format(path_to_source, 'bonds')
        # transformer.save_df_as_png(df=bond_ru, column_width=[0.11] * len(bond_ru.columns),
        #                           figure_size=(15.5, 3), path_to_source=path_to_source, name='bonds')
        transformer.render_mpl_table(bond_ru, 'bonds', header_columns=0, col_width=2.5, title='Доходности ОФЗ.')
        photo = open(png_path, 'rb')
        day = pd.read_sql_query('select * from "report_bon_day"', con=engine).values.tolist()
        month = pd.read_sql_query('select * from "report_bon_mon"', con=engine).values.tolist()
        # day = analysis_text['Облиигации. День'].drop('Unnamed: 0', axis=1).values.tolist()
        # month = analysis_text['Облиигации. Месяц'].drop('Unnamed: 0', axis=1).values.tolist()
        # print(month)
        title = 'ОФЗ'
        data_source = 'investing.com'
        await __sent_photo_and_msg(message, photo, day, month,
                                   title=sample_of_img_title.format(title, data_source, read_curdatetime()))


# ['экономика', 'ставки', 'ключевая ставка', 'кс', 'монетарная политика']
@dp.message_handler(commands=['eco'])
async def economy_info(message: types.Message):
    print('{} - {}'.format(message.from_user.full_name, message.text))
    if await user_in_whitelist(message.from_user.as_json()):
        engine = create_engine(psql_engine)
        # eco = pd.read_excel('{}/tables/eco.xlsx'.format(path_to_source),
        #                    sheet_name=['Ставка', 'Инфляция в России', 'Ключевые ставки ЦБ мира'])
        world_bet = pd.read_sql_query('select * from "eco_global_stake"', con=engine)
        # rus_infl = eco['Инфляция в России'][[]]
        rus_infl = pd.read_sql_query('select * from "eco_rus_influence"', con=engine)
        rus_infl = rus_infl[['Дата', 'Инфляция, % г/г']]
        # world_bet = eco['Ключевые ставки ЦБ мира'].drop('Unnamed: 0', axis=1).rename(columns={'Country': '',
        #                                                                                      'Last': '',
        #                                                                                      'Previous': ''})
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
        # world_bet['Страна'] = world_bet.apply(lambda x: row: model.translate(row["Страна"], target_lang="rus"),
        # axis=1)

        # df transformation
        transformer = dt.Transformer()
        png_path = '{}/img/{}_table.png'.format(path_to_source, 'world_bet')
        # transformer.save_df_as_png(df=world_bet, column_width=[0.25] * len(world_bet.columns),
        #                           figure_size=(8, 6), path_to_source=path_to_source, name='world_bet')
        world_bet = world_bet.round(2)
        transformer.render_mpl_table(world_bet, 'world_bet', header_columns=0,
                                     col_width=2.2, title='Ключевые ставки ЦБ мира.')
        photo = open(png_path, 'rb')
        day = pd.read_sql_query('select * from "report_eco_day"', con=engine).values.tolist()
        month = pd.read_sql_query('select * from "report_eco_mon"', con=engine).values.tolist()
        title = 'Ключевые ставки ЦБ мира'
        data_source = 'ЦБ стран мира'
        curdatetime = read_curdatetime()
        await __sent_photo_and_msg(message, photo, day, month,
                                   title=sample_of_img_title.format(title, data_source, curdatetime))
        # transformer.save_df_as_png(df=rus_infl, column_width=[0.41] * len(rus_infl.columns),
        #                           figure_size=(5, 2), path_to_source=path_to_source, name='rus_infl')

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
                             parse_mode='HTML', protect_content=True)
        # сообщение с текущими ставками
        stat = pd.read_sql_query('select * from "eco_stake"', con=engine)
        rates = [f"{rate[0]}: {str(rate[1]).replace('%', '').replace(',', '.')}%" for rate in stat.values.tolist()[:3]]
        rates_message = f'<b>{rates[0]}</b>\n{rates[1]}\n{rates[2]}'
        await message.answer(rates_message, parse_mode='HTML', protect_content=True)


@dp.message_handler(commands=['view'])
async def data_mart(message: types.Message):
    if await user_in_whitelist(message.from_user.as_json()):
        transformer = dt.Transformer()
        keys_eco = pd.read_excel('{}/tables/key_eco.xlsx'.format(path_to_source))
        keys_eco = keys_eco[['Unnamed: 0', 2021, 2022, '2023E', '2024E']]
        keys_eco = keys_eco.rename(columns=({'Unnamed: 0': 'Экономические показатели'}))
        spld_keys_eco = np.split(keys_eco, keys_eco[keys_eco.isnull().all(1)].index)

        title = 'Динамика и прогноз основных макроэкономических показателей'
        for key_eco in spld_keys_eco:
            key_eco = key_eco[key_eco['Экономические показатели'].notna()]
            key_eco.reset_index(inplace=True, drop=True)
            block = key_eco['Экономические показатели'][0]
            key_eco = key_eco.iloc[1:]
            transformer.render_mpl_table(key_eco, 'key_eco', header_columns=0, col_width=6, title=title)
            png_path = '{}/img/{}_table.png'.format(path_to_source, 'key_eco')
            photo = open(png_path, 'rb')
            await __sent_photo_and_msg(message, photo,
                                       title=sample_of_img_title_view.format(title, block, read_curdatetime()))


# ['Курсы валют', 'курсы', 'валюты', 'рубль', 'доллар', 'юань', 'евро']
@dp.message_handler(commands=['fx'])
async def exchange_info(message: types.Message):
    print('{} - {}'.format(message.from_user.full_name, message.text))
    if await user_in_whitelist(message.from_user.as_json()):
        png_path = '{}/img/{}_table.png'.format(path_to_source, 'exc')
        engine = create_engine(psql_engine)
        exc = pd.read_sql_query('select * from exc', con=engine)
        exc['Курс'] = exc['Курс'].apply(lambda x: round(float(x), 2) if x is not None else x)
        # exc = pd.read_excel('{}/tables/exc.xlsx'.format(path_to_source))
        # exc = exc.drop('Unnamed: 0', axis=1)

        # df transformation
        transformer = dt.Transformer()
        for num, currency in enumerate(exc['Валюта'].values):
            if currency.lower() == 'usdollar':
                exc['Валюта'].values[num] = 'Индекс DXY'
            else:
                cur = currency.upper().split('-')
                exc['Валюта'].values[num] = '/'.join(cur).replace('CNY', 'CNH')
        # exc.loc[2.5] = [' ', ' ']
        exc = exc.sort_index().reset_index(drop=True)

        transformer.render_mpl_table(exc.round(2), 'exc', header_columns=0,
                                     col_width=2, title='Текущие курсы валют')
        # transformer.save_df_as_png(df=exc, column_width=[0.42] * len(exc.columns),
        #                           figure_size=(5, 2), path_to_source=path_to_source, name='exc')
        day = pd.read_sql_query('select * from "report_exc_day"', con=engine).values.tolist()
        month = pd.read_sql_query('select * from "report_exc_mon"', con=engine).values.tolist()
        # day = analysis_text['Курсы. День'].drop('Unnamed: 0', axis=1).values.tolist()
        # month = analysis_text['Курсы. Месяц'].drop('Unnamed: 0', axis=1).values.tolist()
        photo = open(png_path, 'rb')
        title = 'Курсы валют'
        data_source = 'investing.com'
        curdatetime = read_curdatetime()
        await __sent_photo_and_msg(message, photo, day, month,
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


# ['Металлы', 'сырьевые товары', 'commodities']
@dp.message_handler(commands=['commodities'])
async def metal_info(message: types.Message):
    print('{} - {}'.format(message.from_user.full_name, message.text))
    if await user_in_whitelist(message.from_user.as_json()):
        transformer = dt.Transformer()
        engine = create_engine(psql_engine)
        metal = pd.read_sql_query('select * from metals', con=engine)
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
            # metal[key] = metal[key].apply(lambda x: re.sub(r"\.00$", "", str(x)))
            metal[key] = metal[key].apply(lambda x: str(x).replace(",", "."))
            metal[key] = metal[key].apply(lambda x: __replacer(x))
            metal[key] = metal[key].apply(lambda x: str(x).replace("s", ""))
            metal[key] = metal[key].apply(lambda x: str(x).replace("%", ""))
            metal[key] = metal[key].apply(lambda x: str(x).replace('–', '-'))

            metal[key] = metal[key].apply(lambda x: '{}'.format(np.nan)
            if str(x) == 'None'
            else '{}'.format(x))
            metal[key] = metal[key].astype('float')
            metal[key] = metal[key].round()
            metal[key] = metal[key].apply(lambda x: "{:,.0f}".format(x).replace(',', ' '))
            metal[key] = metal[key].apply(lambda x: '{}%'.format(x)
            if x != 'nan' and key != 'Цена'
            else str(x).replace("nan", "-"))

        metal.index = metal.index.astype('int')
        metal.sort_index(inplace=True)
        transformer.render_mpl_table(metal, 'metal', header_columns=0,
                                     col_width=1.5, title='Цены на ключевые сырьевые товары.')

        # transformer.save_df_as_png(df=metal, column_width=[0.13] * len(metal.columns),
        #                           figure_size=(15.5, 4), path_to_source=path_to_source, name='metal')
        png_path = '{}/img/{}_table.png'.format(path_to_source, 'metal')
        day = pd.read_sql_query('select * from "report_met_day"', con=engine).values.tolist()
        photo = open(png_path, 'rb')
        title = ' Сырьевые товары'
        data_source = 'LME, Bloomberg, investing.com'
        await __sent_photo_and_msg(message, photo, day,
                                   title=sample_of_img_title.format(title, data_source, read_curdatetime()))


def __replacer(data: str):
    """
    if '.' > 1 and first object in data_list == 0 => '{}.{}{}'(*data_list)

    :param data: value from cell
    :return: formated data
    """
    data_list = data.split('.')
    if len(data_list) > 2:
        if data_list[0] == '0':
            return '{}.{}{}'.format(*data_list)
        else:
            return '{}{}.{}'.format(*data_list)
    return data


async def draw_all_tables(message: types.Message):
    from sqlalchemy import create_engine
    engine = create_engine('postgresql://bot:12345@0.0.0.0:5432/users')
    df_from_db = pd.read_sql_query('select * from "users"', con=engine)
    print(df_from_db)


async def user_in_whitelist(user: str):
    user_json = json.loads(user)
    user_id = user_json['id']
    engine = create_engine(psql_engine)
    whitelist = pd.read_sql_query('select * from "whitelist"', con=engine)
    if len(whitelist.loc[whitelist['user_id'] == user_id]) > 0:
        return True
    else:
        return False


@dp.message_handler(commands=['addmetowhitelist'])
async def user_to_whitelist(message: types.Message):
    user_raw = json.loads(message.from_user.as_json())
    email = 'message: types.Message'
    if user_in_whitelist(user_raw):
        if 'username' in user_raw:
            user_username = user_raw['username']
        else:
            user_username = 'Empty_username'
        user_id = user_raw['id']
        user = pd.DataFrame([[user_id, user_username, email, 'user', 'active']],
                            columns=['user_id', 'username', 'email', 'user_type', 'user_status'])
        try:
            engine = create_engine(psql_engine)
            user.to_sql('whitelist', if_exists='append', index=False, con=engine)
            await message.answer(f'Добро пожаловать {email}!', protect_content=True)
        except Exception as e:
            await message.answer(f'Во время авторизации произошла ошибка, попробуйте позже '
                                 f'\n\n{e}', protect_content=True)
            print('Во время авторизации произошла ошибка, попробуйте позже: {}'.format(e))
    else:
        await message.answer(f'{email} - уже существует', protect_content=True)


async def check_your_right(user: dict):
    user_id = user['id']
    engine = create_engine(config.psql_engine)
    user_series = pd.read_sql_query(f"select user_type from whitelist WHERE user_id='{user_id}'", con=engine)
    user_type = user_series.values.tolist()[0][0]
    if user_type == 'admin' or user_type == 'owner':
        return True
    else:
        return False


@dp.message_handler(commands=['admin_help'])
async def admin_help(message: types.Message):

    user = json.loads(message.from_user.as_json())
    admin_flag = await check_your_right(user)

    if admin_flag:
        help_msg = ('<b>/show_article</b> - показать детальную информацию о новости\n'
                    '<b>/change_summary</b> - поменять саммари новости с помощью LLM\n'
                    '<b>/delete_article</b> - удалить новость из базы данных')
        await message.answer(help_msg, protect_content=True, parse_mode='HTML')
    else:
        await message.answer('У Вас недостаточно прав для использования данной команды.', protect_content=True)

@dp.message_handler(commands=['show_article'])
async def show_article(message: types.Message):

    await types.ChatActions.typing()

    user = json.loads(message.from_user.as_json())
    admin_flag = await check_your_right(user)

    if admin_flag:
        ask_link = 'Вставьте ссылку на новость, которую хотите получить.'
        await Form.link.set()
        await bot.send_message(chat_id=message.chat.id, text=ask_link, parse_mode='HTML',
                               protect_content=True, disable_web_page_preview=True)
    else:
        await message.answer('У Вас недостаточно прав для использования данной команды.', protect_content=True)


@dp.message_handler(state=Form.link)
async def continue_show_article(message: types.Message, state: FSMContext):

    await types.ChatActions.typing()
    await state.update_data(link=message.text)
    data = await state.get_data()

    apd_obj = ArticleProcessAdmin()
    full_text, old_text_sum = apd_obj.get_article_text_by_link(data['link'])
    if not full_text:
        await message.answer('Извините, не могу найти новость. Попробуйте в другой раз.', protect_content=True)
        await state.finish()
        return

    data_article_dict = apd_obj.get_article_by_link(data['link'])
    format_msg = ''
    for key, val in data_article_dict.items():
        format_msg += f'<b>{key}</b>: {val}\n'

    await message.answer(format_msg, parse_mode='HTML', protect_content=True, disable_web_page_preview=True)
    await state.finish()


@dp.message_handler(commands=['change_summary'])
async def change_summary(message: types.Message):

    await types.ChatActions.typing()

    user = json.loads(message.from_user.as_json())
    admin_flag = await check_your_right(user)

    if admin_flag:
        ask_link = 'Вставьте ссылку на новость, которую хотите изменить.'
        await Form.link_change_summary.set()
        await bot.send_message(chat_id=message.chat.id, text=ask_link, parse_mode='HTML',
                               protect_content=True, disable_web_page_preview=True)
    else:
        await message.answer('У Вас недостаточно прав для использования данной команды.', protect_content=True)


@dp.message_handler(state=Form.link_change_summary)
async def continue_change_summary(message: types.Message, state: FSMContext):

    await state.update_data(link_change_summary=message.text)
    data = await state.get_data()

    apd_obj = ArticleProcessAdmin()
    full_text, old_text_sum = apd_obj.get_article_text_by_link(data['link_change_summary'])
    if not full_text:
        await message.answer('Извините, не могу найти новость. Попробуйте в другой раз.', protect_content=True)
        await state.finish()
        return

    await message.answer('Создание саммари может занять некоторое время. Ожидайте.', protect_content=True)
    await types.ChatActions.typing()
    new_text_sum = summarization_by_chatgpt(full_text)
    apd_obj.insert_new_gpt_summary(new_text_sum, data['link_change_summary'])

    await message.answer(f"<b>Старое саммари:</b> {old_text_sum}", parse_mode='HTML', protect_content=True)
    await message.answer(f"<b>Новое саммари:</b> {new_text_sum}", parse_mode='HTML', protect_content=True)
    await state.finish()


@dp.message_handler(commands=['delete_article'])
async def delete_article(message: types.Message):

    await types.ChatActions.typing()

    user = json.loads(message.from_user.as_json())
    admin_flag = await check_your_right(user)

    if admin_flag:
        ask_link = 'Вставьте ссылку на новость, которую хотите удалить.'
        await Form.link_to_delete.set()
        await bot.send_message(chat_id=message.chat.id, text=ask_link, parse_mode='HTML',
                               protect_content=True, disable_web_page_preview=True)
    else:
        await message.answer('У Вас недостаточно прав для использования данной команды.', protect_content=True)


@dp.message_handler(state=Form.link_to_delete)
async def continue_delete_article(message: types.Message, state: FSMContext):

    await types.ChatActions.typing()
    await state.update_data(link_to_delete=message.text)
    data = await state.get_data()

    apd_obj = ArticleProcessAdmin()
    full_text, old_text_sum = apd_obj.get_article_text_by_link(data['link_to_delete'])
    if not full_text:
        await message.answer('Извините, не могу найти новость. Попробуйте в другой раз.', protect_content=True)
        await state.finish()
        return
    else:
        permission_answer = f'Вы уверены, что хотите удалить данную новость ?\nЕсли да, то напишите: "Удалить новость".'
        await Form.permission_to_delete.set()
        await message.reply(permission_answer, protect_content=True)


@dp.message_handler(state=Form.permission_to_delete)
async def finish_delete_article(message: types.Message, state: FSMContext):

    await types.ChatActions.typing()
    await state.update_data(permission_to_delete=message.text)
    data = await state.get_data()

    apd_obj = ArticleProcessAdmin()
    if data["permission_to_delete"].lower().strip().replace('"', '').replace('.', '') == 'удалить новость':
        apd_obj.delete_article_by_link(data['link_to_delete'])
        await message.answer('Новость удалена.', protect_content=True)
    else:
        await message.answer('Хорошо, удалим в следующий раз.', protect_content=True)

    await state.finish()


@dp.message_handler()
async def giga_ask(message: types.Message, prompt: str = '', return_ans: bool = False):
    msg = '{} {}'.format(prompt, message.text)
    msg = msg.replace('/bonds', '')
    msg = msg.replace('/eco', '')
    msg = msg.replace('/commodities', '')
    msg = msg.replace('/fx', '')
    print('{} - {}'.format(message.from_user.full_name, msg))
    if await user_in_whitelist(message.from_user.as_json()):
        reply_msg, img_name_list = ArticleProcess().process_user_alias(message.text)
        if reply_msg:
            if img_name_list:
                await types.ChatActions.upload_photo()
                media = types.MediaGroup()
                for name in img_name_list:
                    media.attach_photo(types.InputFile(PATH_TO_COMMODITY_GRAPH.format(name)))
                await bot.send_media_group(message.chat.id, media=media, protect_content=True)
            try:
                await message.answer(reply_msg, parse_mode='HTML', protect_content=True, disable_web_page_preview=True)
            except MessageIsTooLong:
                articles = reply_msg.split('\n\n')
                for article in articles:
                    await message.answer(article, parse_mode='HTML', protect_content=True, disable_web_page_preview=True)
            return None

        global chat
        global token
        message_text = message.text.lower().strip()
        if message_text in bonds_aliases:
            await bonds_info(message)
        elif message_text in eco_aliases:
            await economy_info(message)
        elif message_text in metal_aliases:
            await metal_info(message)
        elif message_text in exchange_aliases:
            await exchange_info(message)
        elif message_text in view_aliases:
            await data_mart(message)
        # elif message_text in ['test']:
        #    await draw_all_tables(message)
        else:
            try:
                giga_answer = chat.ask_giga_chat(token=token, text=msg)
                giga_js = giga_answer.json()['choices'][0]['message']['content']

            except AttributeError:
                chat = gig.GigaChat()
                token = chat.get_user_token()
                print('{}...{} - {}({}) | Перевыпуск'.format(token[:10], token[-10:],
                                                             message.from_user.full_name,
                                                             message.from_user.username))
                giga_answer = chat.ask_giga_chat(token=token, text=msg)
                giga_js = giga_answer.json()['choices'][0]['message']['content']

            except KeyError:
                giga_answer = chat.ask_giga_chat(token=token, text=msg)
                giga_js = giga_answer.json()
            if not return_ans:
                await message.answer('{}\n\n{}'.format(giga_js, giga_ans_footer),
                                     protect_content=True)
            else:
                return giga_js
            print('{} - {}'.format('GigaChat_say', giga_js))
    else:
        await message.answer('Неавторизованный пользователь. Отказано в доступе.', protect_content=True)


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    executor.start_polling(dp, skip_updates=True)
