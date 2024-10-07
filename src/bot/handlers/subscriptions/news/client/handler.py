"""Файл с хендлерами подписок на новости по клиентам"""
from aiogram.fsm.state import State, StatesGroup

from db import models
from db.api.client import client_db
from db.api.user_client_subscription import user_client_subscription_db
from handlers.subscriptions.handler import router
from handlers.subscriptions.news.news_interface import ClientAndCommoditySubscriptionsHandler
from keyboards.subscriptions.news.client import callbacks
from keyboards.subscriptions.news.client.constructors import keyboard
from utils.decorators import singleton


class ClientSubscriptionsStates(StatesGroup):
    """Состояние для подписок по клиента"""

    client_user_subscriptions = State()


@singleton
class ClientSubscriptionsHandler(ClientAndCommoditySubscriptionsHandler):
    """Обработчик меню подписок на клиентов"""

    def __init__(self) -> None:
        """Инициализация обработчика меню подписок на клиентов"""
        super().__init__(
            router,
            client_db,
            user_client_subscription_db,
            callbacks,
            keyboard,
            ClientSubscriptionsStates.client_user_subscriptions,
            [models.ClientAlternative],
            'компании',
            'компаний',
            'компании',
        )


handler = ClientSubscriptionsHandler()
handler.setup()
