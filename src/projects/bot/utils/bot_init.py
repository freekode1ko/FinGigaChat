import datetime
import time
from typing import Any, Callable

import pandas as pd
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from configs import config
from constants.commands import PUBLIC_COMMANDS
from db.database import async_session as async_session_maker, engine
from handlers import (
    admin,
    ai,
    analytics,
    call_reports,
    clients,
    commodity,
    common,
    news,
    products,
    quotes,
    referencebook,
    subscriptions,
    telegram_sections
)
from log.bot_logger import logger, user_logger
from middlewares.db import DatabaseMiddleware
from middlewares.logger import LoggingMiddleware
from middlewares.state import StateMiddleware
from utils.base import (
    next_weekday_time,
    wait_until
)
from utils.bot import bot


storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def passive_newsletter(
        newsletter_weekday: int,
        newsletter_hour: int,
        newsletter_minute: int,
        newsletter_executor: Callable,
        newsletter_info: str,
        apscheduler: AsyncIOScheduler,
        **kwargs: Any,
) -> None:
    """
    Рассылка производится в newsletter_weekday день недели, в newsletter_hour:newsletter_minute

    :param newsletter_weekday: день недели, в который производим рассылку 0-6 (0 - пн, 6 - вс), -1 = каждый день
    :param newsletter_hour: час, в который производим рассылку
    :param newsletter_minute: минута, в которую производим рассылку
    :param newsletter_executor: Исполнитель рассылки
    :param newsletter_info: Подпись, какая рассылка производится
    :param apscheduler: Планировщик, который производит рассылку отчетов по CIB Research
    :param kwargs: доп параметры для рассылки
    """
    while True:
        now = datetime.datetime.now()
        next_newsletter_datetime = next_weekday_time(now, newsletter_weekday, newsletter_hour, newsletter_minute)
        newsletter_dt_str = next_newsletter_datetime.strftime(config.INVERT_DATETIME_FORMAT)
        await wait_until(next_newsletter_datetime)
        apscheduler.pause()
        logger.info(f'Начинается рассылка новостей в {newsletter_dt_str} по {newsletter_info}')

        start_tm = time.time()
        # получим справочник пользователей (в цикле, потому что справочник может пополняться)
        user_df = pd.read_sql_query('SELECT user_id, username FROM registered_user', con=engine)

        kwargs['newsletter_start_datetime'] = next_newsletter_datetime
        await newsletter_executor(bot, user_df, **kwargs)

        work_time = time.time() - start_tm
        users_cnt = len(user_df)
        logger.info(
            f'Рассылка в {newsletter_dt_str} для {users_cnt} пользователей успешно завершена за {work_time:.3f} секунд. '
            f'Переходим в ожидание следующей рассылки.'
        )
        apscheduler.resume()


async def set_bot_commands() -> None:
    """Выставление команд в боте"""
    commands = []

    for command in PUBLIC_COMMANDS:
        commands.append(BotCommand(command=f'/{command["command"]}', description=command['description']))

    await bot.delete_my_commands()
    await bot.set_my_commands(commands)


async def start_bot():
    """Функция для запуска бота"""
    # Устанавливаем список актуальных команд
    await set_bot_commands()

    # запускаем бота
    dp.include_routers(
        common.router,
        admin.router,
        quotes.router,
        subscriptions.router,
        ai.router,
        call_reports.router,
        referencebook.router,
        telegram_sections.router,
        analytics.router,
        products.router,
        clients.router,
        commodity.router,
        news.router,
    )
    # Добавляем мидлварю для работы с БД
    dp.update.middleware(DatabaseMiddleware(session_maker=async_session_maker))
    # Добавляем мидлварю для логирования
    dp.update.middleware(LoggingMiddleware(logger=logger, db_logger=user_logger))
    # Добавляем мидлварю для снятия состояния спустя N кол-во минут неактивности пользователя
    dp.update.middleware(StateMiddleware())

    # Отключаем обработку сообщений, которые прислали в период, когда бот был выключен
    await bot.set_webhook(config.WEBHOOK_FULL_URL)