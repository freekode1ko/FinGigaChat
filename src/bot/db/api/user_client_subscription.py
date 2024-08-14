"""
Предоставляет интерфейс для взаимодействия с подписками на клиентов.

Позволяет выполнять стандартные операции для работы с подписками
"""
from db import models
from db.api.subscriptions_interface import IndustryChildrenSubscriptionInterface


user_client_subscription_db = IndustryChildrenSubscriptionInterface(
    models.UserClientSubscriptions,
    'client_id',
    models.Client,
    [models.Client.name],
)
