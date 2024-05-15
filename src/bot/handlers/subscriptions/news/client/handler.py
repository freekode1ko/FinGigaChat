from aiogram.fsm.state import StatesGroup, State

from db.api.client import client_db
from db.api.user_client_subscription import user_client_subscription_db
from db.models import ClientAlternative
from handlers.subscriptions.handler import router
from handlers.subscriptions.news.news_interface import NewsHandler
from keyboards.subscriptions.news.client import callbacks
from keyboards.subscriptions.news.client.constructors import keyboard


class ClientSubscriptionsStates(StatesGroup):
    client_user_subscriptions = State()


handler = NewsHandler(
    router,
    client_db,
    user_client_subscription_db,
    callbacks,
    keyboard,
    ClientSubscriptionsStates.client_user_subscriptions,
    [ClientAlternative],
    'клиенты',
    'клиентов',
    'клиентов',
)
handler.setup()
