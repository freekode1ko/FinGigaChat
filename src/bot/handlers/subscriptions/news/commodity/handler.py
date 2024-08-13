"""Хендлеры подписок на новости сырьевые товары"""
from aiogram.fsm.state import State, StatesGroup

from db import models
from db.api.commodity import commodity_db
from db.api.user_commodity_subscription import user_commodity_subscription_db
from handlers.subscriptions.handler import router
from handlers.subscriptions.news.news_interface import ClientAndCommoditySubscriptionsHandler
from keyboards.subscriptions.news.commodity import callbacks
from keyboards.subscriptions.news.commodity.constructors import keyboard


class CommoditySubscriptionsStates(StatesGroup):
    """Состояние для подписок по сырьевым товарам"""

    commodity_user_subscriptions = State()


class CommoditySubscriptionsHandler(ClientAndCommoditySubscriptionsHandler):  # FIXME add singleton
    """Обработчик меню подписок на сырье"""

    def __init__(self) -> None:
        """Инициализация обработчика меню подписок на сырье"""
        super().__init__(
            router,
            commodity_db,
            user_commodity_subscription_db,
            callbacks,
            keyboard,
            CommoditySubscriptionsStates.commodity_user_subscriptions,
            [models.CommodityAlternative],
            'сырьевые товары',
            'сырьевых товаров',
            'сырьевые товары',
        )


handler = CommoditySubscriptionsHandler()
handler.setup()
