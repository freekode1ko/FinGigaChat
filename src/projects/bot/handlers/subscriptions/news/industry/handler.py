"""Файл с хендлерами подписок на новости по отраслям"""
from aiogram.fsm.state import State, StatesGroup

from db import models
from db.api.industry import industry_db
from db.api.user_industry_subscription import user_industry_subscription_db
from handlers.subscriptions.handler import router
from handlers.subscriptions.news.news_interface import NewsHandler
from keyboards.subscriptions.news.industry import callbacks
from keyboards.subscriptions.news.industry.constructors import keyboard


class IndustrySubscriptionsStates(StatesGroup):
    """Состояние для подписок по отраслям"""

    industry_user_subscriptions = State()


handler = NewsHandler(
    router,
    industry_db,
    user_industry_subscription_db,
    callbacks,
    keyboard,
    IndustrySubscriptionsStates.industry_user_subscriptions,
    [models.IndustryAlternative],
    'отрасли',
    'отраслей',
    'отрасли',
)
handler.setup()
