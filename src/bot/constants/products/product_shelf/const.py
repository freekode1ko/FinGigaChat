from configs import config


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
        'pdf_path': None,
    },
    {
        'name': 'GM',
        'message_title': 'Продукты GM',
        'pdf_path': DATA_ROOT_PATH / 'GM_products',
    },
    {
        'name': 'ВЭД',
        'message_title': 'Продукты ВЭД',
        'pdf_path': None,
    },
    {
        'name': 'IB',
        'message_title': 'Продукты IB',
        'pdf_path': None,
    },
    {
        'name': 'Экосистема',
        'message_title': 'Продукты экосистемы',
        'pdf_path': None,
    },
    {
        'name': 'НКД',
        'message_title': 'Продукты НКД',
        'pdf_path': None,
    },
]
