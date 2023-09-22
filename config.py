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
api_token = '6558730131:AAELuoqsV5Ii1n6cO0iYWqh-lmCG9s9LLyc'
user_cred = ('oddryabkov', 'gEq8oILFVFTV') # ('nvzamuldinov', 'E-zZ5mRckID2')
research_cred = ('mpkartoshin@sberbank.ru', 'yf1P%3*%')

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
    'Вот текст:'
)

table_link = 'https://metals-wire.com/data'

charts_links = \
    {
        'metals_wire_link': 'https://metals-wire.com/api/v2/charts/symbol/history/name_name/?to=date_date&countBack=1825',
        'investing_link': 'https://api.investing.com/api/financialdata/name_name/historical/chart/?period=P5Y&interval=P1M&pointscount=120'
    }

dict_of_commodities = \
    {
        'Нефть Brent': {
            'links': ['CO1'],
            'to_take':4,
            'measurables': '$/бар',
            'naming': 'Brent',
            'alias':'Нефть'
        },
        'Нефть WTI': {
            'links': ['USCRWTIC'],
            'to_take':3,
            'measurables': '$/бар',
            'naming': 'WTI',
            'alias':'Нефть'
        },
        'Нефть Urals': {
            'links': ['1168084',
                  'https://www.investing.com/commodities/crude-oil-urals-spot-futures'],
            'to_take':1,
            'measurables': '$/бар',
            'naming': 'Urals',
            'alias':'Нефть'
        },
        'СПГ Япония/ Корея': {
            'links': ['JKL1'],
            'to_take':1,
            'measurables': '$/MMBTU',
            'naming': 'LNG Japan/Korea' ,
            'alias':'СПГ'
        },
        'Золото': {
            'links': ['XAU'],
            'to_take':4,
            'measurables': '$/унц',
            'naming': 'Gold spot',
            'alias':''
        },
        'Медь': {
            'links': ['LMCADY'],
            'to_take':4,
            'measurables': '$/т',
            'naming': 'Copper LME spot price',
            'alias':''  
        },
        'Алюминий': {
            'links': ['AHDY'],
            'to_take':4,
            'measurables': '$/т',
            'naming': 'Aluminium LME spot',
            'alias':''  
        },
        'Никель': {
            'links': ['LMNIDY'],
            'to_take':4,
            'measurables': '$/т',
            'naming': 'Nickel LME spot',
            'alias':''  
        },
        'Палладий': {
            'links': ['PALL'],
            'to_take':4,
            'measurables': '$/унц',
            'naming': 'Palladium LME spot',
            'alias':''  
        },
        'Платина': {
            'links': ['PLAT'],
            'to_take':4,
            'measurables': '$/унц',
            'naming': 'Platinum LME spot',
            'alias':''  
        },
        'Цинк': {
            'links': ['LMZSDY'],
            'to_take':4,
            'measurables': '$/т',
            'naming': 'Zinc LME spot',
            'alias':''  
        },
        'Свинец': {
            'links': ['LMPBDY'],
            'to_take':4,
            'measurables': '$/т',
            'naming': 'Lead LME spot',
            'alias':''  
        },
        'Серебро': {
            'links': ['SILV'],
            'to_take':4,
            'measurables': '$/унц',
            'naming': 'Silver spot',
            'alias':''  
        },
        'Кобальт': {
            'links': ['LMCODY'],
            'to_take':4,
            'measurables': '$/т',
            'naming': 'Cobalt LME spot',
            'alias':''  
        },
        'ЖРС': {
            'links': ['MB020424'],
            'to_take':4,
            'measurables': '$/т',
            'naming': 'Iron ore 62% Fe CFR China',
            'alias':''  
        },
        'Олово': {
            'links': ['LMSNDY'],
            'to_take':4,
            'measurables': '$/т',
            'naming': 'Tin LME spot',
            'alias':''  
        },
        'Уран': {
            'links': ['UXA1'],
            'to_take':3,
            'measurables': '$/фунт',
            'naming': 'Generic 1st UxC Uranium Price',
            'alias':''  
        },
        'Уголь Европа CIF ARA': {
            'links': ['CIFARA'],
            'to_take':3,
            'measurables': '$/т',
            'naming': '6,000kcal, CIF ARA',
            'alias':'Уголь'  
        },
        'Коксующийся уголь': {
            'links': ['AUHCC1D'],
            'to_take':3,
            'measurables': '$/т',
            'naming': 'HCC FOB Australia',
            'alias':''  
        },
        'Рулон г/к FOB Черное море': {
            'links': ['RUHRC2'],
            'to_take':3,
            'measurables': '$/т',
            'naming': 'HRC FOB Black Sea',
            'alias':'Сталь'  
        },
        'Чугун FOB Черное море': {
            'links': ['RUPIGIRON1'],
            'to_take':3,
            'measurables': '$/т',
            'naming': 'Pig Iron, FOB Black Sea',
            'alias':'Сталь'  
        },
        'Арматура РФ': {
            'links': ['RUREBAR1'],
            'to_take':3,
            'measurables': '$/т',
            'naming': 'Rebar, Russia domestic',
            'alias':'Сталь'  
        },
        'Лом РФ': {
            'links': ['RUSCRAP2'],
            'to_take':3,
            'measurables': '$/т',
            'naming': 'Scrap Russia domestic',
            'alias':'Сталь'  
        },
        'Cляб FOB Черное море': {
            'links': ['RUSLAB'],
            'to_take':3,
            'measurables': '$/т',
            'naming': 'Scrap FOB Black Sea',
            'alias':'Сталь'  
        },
        'Электроэнергия в РФ (Европа)': {
            'links': ['RUelectricityEurope'],
            'to_take':3,
            'measurables': 'руб/MWh',
            'naming': 'Electricity price Russia - Europe',
            'alias':'Электроэнергия'  
        },
        'Электроэнергия в РФ (Сибирь)': {
            'links': ['RUelectricitySiberia'],
            'to_take':3,
            'measurables': 'руб/MWh',
            'naming': 'Electricity price Russia - Siberia',
            'alias':'Электроэнергия'  
        },
        'Аммиак': {
            'links': ['AR96530000'],
            'to_take':3,
            'measurables': '$/т',
            'naming': 'Ammonia, CFR Tampa',
            'alias':''  
        },
        'Газ': {
            'links': ['https://charts.profinance.ru/html/charts/image?SID=kI1Jhn93&s=TTFUSD1000&h=480&w=640&pt=2&tt=10&z=7&ba=2&nw=728'],
            'measurables': '$/тыс м3',
            'naming': 'Gas',
            'alias':''   
        },
    }
