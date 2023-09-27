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
research_cred = ('mpkartoshin@sberbank.ru', 'yf1P%3*%')

api_token = '6558730131:AAELuoqsV5Ii1n6cO0iYWqh-lmCG9s9LLyc'
psql_engine = 'postgresql://bot:12345@0.0.0.0:5432/users'

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

table_link = 'https://metals-wire.com/data'

charts_links = \
    {
        'metals_wire_link': 'https://metals-wire.com/api/v2/charts/symbol/history/name_name/?to=date_date&countBack=1825',
        'investing_link': 'https://api.investing.com/api/financialdata/name_name/historical/chart/?period=P5Y&interval=P1M&pointscount=120'
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
            'to_take':1,
            'measurables': '$/бар',
            'naming': 'WTI',
            'alias':'Нефть'
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
            'alias':'золото'

        },
        'Медь LME спот, $/т': {
            'links': ['LMCADY'],
            'to_take': 4,
            'measurables': '$/т',
            'naming': 'Copper LME spot price',
            'alias':'медь'  

        },
        'Алюминий LME спот, $/т': {
            'links': ['AHDY'],
            'to_take': 4,
            'measurables': '$/т',
            'naming': 'Aluminium LME spot',
            'alias':'алюминий'  

        },
        'Никель LME спот, $/т': {
            'links': ['LMNIDY'],
            'to_take': 4,
            'measurables': '$/т',
            'naming': 'Nickel LME spot',
            'alias':'никель'  

        },
        'Палладий LME спот, $/унц': {
            'links': ['PALL'],
            'to_take': 4,
            'measurables': '$/унц',
            'naming': 'Palladium LME spot',
            'alias':'палладий'  
        },
        'Платина LME спот, $/унц': {
            'links': ['PLAT'],
            'to_take': 4,
            'measurables': '$/унц',
            'naming': 'Platinum LME spot',
            'alias':'платина'  
        },
        'Цинк LME спот, $/т': {
            'links': ['LMZSDY'],
            'to_take': 4,
            'measurables': '$/т',
            'naming': 'Zinc LME spot',
            'alias':'цинк'  

        },
        'Свинец LME спот, $/т': {
            'links': ['LMPBDY'],
            'to_take': 4,
            'measurables': '$/т',
            'naming': 'Lead LME spot',
            'alias':'свинец'  
        },
        'Серебро спот, $/унц': {
            'links': ['SILV'],
            'to_take': 4,
            'measurables': '$/унц',
            'naming': 'Silver spot',
            'alias':'серебро'  
        },
        'Кобальт LME спот, $/т': {
            'links': ['LMCODY'],
            'to_take': 4,
            'measurables': '$/т',
            'naming': 'Cobalt LME spot',
            'alias':'кобальт'  
        },
        'Железная руда 62% Fe CFR Китай, $/т': {
            'links': ['MB020424'],
            'to_take': 4,
            'measurables': '$/т',
            'naming': 'Iron ore 62% Fe CFR China',
            'alias':'жрс'  
        },
        'Олово LME spot, $/т': {
            'links': ['LMSNDY'],
            'to_take': 4,
            'measurables': '$/т',
            'naming': 'Tin LME spot',
            'alias':'олово'  
        },
        'Уран Generic 1st UxC, $/фунт': {
            'links': ['UXA1'],
            'to_take': 3,
            'measurables': '$/фунт',
            'naming': 'Generic 1st UxC Uranium Price',
            'alias':'уран'  
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
            'alias':'коксующийся уголь'  
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
            'alias':'аммиак'  
        },
        'Газ, Natural Gas, $/тыс м3': {
            'links': [
                'https://charts.profinance.ru/html/charts/image?SID=kI1Jhn93&s=TTFUSD1000&h=480&w=640&pt=2&tt=10&z=7&ba=2&nw=728'],
            'measurables': '$/тыс м3',
            'naming': 'Gas',
            'alias':'газ'   
        },
    }
