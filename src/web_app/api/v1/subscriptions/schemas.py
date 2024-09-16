from enum import Enum
from typing import Optional

from pydantic import BaseModel


class SubscriptionTypeEnum(str, Enum):
    """Типы подписок"""

    clients = 'clients'  # Клиенты
    commodity = 'commodity'  # Сырьевые товары
    industry = 'industry'  # Отрасли
    tg_channels = 'tg_channels'  # ТГ каналы
    analytics_reports = 'analytics_reports'  # Аналитические отчеты


class Subscription(BaseModel):
    """Меню подписок"""

    name: str
    subscription_id: Optional[int] = None
    subscription_type: Optional[SubscriptionTypeEnum] = None
    is_subscribed: Optional[bool] = None
    nearest_menu: list['Subscription'] = []


class DetailSubscriptionsResponse(BaseModel):
    """Схема для отображения детализированной аналитики"""

    subscription_id: int
    name: str
    subscriptions: list[Subscription]
