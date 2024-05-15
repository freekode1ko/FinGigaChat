from aiogram.fsm.state import StatesGroup, State

from db.api.industry import industry_db
from db.api.user_industry_subscription import user_industry_subscription_db
from db.models import IndustryAlternative
from handlers.subscriptions.handler import router
from handlers.subscriptions.news.news_interface import NewsHandler
from keyboards.subscriptions.news.industry import callbacks
from keyboards.subscriptions.news.industry.constructors import keyboard


class IndustrySubscriptionsStates(StatesGroup):
    industry_user_subscriptions = State()


handler = NewsHandler(
    router,
    industry_db,
    user_industry_subscription_db,
    callbacks,
    keyboard,
    IndustrySubscriptionsStates.industry_user_subscriptions,
    [IndustryAlternative],
    'отрасли',
    'отраслей',
    'отрасли',
)
handler.setup()
