from configs import config


TITLE = 'Продуктовая полка'

MENU = 'product_shelf_menu'

GET_PRODUCT_PDF = 'get_product_pdf'


DATA_ROOT_PATH = config.PATH_TO_SOURCES / 'products' / 'product_shelf'

PRODUCT_SHELF_DATA = [
    {
        'name': 'Кредитование',
        'message_title': 'Продукты кредитования',
        'pdf_path': DATA_ROOT_PATH / 'Crediting',
    },
    {
        'name': 'Пассивы',
        'message_title': 'Продукты пассивов',
        'pdf_path': DATA_ROOT_PATH / 'liabilities',
    },
    {
        'name': 'GM',
        'message_title': 'Продукты GM',
        'pdf_path': DATA_ROOT_PATH / 'GM_products',
    },
    {
        'name': 'ВЭД',
        'message_title': 'Продукты ВЭД',
        'pdf_path': DATA_ROOT_PATH / 'foreign_trade_activities',
    },
    {
        'name': 'Экосистема',
        'message_title': 'Продукты экосистемы',
        'pdf_path': DATA_ROOT_PATH / 'ecosystem',
    },
    {
        'name': 'Прочий НКД',
        'message_title': 'Прочие продукты НКД',
        'pdf_path': DATA_ROOT_PATH / 'accumulated_coupon_income',
    },
]
