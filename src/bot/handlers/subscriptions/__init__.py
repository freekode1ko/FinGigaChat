from aiogram import Router

from handlers.subscriptions import (
    news_subscriptions_menu,
    research_subscriptions_menu,
    telegram_subscriptions_menu,
)

routers: list[Router] = [
    news_subscriptions_menu.router,
    telegram_subscriptions_menu.router,
    research_subscriptions_menu.router,
]
