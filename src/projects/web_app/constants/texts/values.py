"""Значения по умолчанию для всех констант из Redis, которые используются в WebApp"""
import json

DEFAULT_VALUES = {
    # AUTH
    'AUTH_EMAIL_TEXT': (
        'Добрый день!\n\n'
        'Вы получили данное письмо, потому что указали данный адрес при авторизации в веб-версии терминала AI-помощника Банкира.\n\n'
        'Код для завершения авторизации:\n\n{code}\n'
        'Никому не сообщайте этот код.'
    ),

    # WATERMARK
    'FONT_TYPE': 'Helvetica',
    'FONT_SIZE': 20,
    'ROTATION': 45,
    'FONT_COLOR_ALPHA': 0.3,
    'VERTICAL_REPETITIONS': 3,
    'HORIZONTAL_REPETITIONS': 3,

    # SPECIAL DASHBOARD
    # По ключу идет название кастомной секции, по значению список с котировками
    # из БД вида "название котировки:название секции"
    'SPECIAL_DASHBOARD': json.dumps(
        {
            'FX': (
                'Китайский юань:Котировки (ЦБ)',
                'Доллар США:Котировки (ЦБ)',
                'Евро:Котировки (ЦБ)',
            ),
            'Commodities': (
                'Brent USD/Bbl:Энергетика (TradingEconomics)',
                'Gold USD/t.oz:Металлы (TradingEconomics)',
                'Copper USD/Lbs:Металлы (TradingEconomics)',
            ),
            'Облигации': (
                'Россия 2-летние:Облигации (Investing)',
                'Россия 5-летние:Облигации (Investing)',
                'Россия 10-летние:Облигации (Investing)',
            ),
            'Индексы': (
                'S&P 500:Индексы (Yahoo)',
                'NASDAQ Composite:Индексы (Yahoo)',
                'Bitcoin USD:Криптовалюты (Yahoo)',
            ),
        }
    )
}
