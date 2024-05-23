"""
Предоставляет интерфейс для взаимодействия с подписками на сырьевые товары.
Позволяет выполнять стандартные операции для работы с подписками
"""
from db.api.subscriptions_interface import SubscriptionInterface
from db import models


user_commodity_subscription_db = SubscriptionInterface(models.UserCommoditySubscriptions, 'commodity_id', models.Commodity)
