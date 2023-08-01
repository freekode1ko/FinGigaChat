from aiogram import Bot, Dispatcher, executor, types
import module.data_transformer as dt
import module.gigachat as gig
import pandas as pd
import datetime
import warnings
import config
import re

path_to_source = config.path_to_source
curdatetime = datetime.datetime.now()
API_TOKEN = config.api_token
token = ''
chat = ''

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

bonds_aliases = ['облигации', 'бонды', 'офз']
eco_aliases = ['экономика', 'ставки', 'ключевая ставка', 'кс', 'монетарная политика']
exchange_aliases = ['курсы валют', 'курсы', 'валюты', 'рубль', 'доллар', 'юань', 'евро']
metal_aliases = ['металлы', 'сырьевые товары', 'commodities']
analysis_text = pd.read_excel('{}/tables/text.xlsx'.format(path_to_source), sheet_name=None)
summ_prompt = 'Сократи текст, оставь только ключевую информацию с числовыми показателями и прогнозами на будущее, ' \
              'кратко указывай источник данных, убери из текста сравнительные обороты, вводные фразы, авторские ' \
              'мнения и другую не ключевую информацию. Вот текст:'


async def __text_splitter(message: types.Message, text: str, name: str, date: str, batch_size: int = 2048):
    text_group = []
    # import dateutil.parser as dparser
    # date = dparser.parse(date, fuzzy=True)
    print(date)
    # await message.answer('Краткое содержание:')
    giga_ans = await giga_ask(message, prompt='{}\n {}'.format(summ_prompt, text), return_ans=True)
    if len(giga_ans) > batch_size:
        for batch in range(0, len(giga_ans), batch_size):
            text_group.append(text[batch:batch + batch_size])
        for summ_part in text_group:
            await message.answer('<b>{}</b> - {}\n\n{}\n\n<i>{}</i>'.format(name, date, summ_part, date),
                                 parse_mode="HTML")
    else:
        await message.answer('<b>{}</b> - {}\n\n{}\n\n<i>{}</i>'.format(name, date, giga_ans, date),
                             parse_mode="HTML")


async def __sent_photo_and_msg(message: types.Message, photo, day: str = '', month: str = '', title: str = ''):
    batch_size = 2048
    if day:
        for day_rev in day:
            print(day_rev[0], day_rev[2])
            # await message.answer('Публикация дня: {}, от: {}'.format(day_rev[0], day_rev[2]))
            await __text_splitter(message, day_rev[1], day_rev[0], day_rev[2], batch_size)
    if month:
        for month_rev in month:
            # await message.answer('Публикация месяца: {}, от: {}'.format(month_rev[0], month_rev[2]))
            await __text_splitter(message, month_rev[1], day_rev[0], day_rev[2], batch_size)
    # await message.answer(title)
    await bot.send_photo(message.chat.id, photo, caption=title)


async def __read_tables_from_companies(message: types.Message, companies: dict):
    company = companies['head'].loc[companies['head']['Name'].str.lower() == message.text.lower()].values.tolist()
    company_id = company[0][1]
    company_url = company[0][3]
    transformer = dt.Transformer()
    await message.reply("Ссылка на архивы с результатами:\n{}".format(company_url))
    await message.answer('Табличные данные по показателям:')

    for key in companies.keys():
        if str(company_id) in key:
            png_path = '{}/img/{}_table.png'.format(path_to_source, key)
            title = '{}'.format(key.split('_')[1])
            transformer.save_df_as_png(df=companies[key].drop('Unnamed: 0', axis=1),
                                       column_width=[0.15] * len(companies[key].columns),
                                       figure_size=(15, 1.5), path_to_source=path_to_source, name=key)
            photo = open(png_path, 'rb')
            await __sent_photo_and_msg(message, photo, title=title)


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    global chat
    global token
    chat = gig.GigaChat()
    token = chat.get_user_token()
    print('{}...{} - {}({})'.format(token[:10], token[-10:],
                                    message.from_user.full_name,
                                    message.from_user.username))
    await message.reply("Давай я спрошу GigaChat за тебя")


@dp.message_handler(commands=['companies'])
async def company_info(message: types.Message):
    print('{} - {}'.format(message.from_user.full_name, message.text))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Полиметалл', 'ММК', 'Норникель', 'Полюс', 'Русал', 'Северсталь']
    keyboard.add(*buttons)
    await message.reply("Выберите компанию для детальной информации по ней", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text.lower() in ["полиметалл", 'ммк', 'норникель',
                                                             'полюс', 'русал', 'северсталь'])
async def button_polymetal(message: types.Message):
    print('{} - {}'.format(message.from_user.full_name, message.text))
    companies = pd.read_excel('{}/tables/companies.xlsx'.format(path_to_source), sheet_name=None)
    await __read_tables_from_companies(message, companies)


# ['облигации', 'бонды', 'офз']
@dp.message_handler(commands=['bonds'])
async def bonds_info(message: types.Message):
    print('{} - {}'.format(message.from_user.full_name, message.text))
    bonds = pd.read_excel('{}/tables/bonds.xlsx'.format(path_to_source))
    columns = ['Название', 'Доходность', 'Изм, %']
    bonds = bonds[columns].dropna(axis=0)
    bond_ru = bonds.loc[bonds['Название'].str.contains(r'Россия')].round(2)
    bond_ru = bond_ru.rename(columns={'Название': 'Cрок до погашения'})
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
    day = analysis_text['Облиигации. День'].drop('Unnamed: 0', axis=1).values.tolist()
    month = analysis_text['Облиигации. Месяц'].drop('Unnamed: 0', axis=1).values.tolist()

    title = 'Государственные ценные бумаги'
    # await message.answer('Да да - Вот оно: \n')
    await __sent_photo_and_msg(message, photo, day, month, title='Данные на {}'.format(curdatetime))


# ['экономика', 'ставки', 'ключевая ставка', 'кс', 'монетарная политика']
@dp.message_handler(commands=['eco'])
async def economy_info(message: types.Message):
    print('{} - {}'.format(message.from_user.full_name, message.text))
    eco = pd.read_excel('{}/tables/eco.xlsx'.format(path_to_source),
                        sheet_name=['Ставка', 'Инфляция в России', 'Ключевые ставки ЦБ мира'])
    stat = eco['Ставка'].drop('Unnamed: 0', axis=1)
    rus_infl = eco['Инфляция в России'][['Дата', 'Инфляция, % г/г']]
    world_bet = eco['Ключевые ставки ЦБ мира'].drop('Unnamed: 0', axis=1).rename(columns={'Country': 'Страна',
                                                                                          'Last': 'Ставка',
                                                                                          'Previous': 'Предыдущая'})
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
    world_bet = world_bet[['Страна', 'Ставка', 'Предыдущая']]
    for num, country in enumerate(world_bet['Страна'].values):
        world_bet.Страна[world_bet.Страна == country] = countries[country]
    # world_bet['Страна'] = world_bet.apply(lambda x: row: model.translate(row["Страна"], target_lang="rus"), axis=1)

    # df transformation
    transformer = dt.Transformer()
    png_path = '{}/img/{}_table.png'.format(path_to_source, 'world_bet')
    # transformer.save_df_as_png(df=world_bet, column_width=[0.25] * len(world_bet.columns),
    #                           figure_size=(8, 6), path_to_source=path_to_source, name='world_bet')
    world_bet = world_bet.round(2)
    transformer.render_mpl_table(world_bet, 'world_bet', header_columns=0,
                                 col_width=2.2, title='Ключевые ставки ЦБ мира.')
    photo = open(png_path, 'rb')
    day = analysis_text['Экономика. День'].drop('Unnamed: 0', axis=1).values.tolist()
    month = analysis_text['Экономика. Месяц'].drop('Unnamed: 0', axis=1).values.tolist()

    await message.answer('{}\n{}\n{}'.format(*['{}: {}'.format(i[0], i[1]) for i in stat.head(3).values]))
    # await message.answer()
    title = 'Ключевые ставки ЦБ мира'
    await __sent_photo_and_msg(message, photo, day, month, title='Данные на {}'.format(curdatetime))
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
    #title = 'Инфляция в России'
    await bot.send_photo(message.chat.id, photo, caption='Данные на {}'.format(curdatetime))


# ['Курсы валют', 'курсы', 'валюты', 'рубль', 'доллар', 'юань', 'евро']
@dp.message_handler(commands=['exchange'])
async def exchange_info(message: types.Message):
    print('{} - {}'.format(message.from_user.full_name, message.text))
    png_path = '{}/img/{}_table.png'.format(path_to_source, 'exc')
    exc = pd.read_excel('{}/tables/exc.xlsx'.format(path_to_source))
    exc = exc.drop('Unnamed: 0', axis=1)

    # df transformation
    transformer = dt.Transformer()
    for num, currency in enumerate(exc['Валюта'].values):
        if currency.lower() == 'usdollar':
            exc['Валюта'].values[num] = 'Индекс DXY'
        else:
            cur = currency.upper().split('-')
            exc['Валюта'].values[num] = '/'.join(cur).replace('CNY', 'CNH')
    exc.loc[2.5] = [' ', ' ']
    exc = exc.sort_index().reset_index(drop=True)

    transformer.render_mpl_table(exc.round(2), 'exc', header_columns=0,
                                 col_width=2, title='Текущие курсы валют')
    # transformer.save_df_as_png(df=exc, column_width=[0.42] * len(exc.columns),
    #                           figure_size=(5, 2), path_to_source=path_to_source, name='exc')
    day = analysis_text['Курсы. День'].drop('Unnamed: 0', axis=1).values.tolist()
    month = analysis_text['Курсы. Месяц'].drop('Unnamed: 0', axis=1).values.tolist()
    photo = open(png_path, 'rb')
    # title = 'Курсы валют'
    # await message.answer('Да да - Вот оно:\n')
    await __sent_photo_and_msg(message, photo, day, month, title='Данные на {}'.format(curdatetime))


# ['Металлы', 'сырьевые товары', 'commodities']
@dp.message_handler(commands=['metal'])
async def metal_info(message: types.Message):
    print('{} - {}'.format(message.from_user.full_name, message.text))
    transformer = dt.Transformer()
    metal = pd.read_excel('{}/tables/metal.xlsx'.format(path_to_source))
    metal = metal[['Metals', 'Price', 'Day', 'Weekly', 'Monthly', 'YoY']]
    metal = metal.rename(columns=({'Metals': 'Сырье', 'Price': 'Цена', 'Day': 'Δ День',
                                   'Weekly': 'Δ Неделя', 'Monthly': 'Δ Месяц', 'YoY': 'Δ Год'}))

    order = {'Медь': ['Медь, $/т', '0'],
             'Aluminum USD/T': ['Алюминий, $/т', '1'],
             'Nickel USD/T': ['Никель, $/т', '2'],
             'Lead USD/T': ['Cвинец, $/т', '3'],
             'Zinc USD/T': ['Цинк, $/т', '4'],
             'Lithium CNY/T': ['Литий, CNH/т', '9'],
             'Cobalt USD/T': ['Кобальт, $/т', '10'],
             'Железорудное сырье': ['ЖРС (Китай), $/т', '11'],
             'кокс. уголь': ['Кокс. уголь (Au), $/т', '14']
             }
    metal['ind'] = None
    for num, commodity in enumerate(metal['Сырье'].values):
        if commodity in order:
            metal.Сырье[metal.Сырье == commodity] = '<>'.join(order[commodity])
        else:
            metal.drop(num, inplace=True)
    metal[['Сырье', 'ind']] = metal['Сырье'].str.split('<>', expand=True)
    metal.set_index('ind', drop=True, inplace=True)
    metal.sort_index(inplace=True)
    # locale.setlocale(locale.LC_NUMERIC, 'English')
    # TODO: Fix bug with delete splitter ',' for thousands
    for key in metal.columns[1:]:
        metal[key] = metal[key].apply(lambda x: re.sub(r"\.00$", "", str(x)))
        metal[key] = metal[key].apply(lambda x: str(x).replace(",", "."))
        metal[key] = metal[key].apply(lambda x: str(x).replace("s", ""))
        metal[key] = metal[key].apply(lambda x: str(x).replace("%", ""))
        # metal[key] = metal[key].apply(lambda x: str(x).replace(".00", ""))
        metal[key] = metal[key].apply(lambda x: str(x).replace('–', '-'))

        metal[key] = metal[key].astype('float')
        metal[key] = metal[key].round(1)
        metal[key] = metal[key].apply(lambda x: str(x).replace("nan", "-"))

    transformer.render_mpl_table(metal, 'metal', header_columns=0,
                                 col_width=3.1, title='Цены на ключевые сырьевые товары.')

    # transformer.save_df_as_png(df=metal, column_width=[0.13] * len(metal.columns),
    #                           figure_size=(15.5, 4), path_to_source=path_to_source, name='metal')
    png_path = '{}/img/{}_table.png'.format(path_to_source, 'metal')
    day = analysis_text['Металлы. День'].drop('Unnamed: 0', axis=1).T.values.tolist()
    print(day)
    photo = open(png_path, 'rb')
    # await message.answer('Да да - Вот оно:')
    await __sent_photo_and_msg(message, photo, day, title='Данные на {}'.format(curdatetime))


def __replacer(data: str, change):
    list_of_data = data.split(change)
    print(data, len(list_of_data))
    if len(list_of_data) > 1:
        return '{}{}'.format(list_of_data[0], '.'.join(list_of_data[1:]))
    else:
        return data


async def draw_all_tables(message: types.Message):
    print('{} - {}'.format(message.from_user.full_name, message.text))
    await message.answer('Deprecated method: \nЭтот метод более не активен. '
                         '\nЧат переведен на новый формат отображения данных')
    '''
    bonds = pd.read_excel('{}/tables/bonds.xlsx'.format(path_to_source))
    columns = ['Название', 'Доходность', 'Осн,', 'Макс,', 'Мин,', 'Изм,', 'Изм, %', 'Время']
    bonds = bonds[columns].dropna(axis=0)
    bond_ru = bonds.loc[bonds['Название'].str.contains(r'Россия')]

    metal = pd.read_excel('{}/tables/metal.xlsx'.format(path_to_source))
    metal = metal[['Metals', 'Price', 'Day', 'Weekly', 'Monthly', 'YoY']]
    metal = metal.rename(columns=({'Metals': 'Сырье', 'Price': 'Цена', 'Day': 'Δ День',
                                   'Weekly': 'Δ Неделя', 'Monthly': 'Δ Месяц', 'YoY': 'Δ Год'}))

    exc = pd.read_excel('{}/tables/exc.xlsx'.format(path_to_source))
    exc = exc.drop('Unnamed: 0', axis=1)

    eco = pd.read_excel('{}/tables/eco.xlsx'.format(path_to_source),
                        sheet_name=['Ставка', 'Инфляция в России', 'Ключевые ставки ЦБ мира'])
    stat = eco['Ставка'].drop('Unnamed: 0', axis=1)
    rus_infl = eco['Инфляция в России'][['Дата', 'Инфляция, % г/г']]
    world_bet = eco['Ключевые ставки ЦБ мира'].drop('Unnamed: 0', axis=1).rename(columns={'Country': 'Страна',
                                                                                          'Last': 'Ставка',
                                                                                          'Previous': 'Предыдущая'})
    world_bet = world_bet[['Страна', 'Ставка', 'Предыдущая']]

    day = ''
    month = ''
    transformer = dt.Transformer()
    import datetime
    curdatetime = datetime.datetime.now()

    title = 'Доходности ОФЗ.'
    png_path = '{}/img/{}_table.png'.format(path_to_source, '1_TEST')
    transformer.render_mpl_table(bond_ru, '1_TEST', header_columns=0, col_width=2.13,
                                 title=title)  # [i*0.2 for i in columns_width])
    photo = open(png_path, 'rb')
    await __sent_photo_and_msg(message, photo, day, month, 'Данные на {}'.format(curdatetime))

    title = 'Ключевые ставки ЦБ мира.'
    png_path = '{}/img/{}_table.png'.format(path_to_source, '2_TEST')
    transformer.render_mpl_table(world_bet, '2_TEST', header_columns=0, col_width=2,
                                 title=title)  # [i*0.2 for i in columns_width])
    photo = open(png_path, 'rb')
    await __sent_photo_and_msg(message, photo, day, month, 'Данные на {}'.format(curdatetime))

    title = 'Ежемесячная инфляция в России.'
    png_path = '{}/img/{}_table.png'.format(path_to_source, '3_TEST')
    transformer.render_mpl_table(rus_infl, '3_TEST', header_columns=0, col_width=2,
                                 title=title)  # [i*0.2 for i in columns_width])
    photo = open(png_path, 'rb')
    await __sent_photo_and_msg(message, photo, day, month, 'Данные на {}'.format(curdatetime))

    title = 'Текущие курсы валют'
    png_path = '{}/img/{}_table.png'.format(path_to_source, '4_TEST')
    transformer.render_mpl_table(exc, '4_TEST', header_columns=0, col_width=2,
                                 title=title)  # [i*0.2 for i in columns_width])
    photo = open(png_path, 'rb')
    await __sent_photo_and_msg(message, photo, day, month, 'Данные на {}'.format(curdatetime))

    title = 'Цены на ключевые сырьевые товары.'
    png_path = '{}/img/{}_table.png'.format(path_to_source, '5_TEST')
    transformer.render_mpl_table(metal, '5_TEST', header_columns=0, col_width=3.1,
                                 title=title)  # [i*0.2 for i in columns_width])
    photo = open(png_path, 'rb')
    await __sent_photo_and_msg(message, photo, day, month, 'Данные на {}'.format(curdatetime))
    '''
    '''
    # METALS
    await message.answer("METALS")
    metal = pd.read_excel('{}/tables/metal.xlsx'.format(path_to_source))
    metal = metal[['Metals', 'Price', 'Day', 'Weekly', 'Monthly', 'YoY']]
    metal = metal.rename(columns=({'Metals': 'Сырье', 'Price': 'Цена', 'Day': 'Δ День',
                                   'Weekly': 'Δ Неделя', 'Monthly': 'Δ Месяц', 'YoY': 'Δ Год'}))
    await message.answer(metal.to_markdown(tablefmt="grid", index=False))#.to_string(index=False))

    # EXCHANGE
    await message.answer("EXCHANGE")
    exc = pd.read_excel('{}/tables/exc.xlsx'.format(path_to_source))
    exc = exc.drop('Unnamed: 0', axis=1)
    await message.answer(exc.to_markdown(tablefmt="grid", index=False))#.to_string(index=False))

    # ECONOMY
    await message.answer("ECONOMY")
    eco = pd.read_excel('{}/tables/eco.xlsx'.format(path_to_source),
                        sheet_name=['Ставка', 'Инфляция в России', 'Ключевые ставки ЦБ мира'])
    stat = eco['Ставка'].drop('Unnamed: 0', axis=1)
    rus_infl = eco['Инфляция в России'][['Дата', 'Инфляция, % г/г']]
    world_bet = eco['Ключевые ставки ЦБ мира'].drop('Unnamed: 0', axis=1).rename(columns={'Country': 'Страна',
                                                                                          'Last': 'Ставка',
                                                                                          'Previous': 'Предыдущая'})
    world_bet = world_bet[['Страна', 'Ставка', 'Предыдущая']]
    await message.answer(stat.to_markdown(tablefmt="grid", index=False))#.to_string(index=False))
    await message.answer(rus_infl.to_markdown(tablefmt="grid", index=False))#.to_string(index=False))
    await message.answer(world_bet.to_markdown(tablefmt="grid", index=False))#.to_string(index=False))

    # BONDS
    await message.answer("BONDS")
    bonds = pd.read_excel('{}/tables/bonds.xlsx'.format(path_to_source))
    columns = ['Название', 'Доходность', 'Осн,', 'Макс,', 'Мин,', 'Изм,', 'Изм, %', 'Время']
    bonds = bonds[columns].dropna(axis=0)
    bond_ru = bonds.loc[bonds['Название'].str.contains(r'Россия')]
    await message.answer(bond_ru.to_markdown(tablefmt="grid", index=False))#.to_string(index=False))
    '''

@dp.message_handler()
async def giga_ask(message: types.Message, prompt: str = '', return_ans: bool = False):
    global chat
    global token
    msg = '{} {}'.format(prompt, message.text)
    msg = msg.replace('/bonds', '')
    msg = msg.replace('/eco', '')
    msg = msg.replace('/metal', '')
    msg = msg.replace('/exchange', '')
    print('{} - {}'.format(message.from_user.full_name, msg))

    if message.text.lower() in bonds_aliases:
        await bonds_info(message)
    elif message.text.lower() in eco_aliases:
        await economy_info(message)
    elif message.text.lower() in metal_aliases:
        await metal_info(message)
    elif message.text.lower() in exchange_aliases:
        await exchange_info(message)
    elif message.text.lower() in ['test']:
        await draw_all_tables(message)
    else:
        try:
            giga_answer = chat.ask_giga_chat(msg, token)
            giga_js = giga_answer.json()['choices'][0]['message']['content']

        except AttributeError:
            chat = gig.GigaChat()
            token = chat.get_user_token()
            print('{}...{} - {}({}) | Перевыпуск'.format(token[:10], token[-10:],
                                                         message.from_user.full_name,
                                                         message.from_user.username))
            giga_answer = chat.ask_giga_chat(msg, token)
            giga_js = giga_answer.json()['choices'][0]['message']['content']

        except KeyError:
            giga_answer = chat.ask_giga_chat(msg, token)
            giga_js = giga_answer.json()
        if not return_ans:
            await message.answer(giga_js)
        else:
            return giga_js
        print('{} - {}'.format('GigaChat_say', giga_js))


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    executor.start_polling(dp, skip_updates=True)
