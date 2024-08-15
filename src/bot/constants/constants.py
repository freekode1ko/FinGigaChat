"""Файл с основными константами для бота"""
import copy
import datetime

sample_of_news_title = '{}\n<i><a href="{}">{}</a></i>\n\n'
sample_of_img_title = '<b>{}</b>\nИсточник: {}\nДанные на <i>{}</i>'
sample_of_img_title_view = '<b>{}\n{}</b>\nДанные на <i>{}</i>'

handbook_prefix = '<b>{}</b>\n\n'

research_footer = 'Источник: SberCIB Investment Research. Распространение материалов за пределами Сбербанка запрещено'
GIGA_FOOTER = 'Ответ сгенерирован Gigachat. Информация требует дополнительной верификации.'

SELECTED = '✅'
UNSELECTED = '🟩'
DELETE_CROSS = '❌'
NEXT_PAGE = '➡'
PREV_PAGE = '⬅'
STOP = '⛔'

CANCEL_CALLBACK = 'cancel'

BACK_BUTTON_TXT = 'Назад'
END_BUTTON_TXT = 'Завершить'

# константы для RAG
DEFAULT_RAG_ANSWER = 'В базе знаний нет ответа на этот вопрос, обратитесь к команде проекта.'
COUNT_OF_USEFUL_LAST_MSGS = 5
KEEP_DIALOG_TIME = 60 * 30

TELEGRAM_MESSAGE_MAX_LEN = 4096
TELEGRAM_MESSAGE_CAPTION_MAX_LEN = 1024
TELEGRAM_MAX_MEDIA_ITEMS = 10

REGISTRATION_CODE_MIN = 100_000
REGISTRATION_CODE_MAX = 999_999
MAX_REGISTRATION_CODE_ATTEMPTS = 5  # макс кол-во попыток ввода кода пользователем при регистрации

GET_NEWS_PERIODS = [
    {
        'text': 'За 1 день',
        'days': 1,
    },
    {
        'text': 'За 3 дня',
        'days': 3,
    },
    {
        'text': 'За неделю',
        'days': 7,
    },
    {
        'text': 'За месяц',
        'days': 30,  # average
    },
]


EXTENDED_GET_NEWS_PERIODS = copy.deepcopy(GET_NEWS_PERIODS) + [
    {
        'text': 'За квартал',
        'days': 90,  # average
    },
    {
        'text': 'За полгода',
        'days': 176,  # average
    },
    {
        'text': 'За год',
        'days': 365 if datetime.date.today().year % 4 else 366,  # average
    },
]
