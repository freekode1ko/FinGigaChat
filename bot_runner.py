from aiogram import Bot, Dispatcher, executor, types
import module.data_transformer as dt
import module.gigachat as gig
import pandas as pd
import warnings
import config

path_to_source = config.path_to_source
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


async def __text_splitter(message: types.Message, text: str, batch_size: int = 2048):
    text_group = []
    await message.answer('Краткое содержание:')
    giga_ans = await giga_ask(message, prompt='{}\n {}'.format(summ_prompt, text), return_ans=True)
    if len(giga_ans) > batch_size:
        for batch in range(0, len(giga_ans), batch_size):
            text_group.append(text[batch:batch + batch_size])
        for summ_part in text_group:
            await message.answer(summ_part)
    else:
        await message.answer(giga_ans)


async def __sent_photo_and_msg(message: types.Message, photo, day: str = '', month: str = ''):
    batch_size = 2048
    await bot.send_photo(message.chat.id, photo)
    if day:
        for day_rev in day:
            print(day_rev[0], day_rev[2])
            await message.answer('Публикация дня: {}, от: {}'.format(day_rev[0], day_rev[2]))
            await __text_splitter(message, day_rev[1], batch_size)
    if month:
        for month_rev in month:
            await message.answer('Публикация месяца: {}, от: {}'.format(month_rev[0], month_rev[2]))
            await __text_splitter(message, month_rev[1], batch_size)


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
            await message.answer('{}:'.format(key.split('_')[1]))
            transformer.save_df_as_png(df=companies[key].drop('Unnamed: 0', axis=1),
                                       column_width=[0.15] * len(companies[key].columns),
                                       figure_size=(15, 1.5), path_to_source=path_to_source, name=key)
            photo = open(png_path, 'rb')
            await __sent_photo_and_msg(message, photo)


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    global chat
    global token
    chat = gig.GigaChat()
    token = chat.get_user_token()
    print('{}...{} - {}({})'.format(token[:10], token[-10:],
                                    message.from_user.full_name,
                                    message.from_user.username))
    await message.reply("Давай я спрошу ГигаЧат за тебя")


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
    columns = ['Название', 'Доходность', 'Осн,', 'Макс,', 'Мин,', 'Изм,', 'Изм, %', 'Время']
    bonds = bonds[columns].dropna(axis=0)
    bond_ru = bonds.loc[bonds['Название'].str.contains(r'Россия')]

    # df transformation
    transformer = dt.Transformer()
    png_path = '{}/img/{}_table.png'.format(path_to_source, 'bonds')
    transformer.save_df_as_png(df=bond_ru, column_width=[0.11] * len(bond_ru.columns),
                               figure_size=(15.5, 3), path_to_source=path_to_source, name='bonds')
    photo = open(png_path, 'rb')
    day = analysis_text['Облиигации. День'].drop('Unnamed: 0', axis=1).values.tolist()
    month = analysis_text['Облиигации. Месяц'].drop('Unnamed: 0', axis=1).values.tolist()
    await message.answer('Да да - Вот оно: \nГосударственные ценные бумаги:')
    await __sent_photo_and_msg(message, photo, day, month)


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
    world_bet = world_bet[['Страна', 'Ставка', 'Предыдущая']]

    # df transformation
    transformer = dt.Transformer()
    png_path = '{}/img/{}_table.png'.format(path_to_source, 'world_bet')
    transformer.save_df_as_png(df=world_bet, column_width=[0.25] * len(world_bet.columns),
                               figure_size=(8, 6), path_to_source=path_to_source, name='world_bet')
    photo = open(png_path, 'rb')
    day = analysis_text['Экономика. День'].drop('Unnamed: 0', axis=1).values.tolist()
    month = analysis_text['Экономика. Месяц'].drop('Unnamed: 0', axis=1).values.tolist()

    await message.answer('Да да - Вот оно:\n{}\n{}\n{}'
                         .format(*['{}: {}'.format(i[0], i[1]) for i in stat.head(3).values]))
    await message.answer('Ключевые ставки ЦБ мира:')
    await __sent_photo_and_msg(message, photo, day, month)

    transformer.save_df_as_png(df=rus_infl, column_width=[0.41] * len(rus_infl.columns),
                               figure_size=(5, 2), path_to_source=path_to_source, name='rus_infl')
    png_path = '{}/img/{}_table.png'.format(path_to_source, 'rus_infl')
    photo = open(png_path, 'rb')
    await message.answer('Инфляция в России:')
    await bot.send_photo(message.chat.id, photo)


# ['Курсы валют', 'курсы', 'валюты', 'рубль', 'доллар', 'юань', 'евро']
@dp.message_handler(commands=['exchange'])
async def exchange_info(message: types.Message):
    print('{} - {}'.format(message.from_user.full_name, message.text))
    png_path = '{}/img/{}_table.png'.format(path_to_source, 'exc')
    exc = pd.read_excel('{}/tables/exc.xlsx'.format(path_to_source))
    exc = exc.drop('Unnamed: 0', axis=1)

    # df transformation
    transformer = dt.Transformer()
    transformer.save_df_as_png(df=exc, column_width=[0.42] * len(exc.columns),
                               figure_size=(5, 2), path_to_source=path_to_source, name='exc')
    day = analysis_text['Курсы. День'].drop('Unnamed: 0', axis=1).values.tolist()
    month = analysis_text['Курсы. Месяц'].drop('Unnamed: 0', axis=1).values.tolist()
    photo = open(png_path, 'rb')
    await message.answer('Да да - Вот оно:\nКурсы валют:')
    await __sent_photo_and_msg(message, photo, day, month)


# ['Металлы', 'сырьевые товары', 'commodities']
@dp.message_handler(commands=['metal'])
async def metal_info(message: types.Message):
    print('{} - {}'.format(message.from_user.full_name, message.text))
    transformer = dt.Transformer()
    metal = pd.read_excel('{}/tables/metal.xlsx'.format(path_to_source))
    metal = metal[['Metals', 'Price', 'Day', 'Weekly', 'Monthly', 'YoY']]
    metal = metal.rename(columns=({'Metals': 'Сырье', 'Price': 'Цена', 'Day': 'Δ День',
                                   'Weekly': 'Δ Неделя', 'Monthly': 'Δ Месяц', 'YoY': 'Δ Год'}))
    transformer.save_df_as_png(df=metal, column_width=[0.13] * len(metal.columns),
                               figure_size=(15.5, 4), path_to_source=path_to_source, name='metal')
    png_path = '{}/img/{}_table.png'.format(path_to_source, 'metal')
    day = analysis_text['Металлы. День'].drop('Unnamed: 0', axis=1).T.values.tolist()
    photo = open(png_path, 'rb')
    await message.answer('Да да - Вот оно:')
    await __sent_photo_and_msg(message, photo, day)


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
