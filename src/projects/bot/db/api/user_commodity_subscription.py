"""
Предоставляет интерфейс для взаимодействия с подписками на сырьевые товары.

Позволяет выполнять стандартные операции для работы с подписками
"""
from db import models
from db.api.subscriptions_interface import IndustryChildrenSubscriptionInterface


user_commodity_subscription_db = IndustryChildrenSubscriptionInterface(
    models.UserCommoditySubscriptions,
    'commodity_id',
    models.Commodity,
    [models.Commodity.name],
)
