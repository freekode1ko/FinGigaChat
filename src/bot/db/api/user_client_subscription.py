"""
Предоставляет интерфейс для взаимодействия с подписками на клиентов.

Позволяет выполнять стандартные операции для работы с подписками
"""
from db import models
from db.api.subscriptions_interface import SubscriptionInterface


user_client_subscription_db = SubscriptionInterface(
    models.UserClientSubscriptions,
    'client_id',
    models.Client,
    [models.Client.name],
)
