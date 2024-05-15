from aiogram.fsm.state import StatesGroup, State

from db import models
from db.api.commodity import commodity_db
from db.api.user_commodity_subscription import user_commodity_subscription_db
from handlers.subscriptions.handler import router
from handlers.subscriptions.news.news_interface import NewsHandler
from keyboards.subscriptions.news.commodity import callbacks
from keyboards.subscriptions.news.commodity.constructors import keyboard


class CommoditySubscriptionsStates(StatesGroup):
    commodity_user_subscriptions = State()


handler = NewsHandler(
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
handler.setup()
