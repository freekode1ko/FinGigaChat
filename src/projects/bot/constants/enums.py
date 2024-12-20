"""Файл с перечислениями"""

from __future__ import annotations

from enum import auto, Enum, IntEnum


class Environment(str, Enum):
    """Среда окружения, где запускаем код"""

    STAGE = 'dev'
    PROD = 'prod'
    LOCAL = 'local'
    UNKNOWN = 'unknown'

    def is_local(self) -> bool:
        """Является ли окружение локальным?"""
        return self in (Environment.UNKNOWN, Environment.LOCAL)

    @classmethod
    def from_str(cls, param: str) -> Environment:
        """Получить объект енумератора из переданной строки"""
        try:
            return cls(param.lower())
        except ValueError:
            return cls.UNKNOWN


class HTTPMethod(str, Enum):
    """Http методы."""

    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'


class RetrieverType(Enum):
    """Типы ретриверов в боте"""

    other = 0  # простое обращение к гигачат
    state_support = 1  # ретривер по господдержке
    qa_banker = 2  # ретривер по новостям и финансовым показателям


class ResearchSectionType(Enum):
    """Типы разделов CIB Research, участвует в формировании меню аналитики"""

    default = 0  # Раздел без доп пунктов
    economy = 1  # Раздел с прогнозом КС ЦБ и макроэконом показателями [витрина данных]
    financial_exchange = 2  # Раздел с прогнозом валютных курсов


class ResearchSummaryType(Enum):
    """Тип формирования сводки отчетов CIB Research, участвует в формировании меню аналитики"""

    periodic = 0  # Предлагает пользователю выгрузить отчеты за период
    last_actual = 1  # Выгружает последний актуальный отчет
    analytical_indicators = 2  # Формирует отдельное меню для выгрузки различных аналитических данных
    key_rate_dynamics_table = 3  # Выгрузка таблицы викли пульс с прогнозом КС ЦБ
    exc_rate_prediction_table = 4  # Выгрузка таблицы викли пульс с прогнозом валют
    data_mart = 5  # Выгрузка витрины данных
    economy_monthly = 6  # Выгрузка ежемесячных обзоров по экономике РФ
    economy_daily = 7  # Выгрузка ежедневных обзоров по экономике РФ


class FIGroupType(Enum):
    """Типы долговых рынков"""

    bonds = 0, 'ОФЗ'

    # obligates = 1, 'Корпоративные облигации '
    # foreign_markets = 2, 'Зарубежные рынки '

    def __init__(self, value, title):
        self._value_ = value
        self._title_ = title

    @property
    def title(self):
        """Получить тайтл"""
        return self._title_


class IndustryTypes(IntEnum):
    """Типы отраслей. Используется для меню отраслевой аналитики и для таблицы bot_industry_documents"""

    default = auto()            # Все стандартные отрасли
    other = auto()              # Пункт прочее
    general_comments = auto()   # Пункт общий комментарий


class SubjectType(str, Enum):
    """Типы объектов, по которым собираются новости."""

    client = 'client'
    commodity = 'commodity'
    industry = 'industry'


class AutoEnum(Enum):
    """
    Родительский класс, который позволяет задать атрибуты у значений енумератора.

    Атрибут value задается автоматически в зависимости от количества создаваемых значений енумератора.
    Тажке позволяет производить сравнение value енумератора с int и получать значения енумератора по передаваемому int.
    Например,

    >>> class Test(AutoEnum):
    ...    data1 = {'title': 'data1'}
    ...    data2 = {'title': 'data2'}

    >>> Test.data1 == '0'
    True
    >>> Test('0') == Test.data1
    True
    >>> Test.data1
    """

    def __new__(cls, *args):
        """При создании экземпляра енумератора из всех переданных аргументов, лишь первый станет value"""
        value = len(cls.__members__)
        obj = object.__new__(cls)
        obj._value_ = str(value)
        return obj

    def __eq__(self, obj) -> bool:
        """Оператор равенства"""
        if type(self) is type(obj):
            return super().__eq__(obj)
        return self.value == obj

    def __ne__(self, obj) -> bool:
        """Оператор неравенства"""
        if type(self) is type(obj):
            return super().__ne__(obj)
        return self.value != obj


class FinancialIndicatorsType(AutoEnum):
    """Типы фин показателей, которые можно получить"""

    def __init__(self, *args) -> None:
        """Инициализация енумератора с атрибутом - имя таблицы фин показателей"""
        if len(args) > 0 and isinstance(args[0], str):
            self._table_name_ = args[0]

    @property
    def table_name(self) -> str:
        """Возврат атрибута имя таблицы фин показателей"""
        return self._table_name_

    review_table = 'Обзор'
    pl_table = 'P&L'
    balance_table = 'Баланс'
    money_table = 'Денежный поток'


class FormatType(IntEnum):
    """Enum`сы форматов отправки файлов пользователю"""

    # Выдача общего текста группы и затем выдача группы файлов
    group_files = 1
    # Выдача общего текста группы, затем для каждого документа выдача сообщений:
    # document.name жирным
    # document.description просто текст
    # [document.file] если есть файл
    individual_messages = 2


class StakeholderType(str, Enum):
    """Тип того, кем является стейкхолдер для клиента."""

    lpr = 'лпр'
    beneficiary = 'бенефициар'
    undefined = 'не определено'


class FeatureType(str, Enum):
    """Перечень функционала в боте."""

    news = 'news'
    analytics_menu = 'analytics_menu'
    quotes_menu = 'quotes_menu'
    company_menu = 'company_menu'
    products_menu = 'products_menu'
    subscriptions_menu = 'subscriptions_menu'
    notes = 'notes'
    meeting = 'meeting'
    knowledgebase = 'knowledgebase'
    common = 'common'
    admin = 'admin'

    rag_research = 'rag_research'
    web_retriever = 'web_retriever'


class LinksType(str, Enum):
    """Тип ссылки."""

    subject_link = 'subject_link'  # ссылка на новость, содержащая новость об объекте (клиенте, коммоде и тд)
    tg_link = 'tg_link'  # ссылка на новость из тг-каналов, не относящаяся ни к чему (отрасли)


class QuotesType(str, Enum):
    """Кнопки в меню хэндлера quotes"""

    FX = 'fx'
    FI = 'fi'
    EQUITY = 'equity'
    COMMODITIES = 'commodities'
    ECO = 'eco'


class FileType(str, Enum):
    """Тип файла"""

    IMAGE = 'image'
    DOCUMENT = 'document'
    OTHER = 'other'
