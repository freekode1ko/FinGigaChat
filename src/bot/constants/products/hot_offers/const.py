from configs import config


TITLE = '🔥Hot offers'

MENU = 'hot_offers_menu'
GET_HOT_OFFERS_PDF = 'get_hot_offers'

DATA_ROOT_PATH = config.PATH_TO_SOURCES / 'products' / 'hot_offers'

TABLE_DATA = [
    {
        'name': 'Кредитование',
        'message_title': 'Актуальные предложения по продуктам кредитования',
        'pdf_path': DATA_ROOT_PATH / 'Crediting',
    },
    {
        'name': 'Пассивы',
        'message_title': 'Актуальные предложения по продуктам пассивов',
        'pdf_path': DATA_ROOT_PATH / 'liabilities',
    },
    {
        'name': 'GM',
        'message_title': 'Актуальные предложения по продуктам GM',
        'pdf_path': DATA_ROOT_PATH / 'GM_products',
    },
    {
        'name': 'ВЭД',
        'message_title': 'Актуальные предложения по продуктам ВЭД',
        'pdf_path': DATA_ROOT_PATH / 'foreign_trade_activities',
    },
    {
        'name': 'Экосистема',
        'message_title': 'Актуальные предложения по продуктам экосистемы',
        'pdf_path': DATA_ROOT_PATH / 'ecosystem',
    },
    {
        'name': 'Прочий НКД',
        'message_title': 'Актуальные предложения по прочим продуктам НКД',
        'pdf_path': DATA_ROOT_PATH / 'accumulated_coupon_income',
    },
]
