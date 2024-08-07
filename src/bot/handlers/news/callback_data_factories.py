"""
Уровни меню новостей и данные для этого меню.

Енумератор хардкод кнопок NewsItems.
Уровни меню новостей.
Фабрики колбэк данных.

тг группы (из БД)
...
клиент новости (хардкод)
сырье новости (хардкод)


тг группа без флага ведет в выбор тг каналов
с флагом ведет в выбор telegram_section

tg section дает выбор - тг каналы или внешние источники (если тг каналов нет, то сразу выбор периода)

клиенты и сырье дают выбор поиска из подписок или остальных, после выбора клиента или сырья - выбор периода
"""
from enum import auto, IntEnum
from typing import Optional

from aiogram.filters.callback_data import CallbackData

from constants.enums import AutoEnum
from db.api.client import client_db
from db.api.commodity import commodity_db
from db.api.industry import industry_db
from db.api.subject_interface import SubjectInterface
from db.api.subscriptions_interface import SubscriptionInterface
from db.api.telegram_channel import telegram_channel_article_db
from db.api.user_client_subscription import user_client_subscription_db
from db.api.user_commodity_subscription import user_commodity_subscription_db

MENU = 'news'


class NewsItems(AutoEnum):
    """
    Класс с хардкод кнопками для получения новостей

    В качестве значения енумератора передается dict,
    для заданных атрибутов с декоратором property вынимаются значения этого dict.
    """

    def __init__(self, *args) -> None:
        """
        Инициализация енумератора.

        Атрибуты:
        - титул,
        - имя субъекта в винительном и родительном падежах,
        - кнопки,
        - интерфейсы.
        """
        if len(args) > 0 and isinstance(args[0], dict):
            self._title_ = args[0].get('title', self._name_)
            self._subject_name_ = args[0].get('subject_name', self._name_)
            self._subject_name_genitive_ = args[0].get('subject_name_genitive', self._name_)
            self._buttons_ = args[0].get('buttons', [])
            self._subject_db_ = args[0].get('subject_db')
            self._subject_subscription_db_ = args[0].get('subject_subscription_db')

    @property
    def title(self) -> str:
        """Возврат атрибута титула"""
        return self._title_

    @property
    def subject_name(self) -> str:
        """Возврат атрибута имени субъекта в винительном падеже"""
        return self._subject_name_

    @property
    def subject_name_genitive(self) -> str:
        """Возврат атрибута имени субъекта в родительном падеже"""
        return self._subject_name_genitive_

    @property
    def buttons(self) -> list[dict]:
        """Возврат атрибута кнопок"""
        return self._buttons_

    @property
    def subject_db(self) -> SubjectInterface:
        """Возврат атрибута интерфейса субъекта"""
        return self._subject_db_

    @property
    def subject_subscription_db(self) -> SubscriptionInterface:
        """Возврат атрибута интерфейса подписок"""
        return self._subject_subscription_db_

    clients = {
        'title': 'Новости по клиентам',
        'subject_name': 'клиента',
        'subject_name_genitive': 'клиента',
        'subject_db': client_db,
        'subject_subscription_db': user_client_subscription_db,
        'buttons': [
            {
                'text': 'Выбрать клиента из моих подписок',
                'subscribed': True,
            },
            {
                'text': 'Выбрать другого клиента',
                'subscribed': False,
            },
        ],
    }
    commodities = {
        'title': 'Новости по commodities',
        'subject_name': 'сырьевой товар',
        'subject_name_genitive': 'сырьевого товара',
        'subject_db': commodity_db,
        'subject_subscription_db': user_commodity_subscription_db,
        'buttons': [
            {
                'text': 'Выбрать сырьевой товар из моих подписок',
                'subscribed': True,
            },
            {
                'text': 'Выбрать другой сырьевой товар',
                'subscribed': False,
            },
        ],
    }


class SubjectsInterfaces(AutoEnum):
    """Интерфейсы для получения новостей"""

    def __init__(self, *args) -> None:
        """Инициализация енумератора с атрибутом-интерфейсом субъекта"""
        if len(args) > 0 and isinstance(args[0], SubjectInterface):
            self._interface_ = args[0]

    @property
    def interface(self) -> SubjectInterface:
        """Возврат атрибута интерфейса субъекта"""
        return self._interface_

    clients = client_db
    commodities = commodity_db
    telegram = telegram_channel_article_db
    industry = industry_db


class NewsMenusEnum(IntEnum):
    """Уровни меню клиенты"""

    main_menu = auto()
    end_menu = auto()

    # переход из main_menu
    choose_telegram_subjects = auto()   # для тг групп (отображение зависит от флага у группы)
    choose_subs_or_unsubs = auto()      # выбор из подписок или остальных

    # переход из выбора отрасли в тг группе
    choose_source_group = auto()        # tg каналы или внешние источники

    # Переход из choose_subs_or_unsubs (поиск или выбор)
    subjects_list = auto()              # subs group items or unsubs group items for client, commodity

    # Переход из choose_source_group
    telegram_channels_by_section = auto()

    # переход из субъекта в выбор периода (из choose_telegram_subjects, subjects_list)
    choose_period_for_subject = auto()   # для клиента или сырья
    choose_period_for_telegram = auto()  # для тг каналов и отраслей

    # Переход из choose_period
    news_by_period = auto()             # выдача новостей за период
    industry_news_by_period = auto()             # выдача новостей за период

    # меню для стейкхолдеров
    choose_stakeholder_clients = auto()  # выбор клиентов стейкхолдера
    show_news = auto()  # выдача новостей по выбранным клиентам


class NewsMenuData(CallbackData, prefix=MENU):
    """Меню новости"""

    menu: NewsMenusEnum
    back_menu: NewsMenusEnum = NewsMenusEnum.main_menu
    days_count: int = 1
    subject_ids: str = '0'
    interface: Optional[SubjectsInterfaces] = None


class TelegramGroupData(NewsMenuData, prefix=MENU):
    """
    При выборе тг группы в меню новостей, мы можем либо получить новости из тг каналов, либо из внеш источников

    Внеш источники есть только в отраслевых новостях (там же флаг is_show_all_channels)
    """

    telegram_group_id: int
    telegram_section_id: int = 0
    telegram_channel_id: int = 0
    is_external_sources: bool = False


class SubjectData(NewsMenuData, prefix=MENU):
    """Выгрузка новостей по клиентам или сырьевых товарам"""

    subject: NewsItems
    subscribed: bool = True
    page: int = 0
    subject_id: int = 0


class StakeholderData(NewsMenuData, prefix=MENU):
    """Выгрузка новостей по стейкхолдерам."""

    stakeholder_id: int = 0
    selected_ids: int = 0
    subject_id: int = 0
    get_all: bool = False
