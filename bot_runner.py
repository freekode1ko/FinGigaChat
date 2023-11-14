import re
import json
import warnings
import textwrap
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import MessageIsTooLong
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext

from module.article_process import ArticleProcess, ArticleProcessAdmin
from module.model_pipe import summarization_by_chatgpt
import module.data_transformer as dt
import module.gigachat as gig
import config

path_to_source = config.path_to_source
API_TOKEN = config.api_token
psql_engine = config.psql_engine
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
    # with open('sources/tables/time.txt', 'r') as f:
    #     curdatetime = f.read()
    engine = create_engine(psql_engine)
    curdatetime = pd.read_sql_query('select * from "date_of_last_build"', con=engine)
    return curdatetime['date_time'][0]


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


@dp.message_handler(commands=['start', 'help'])
async def help_handler(message: types.Message):
    help_text = config.help_text
    if await user_in_whitelist(message.from_user.as_json()):
        to_pin = await bot.send_message(message.chat.id, help_text, protect_content=True)
        msg_id = to_pin.message_id
        await bot.pin_chat_message(chat_id=message.chat.id, message_id=msg_id)


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
    print('{} - {}'.format(message.from_user.full_name, message.text))
    if await user_in_whitelist(message.from_user.as_json()):
        transformer = dt.Transformer()
        engine = create_engine(psql_engine)
        key_eco_table = pd.read_sql_query('select * from key_eco', con=engine)
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


@dp.message_handler(commands=['myactivesubscriptions'])
async def user_subscriptions(message: types.Message):
    user_id = json.loads(message.from_user.as_json())['id']  # Get user_ID from message
    engine = create_engine(psql_engine)
    subscriptions = pd.read_sql_query(f"SELECT subscriptions FROM whitelist WHERE user_id = '{user_id}'",
                                      con=engine)['subscriptions'].values.tolist()
    if not subscriptions:
        keyboard = types.ReplyKeyboardRemove()
        msg_txt = 'Нет активных подписок'
    else:
        buttons = []
        for subscription in subscriptions:
            buttons.append([types.KeyboardButton(text=subscription)])
        msg_txt = 'Выберите подписку'
        keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True,
                                             input_field_placeholder=msg_txt)
    await message.answer(msg_txt, reply_markup=keyboard)


async def user_in_whitelist(user: str):
    user_json = json.loads(user)
    user_id = user_json['id']
    engine = create_engine(psql_engine)
    whitelist = pd.read_sql_query('select * from "whitelist"', con=engine)
    if len(whitelist.loc[whitelist['user_id'] == user_id]) >= 1:
        return True
    else:
        return False


@dp.message_handler(commands=['addmetowhitelist'])
async def user_to_whitelist(message: types.Message):
    print('{} - {}'.format(message.from_user.full_name, message.text))
    user_raw = json.loads(message.from_user.as_json())
    email = ' '
    if not await user_in_whitelist(message.from_user.as_json()):
        if 'username' in user_raw:
            user_username = user_raw['username']
        else:
            user_username = 'Empty_username'
        user_id = user_raw['id']
        user = pd.DataFrame([[user_id, user_username, email, 'user', 'active', None]],
                            columns=['user_id', 'username', 'email', 'user_type', 'user_status', 'subscriptions'])
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


async def __create_fin_table(message, client_name, client_fin_table):
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
    print('{} - {}'.format(message.from_user.full_name, message.text))
    user = json.loads(message.from_user.as_json())
    admin_flag = await check_your_right(user)

    if admin_flag:
        # TODO: '<b>/analyse_bad_article</b> - показать возможные нерелевантные новости\n'
        help_msg = ('<b>/show_article</b> - показать детальную информацию о новости\n'
                    '<b>/change_summary</b> - поменять саммари новости с помощью LLM\n'
                    '<b>/delete_article</b> - удалить новость из базы данных')
        await message.answer(help_msg, protect_content=True, parse_mode='HTML')
    else:
        await message.answer('У Вас недостаточно прав для использования данной команды.', protect_content=True)


@dp.message_handler(commands=['show_article'])
async def show_article(message: types.Message):
    await types.ChatActions.typing()
    print('{} - {}'.format(message.from_user.full_name, message.text))
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
    print('{} - {}'.format(message.from_user.full_name, message.text))
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
    if not isinstance(data_article_dict, dict):
        await message.answer(f'Извините, произошла ошибка: {data_article_dict}.\nПопробуйте в другой раз.',
                             protect_content=True)
        return

    format_msg = ''
    for key, val in data_article_dict.items():
        format_msg += f'<b>{key}</b>: {val}\n'

    await message.answer(format_msg, parse_mode='HTML', protect_content=True, disable_web_page_preview=True)
    await state.finish()


@dp.message_handler(commands=['change_summary'])
async def change_summary(message: types.Message):
    print('{} - {}'.format(message.from_user.full_name, message.text))
    if not config.api_key_gpt:
        await message.answer('Данная команда пока недоступна.', protect_content=True)
        return

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
    print('{} - {}'.format(message.from_user.full_name, message.text))
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
    try:
        await message.answer(f"<b>Старое саммари:</b> {old_text_sum}", parse_mode='HTML', protect_content=True)
    except MessageIsTooLong:
        # TODO: показывать батчами при необходимости
        await message.answer(f"<b>Старое саммари не помещается в одно сообщение.</b>",
                             parse_mode='HTML', protect_content=True)
    await message.answer(f"<b>Новое саммари:</b> {new_text_sum}", parse_mode='HTML', protect_content=True)
    await state.finish()


# TODO: Убрать проверку удаления новости
@dp.message_handler(commands=['delete_article'])
async def delete_article(message: types.Message):
    await types.ChatActions.typing()
    print('{} - {}'.format(message.from_user.full_name, message.text))
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
    print('{} - {}'.format(message.from_user.full_name, message.text))
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
    print('{} - {}'.format(message.from_user.full_name, message.text))
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


@dp.message_handler(commands=['analyse_bad_article'])
async def analyse_bad_article(message: types.Message):
    print('{} - {}'.format(message.from_user.full_name, message.text))
    await types.ChatActions.typing()
    await message.answer('Пока команда недоступна.', protect_content=True)
    return
    # TODO: реализовать при необходимости
    # user = json.loads(message.from_user.as_json())
    # admin_flag = await check_your_right(user)
    #
    # if admin_flag:
    #     apd_obj = ArticleProcessAdmin()
    #     msgs = apd_obj.get_bad_article()
    #     for msg_dict in msgs:
    #         format_msg = ''
    #         for key, val in msg_dict.items():
    #             format_msg += f'<b>{key}</b>: {val}\n'
    #         await message.answer(format_msg, parse_mode='HTML', disable_web_page_preview=True)
    # else:
    #     await message.answer('У Вас недостаточно прав для использования данной команды.', protect_content=True)


@dp.callback_query_handler(text='next_5_news')
async def send_next_five_news(call: types.CallbackQuery):
    try:
        await call.message.answer(articles_l5, parse_mode='HTML',
                                  protect_content=True, disable_web_page_preview=True)
    except MessageIsTooLong:
        articles = articles_l5.split('\n\n')
        for article in articles:
            await call.message.answer(article, parse_mode='HTML',
                                      protect_content=True, disable_web_page_preview=True)
    finally:
        await call.message.edit_reply_markup()


async def show_client_fin_table(message: types.Message, s_id: int) -> bool:
    client_fin_table = ArticleProcess().get_client_fin_indicators(s_id, message.text.strip().lower())
    if client_fin_table:
        for name, client_fin_table_item in client_fin_table.items():
            if not client_fin_table_item.empty:
                await types.ChatActions.upload_photo()
                await __create_fin_table(message, name, client_fin_table_item)
        return True
    else:
        return False


@dp.message_handler()
async def giga_ask(message: types.Message, prompt: str = '', return_ans: bool = False):
    msg = '{} {}'.format(prompt, message.text)
    msg = msg.replace('/bonds', '')
    msg = msg.replace('/eco', '')
    msg = msg.replace('/commodities', '')
    msg = msg.replace('/fx', '')
    print('{} - {}'.format(message.from_user.full_name, msg))
    if await user_in_whitelist(message.from_user.as_json()):
        msg_text = message.text.replace('«', '"').replace('»', '"')
        subject_ids, subject = ArticleProcess().find_subject_id(msg_text, 'client'), 'client'
        if not subject_ids:
            subject_ids, subject = ArticleProcess().find_subject_id(msg_text, 'commodity'), 'commodity'

        for subject_id in subject_ids:
            com_price, reply_msg, img_name_list = ArticleProcess().process_user_alias(subject_id, subject)

            return_ans = await show_client_fin_table(message, subject_id)

            if reply_msg:

                if img_name_list:
                    await types.ChatActions.upload_photo()
                    media = types.MediaGroup()
                    for name in img_name_list:
                        media.attach_photo(types.InputFile(PATH_TO_COMMODITY_GRAPH.format(name)))
                    await bot.send_media_group(message.chat.id, media=media, protect_content=True)

                if com_price:
                    await message.answer(com_price, parse_mode='HTML', protect_content=True,
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
                        await message.answer(articles_f5, parse_mode='HTML', protect_content=True,
                                             disable_web_page_preview=True, reply_markup=keyboard)
                    except MessageIsTooLong:
                        articles = articles_f5.split('\n\n')
                        for article in articles:
                            if len(article) < 4050:
                                await message.answer(article, parse_mode='HTML', protect_content=True,
                                                     disable_web_page_preview=True)
                            else:
                                print(f"MessageIsTooLong ERROR: {article}")
                return_ans = True

        if not return_ans:
            return_ans = await show_client_fin_table(message, None)

        if not return_ans:
            await types.ChatActions.typing()
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
                    if giga_answer.status_code == 200:
                        giga_js = giga_answer.json()['choices'][0]['message']['content']
                    elif giga_answer.status_code == 401:
                        print('Token {}...{} is dead.'.format(token[:10], token[-10:]))
                        raise AttributeError
                    else:
                        raise KeyError

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

                await message.answer('{}\n\n{}'.format(giga_js, giga_ans_footer), protect_content=True)
                print('{} - {}'.format('GigaChat_say', giga_js))
    else:
        await message.answer('Неавторизованный пользователь. Отказано в доступе.', protect_content=True)


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    executor.start_polling(dp, skip_updates=True)
