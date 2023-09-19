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
api_token = '6191720187:AAFF0SVqRi6J88NDSEhTctFN-QjwB0ekWjU'
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