user_agents = \
    [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 '
        'Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 '
        'Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 '
        'Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 '
        'Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 '
        'Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) '
        'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 '
        'Safari/605.1.15',
    ]

list_of_companies = \
    [
        ['831', 'Полиметалл',
         'https://www.polymetalinternational.com/ru/investors-and-media/reports-and-results/result-centre/'],
        ['675', 'ММК', 'https://mmk.ru/ru/press-center/news/operatsionnye-rezultaty-gruppy-mmk-za-1-kvartal-2023-g/'],
        ['689', 'Норникель', 'https://www.nornickel.ru/investors/disclosure/financials/#accordion-2022'],
        ['827', 'Полюс', 'https://polyus.com/ru/investors/results-and-reports/'],
        ['798', 'Русал', 'https://rusal.ru/investors/financial-stat/annual-reports/'],
        ['714', 'Северсталь', 'https://severstal.com/rus/ir/indicators-reporting/operational-results/']
    ]

chat_base_url = 'https://beta.saluteai.sberdevices.ru/v1/'
research_base_url = 'https://research.sberbank-cib.com/'
data_market_base_url = 'https://markets.tradingeconomics.com/'
path_to_source = './sources'
user_cred = ('oddryabkov', 'gEq8oILFVFTV')  # ('nvzamuldinov', 'E-zZ5mRckID2')
api_key_gpt = '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'
research_cred = ('annekrasov@sberbank.ru', 'GfhjkmGfhjkm1')

# api_token = '6191720187:AAFF0SVqRi6J88NDSEhTctFN-QjwB0ekWjU'  # PROM
api_token = '6558730131:AAELuoqsV5Ii1n6cO0iYWqh-lmCG9s9LLyc'  # DEV

psql_engine = 'postgresql://bot:12345@0.0.0.0:5432/users'

CLIENT_NAME_PATH = 'data/name/client_name.csv'
COMMODITY_NAME_PATH = 'data/name/commodity_name.csv'
CLIENT_ALTERNATIVE_NAME_PATH = 'data/name/client_with_alternative_names.xlsx'
COMMODITY_ALTERNATIVE_NAME_PATH = 'data/name/commodity_with_alternative_names.xlsx'
CLIENT_ALTERNATIVE_NAME_PATH_FOR_UPDATE = 'data/name/client_alternative.csv'
BASE_GIGAPARSER_URL = 'http://gigaparsernews.ru:8000/{}'

mail_username = "ai-helper@mail.ru"
mail_password = "ExamKejCpmcpr8kM5emw"
mail_imap_server = "imap.mail.ru"
summarization_prompt = (
    'Ты - суммаризатор новостной ленты.'
    'На вход тебе будут подаваться новости.'
    'Твоя задача - суммаризировать новость.'
    ''
    'Формат ответа:'
    '- суммаризация не должна быть слишком длинной;'
    '- тезисы должны быть лаконичными;'
    '- основная мысль не должна искажаться;'
    '- любые факты, которых не было в оригинальной статье, недопустимы;'
    '- нельзя использовать вводные слова, только текст суммаризации.'
    ''
    'ВАЖНО! Игнорировать формат ответа нельзя! Все условия должны соответствовать формату ответа!'
    ''
    '________________'
    'Твой ответ:'
)


help_text = ('Всем привет! Мы начинаем пилотирование MVP AI-помощника банкира на ограниченной выборке ГКМ, старших '
             'банкиров и руководителей.\n\n'
             'В боте можно посмотреть аналитику CIB Research, текущие и прогнозные котировки и данные по макроэкономике,'
             ' FI, FX, сырьевым товарам воспользовавшись командами из бокового меню или ввести ключевые слова '
             '(экономика, валюты, ОФЗ, металлы, нефть, инфляция, КС, ВВП, бюджет, юань и тд).\n\n'
             'Для просмотра новостного потока по клиентам необходимо ввести название клиента («Роснефть», «Магнит», '
             '«Уралхим» и тд) - в настоящее время доступен сервис по 250 именам. По публичным клиентам доступны '
             'также исторические и прогнозные финансовые показатели.  Аналогичный новостной функционал, а также '
             'динамика котировок доступны по ключевым commodities.\n\n'
             'Кроме того, в боте вы можете пообщаться с Гигачатом в свободной форме, попросив написать письмо, сделать '
             'самари, перевести текст и тд.\n\n'
             'В ближайших планах: расширение функционала в части отраслевой аналитики, персонализация под ГКМ и '
             'настройка пассивного контента (настройка рассылки), инфо по законодательству, госпраммам и многое другое!\n\n'
             'В перспективе рассматриваем варианты заведения колл репортов через этот бот и интеграцию с контуром '
             'альфа (тут есть ограничения по безопасности, но мы не сдаемся и ищем варианты:)\n\n'
             'Бот постоянно совершенствуется и дообучается, поэтому присылайте, пожалуйста, обратную связь по контенту, '
             'функционалу и новым идеям Максиму Королькову @korolkov_m и Александру Юдину.')

table_link = 'https://metals-wire.com/data'

charts_links = \
    {
        'metals_wire_link': 'https://metals-wire.com/api/v2/charts/symbol/history/name_name/'
                            '?to=date_date&countBack=1825',
        'investing_link': 'https://api.investing.com/api/financialdata/name_name/historical/chart/'
                          '?period=P5Y&interval=P1M&pointscount=120'
    }

dict_of_commodities = \
    {
        'Нефть Brent, $/бар': {
            'links': ['CO1'],
            'to_take': 4,
            'measurables': '$/бар',
            'naming': 'Brent',
            'alias': 'Нефть'
        },
        'Нефть WTI, $/бар': {
            'links': ['8849',
                      'https://ru.investing.com/commodities/crude-oil'],
            'to_take': 1,
            'measurables': '$/бар',
            'naming': 'WTI',
            'alias': 'Нефть'
        },
        'Нефть Urals, $/бар': {
            'links': ['1168084',
                      'https://www.investing.com/commodities/crude-oil-urals-spot-futures'],
            'to_take': 1,
            'measurables': '$/бар',
            'naming': 'Urals',
            'alias': 'Нефть'
        },
        'СПГ Япония/Корея, $/MMBTU': {
            'links': ['JKL1'],
            'to_take': 1,
            'measurables': '$/MMBTU',
            'naming': 'LNG Japan/Korea',
            'alias': 'СПГ'
        },
        'Золото спот, $/унц': {
            'links': ['XAU'],
            'to_take': 4,
            'measurables': '$/унц',
            'naming': 'Gold spot',
            'alias': 'золото'

        },
        'Медь LME спот, $/т': {
            'links': ['LMCADY'],
            'to_take': 4,
            'measurables': '$/т',
            'naming': 'Copper LME spot price',
            'alias': 'медь'

        },
        'Алюминий LME спот, $/т': {
            'links': ['AHDY'],
            'to_take': 4,
            'measurables': '$/т',
            'naming': 'Aluminium LME spot',
            'alias': 'алюминий'

        },
        'Никель LME спот, $/т': {
            'links': ['LMNIDY'],
            'to_take': 4,
            'measurables': '$/т',
            'naming': 'Nickel LME spot',
            'alias': 'никель'

        },
        'Палладий LME спот, $/унц': {
            'links': ['PALL'],
            'to_take': 4,
            'measurables': '$/унц',
            'naming': 'Palladium LME spot',
            'alias': 'палладий'
        },
        'Платина LME спот, $/унц': {
            'links': ['PLAT'],
            'to_take': 4,
            'measurables': '$/унц',
            'naming': 'Platinum LME spot',
            'alias': 'платина'
        },
        'Цинк LME спот, $/т': {
            'links': ['LMZSDY'],
            'to_take': 4,
            'measurables': '$/т',
            'naming': 'Zinc LME spot',
            'alias': 'цинк'

        },
        'Свинец LME спот, $/т': {
            'links': ['LMPBDY'],
            'to_take': 4,
            'measurables': '$/т',
            'naming': 'Lead LME spot',
            'alias': 'свинец'
        },
        'Серебро спот, $/унц': {
            'links': ['SILV'],
            'to_take': 4,
            'measurables': '$/унц',
            'naming': 'Silver spot',
            'alias': 'серебро'
        },
        'Кобальт LME спот, $/т': {
            'links': ['LMCODY'],
            'to_take': 4,
            'measurables': '$/т',
            'naming': 'Cobalt LME spot',
            'alias': 'кобальт'
        },
        'Железная руда 62% Fe CFR Китай, $/т': {
            'links': ['MB020424'],
            'to_take': 4,
            'measurables': '$/т',
            'naming': 'Iron ore 62% Fe CFR China',
            'alias': 'жрс'
        },
        'Олово LME spot, $/т': {
            'links': ['LMSNDY'],
            'to_take': 4,
            'measurables': '$/т',
            'naming': 'Tin LME spot',
            'alias': 'олово'
        },
        'Уран Generic 1st UxC, $/фунт': {
            'links': ['UXA1'],
            'to_take': 3,
            'measurables': '$/фунт',
            'naming': 'Generic 1st UxC Uranium Price',
            'alias': 'уран'
        },
        'Энергетический уголь 6 000kcal, CIF ARA, $/т': {
            'links': ['CIFARA'],
            'to_take': 3,
            'measurables': '$/т',
            'naming': '6,000kcal, CIF ARA',
            'alias': 'Уголь'
        },
        'Коксующийся уголь, FOB Australia, $/т': {
            'links': ['AUHCC1D'],
            'to_take': 3,
            'measurables': '$/т',
            'naming': 'HCC FOB Australia',
            'alias': 'коксующийся уголь'
        },
        'Рулон г/к FOB Черное море, $/т': {
            'links': ['RUHRC2'],
            'to_take': 3,
            'measurables': '$/т',
            'naming': 'HRC FOB Black Sea',
            'alias': 'Сталь'
        },
        'Чугун FOB Черное море, $/т': {
            'links': ['RUPIGIRON1'],
            'to_take': 3,
            'measurables': '$/т',
            'naming': 'Pig Iron, FOB Black Sea',
            'alias': 'Сталь'
        },
        'Арматура РФ, $/т': {
            'links': ['RUREBAR1'],
            'to_take': 3,
            'measurables': '$/т',
            'naming': 'Rebar, Russia domestic',
            'alias': 'Сталь'
        },
        'Лом РФ, $/т': {
            'links': ['RUSCRAP2'],
            'to_take': 3,
            'measurables': '$/т',
            'naming': 'Scrap Russia domestic',
            'alias': 'Сталь'
        },
        'Cляб FOB Черное море, $/т': {
            'links': ['RUSLAB'],
            'to_take': 3,
            'measurables': '$/т',
            'naming': 'Scrap FOB Black Sea',
            'alias': 'Сталь'
        },
        'Электроэнергия в РФ (Европа)': {
            'links': ['RUelectricityEurope'],
            'to_take': 3,
            'measurables': 'руб/MWh',
            'naming': 'Electricity price Russia - Europe',
            'alias': 'Электроэнергия'
        },
        'Электроэнергия в РФ (Сибирь)': {
            'links': ['RUelectricitySiberia'],
            'to_take': 3,
            'measurables': 'руб/MWh',
            'naming': 'Electricity price Russia - Siberia',
            'alias': 'Электроэнергия'
        },
        'Аммиак, CFR Tampa, $/т': {
            'links': ['AR96530000'],
            'to_take': 3,
            'measurables': '$/т',
            'naming': 'Ammonia, CFR Tampa',
            'alias': 'аммиак'
        },
        'Газ, Natural Gas, $/тыс м3': {
            'links': [
                'https://charts.profinance.ru/html/charts/image'
                '?SID=kI1Jhn93&s=TTFUSD1000&h=480&w=640&pt=2&tt=10&z=7&ba=2&nw=728'],
            'measurables': '$/тыс м3',
            'naming': 'Gas',
            'alias': 'газ'
        },
    }

dict_of_companies = \
    {
        'Газпром': {
            'company_id': '656',
            'alias': 'Нефть и газ'
        },
        'Газпром нефть': {
            'company_id': '657',
            'alias': 'Нефть и газ'
        },
        'ЛУКойл': {
            'company_id': '673',
            'alias': 'Нефть и газ'
        },
        'НОВАТЭК': {
            'company_id': '690',
            'alias': 'Нефть и газ'
        },
        'Роснефть': {
            'company_id': '710',
            'alias': 'Нефть и газ'
        },
        'Татнефть': {
            'company_id': '722',
            'alias': 'Нефть и газ'
        },
        'Транснефть': {
            'company_id': '734',
            'alias': 'Нефть и газ'
        },
        'Полиметалл': {
            'company_id': '831',
            'alias': 'Металлургия'
        },
        'ММК': {
            'company_id': '675',
            'alias': 'Металлургия'
        },
        'НЛМК': {
            'company_id': '691',
            'alias': 'Металлургия'
        },
        'Норильский Никель': {
            'company_id': '689',
            'alias': 'Металлургия'
        },
        'Полюс': {
            'company_id': '827',
            'alias': 'Металлургия'
        },
        'РУСАЛ': {
            'company_id': '798',
            'alias': 'Металлургия'
        },
        'Северсталь': {
            'company_id': '714',
            'alias': 'Металлургия'
        },
        'Акрон': {
            'company_id': '640',
            'alias': 'Химическая промышленность'
        },
        'ФосАгро': {
            'company_id': '824',
            'alias': 'Химическая промышленность'
        },
        'TCS Group': {
            'company_id': '846',
            'alias': 'Финансовый сектор'
        },
        'Банк Санкт-Петербург': {
            'company_id': '750',
            'alias': 'Финансовый сектор'
        },
        'ВТБ': {
            'company_id': '744',
            'alias': 'Финансовый сектор'
        },
        'Московская биржа': {
            'company_id': '872',
            'alias': 'Финансовый сектор'
        },
        'Интер РАО': {
            'company_id': '781',
            'alias': 'Электроэнергетика'
        },
        'Мосэнерго': {
            'company_id': '682',
            'alias': 'Электроэнергетика'
        },
        'ОГК-2': {
            'company_id': '694',
            'alias': 'Электроэнергетика'
        },
        'РусГидро': {
            'company_id': '749',
            'alias': 'Электроэнергетика'
        },
        'ТГК-1': {
            'company_id': '723',
            'alias': 'Электроэнергетика'
        },
        'ЭЛ5 Энерго': {
            'company_id': '696',
            'alias': 'Электроэнергетика'
        },
        'Юнипро': {
            'company_id': '695',
            'alias': 'Электроэнергетика'
        },
        'Fix Price Group': {
            'company_id': '1437',
            'alias': 'Потребительский сектор'
        },
        'X5 Retail Group': {
            'company_id': '747',
            'alias': 'Потребительский сектор'
        },
        'Детский мир': {
            'company_id': '1404',
            'alias': 'Потребительский сектор'
        },
        'Лента': {
            'company_id': '1296',
            'alias': 'Потребительский сектор'
        },
        'М.Видео': {
            'company_id': '796',
            'alias': 'Потребительский сектор'
        },
        'Магнит': {
            'company_id': '674',
            'alias': 'Потребительский сектор'
        },
        'ОКЕЙ': {
            'company_id': '817',
            'alias': 'Потребительский сектор'
        },
        'Русагро': {
            'company_id': '832',
            'alias': 'Потребительский сектор'
        },
        'Эталон': {
            'company_id': '835',
            'alias': 'Недвижимость'
        },
        'ГК ПИК': {
            'company_id': '701',
            'alias': 'Недвижимость'
        },
        'ГК Самолет': {
            'company_id': '1441',
            'alias': 'Недвижимость'
        },
        'ЛСР': {
            'company_id': '778',
            'alias': 'Недвижимость'
        },
        'ХэдХантер': {
            'company_id': '1416',
            'alias': 'Интернет'
        },
        'Ozon': {
            'company_id': '1430',
            'alias': 'Интернет'
        },
        'VK': {
            'company_id': '819',
            'alias': 'Интернет'
        },
        'Whoosh': {
            'company_id': '1443',
            'alias': 'Интернет'
        },
        'Группа Позитив': {
            'company_id': '1440',
            'alias': 'Интернет'
        },
        'Яндекс': {
            'company_id': '821',
            'alias': 'Интернет'
        },
        'АФК Система': {
            'company_id': '718',
            'alias': 'Телекоммуникации'
        },
        'МТС': {
            'company_id': '686',
            'alias': 'Телекоммуникации'
        },
        'Ростелеком': {
            'company_id': '871',
            'alias': 'Телекоммуникации'
        },
        'Аэрофлот': {
            'company_id': '641',
            'alias': 'Транспорт'
        },
        'Глобалтранс': {
            'company_id': '771',
            'alias': 'Транспорт'
        },
        'Совкомфлот': {
            'company_id': '873',
            'alias': 'Транспорт'
        },
        'Сегежа': {
            'company_id': '1438',
            'alias': 'Промышленность'
        }
    }

industry_reviews = \
    {
        '1':'Нефть и газ',
        '2':'Металлургия',
        '3':'Химическая промышленность',
        '5':'Электроэнергетика',
        '6':'Потребительский индекс Иванова',
        '7':'Недвижимость',
        '10':'Железнодорожный транспорт'
    }

industry_base_url = 'https://research.sberbank-cib.com/group/guest/' \
        'equities?sector={}#cibViewReportContainer_cibequitypublicationsportlet_' \
        'WAR_cibpublicationsportlet_INSTANCE_gnfy_'
