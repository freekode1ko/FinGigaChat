from configs import config


MENU = 'product_shelf_menu'

GET_PRODUCT_PDF = 'get_product_pdf'


DATA_ROOT_PATH = config.PATH_TO_SOURCES / 'products' / 'product_shelf'

PRODUCT_SHELF_DATA = [
    {
        'name': 'Кредитование',
        'pdf_path': DATA_ROOT_PATH / 'crediting',
    },
    {
        'name': 'Пассивы',
        'pdf_path': None,
    },
    {
        'name': 'GM',
        'pdf_path': DATA_ROOT_PATH / 'GM_products',
    },
    {
        'name': 'ВЭД',
        'pdf_path': None,
    },
    {
        'name': 'IB',
        'pdf_path': None,
    },
    {
        'name': 'Экосистема',
        'pdf_path': None,
    },
    {
        'name': 'НКД',
        'pdf_path': None,
    },
]
