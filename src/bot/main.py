"""
Точка входа для запуска бота🤡
"""
import asyncio
import datetime
import time
import warnings
from typing import Callable, Any

import pandas as pd
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from configs import config, newsletter_config
from constants.commands import PUBLIC_COMMANDS
from db.database import engine, async_session as async_session_maker
from handlers import (
    admin, ai, analytics, common, telegram_sections, news, quotes, referencebook, subscriptions, products, call_reports, clients
)
from log.bot_logger import logger
from log.sentry import init_sentry
from middlewares.db import DatabaseMiddleware
from middlewares.logger import LoggingMiddleware
from utils.base import (
    next_weekday_time, wait_until,
)
from utils import newsletter, sessions

storage = MemoryStorage()
bot = Bot(token=config.api_token)
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
        user_df = pd.read_sql_query('SELECT user_id, username FROM whitelist', con=engine)

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
    commands = []

    for command in PUBLIC_COMMANDS:
        commands.append(BotCommand(command=f'/{command["command"]}', description=command['description']))

    await bot.delete_my_commands()
    await bot.set_my_commands(commands)


async def start_bot():
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
        news.router,
    )
    # Добавляем мидлварю для работы с БД
    dp.update.middleware(DatabaseMiddleware(session_maker=async_session_maker))
    # Добавляем мидлварю для логирования
    dp.update.middleware(LoggingMiddleware(logger=logger))

    # Отключаем обработку сообщений, которые прислали в период, когда бот был выключен
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def main():
    init_sentry(dsn=config.SENTRY_CHAT_BOT_DSN)
    warnings.filterwarnings('ignore')

    # запускам рассылки
    print('Инициализация бота')
    loop = asyncio.get_event_loop()

    scheduler = AsyncIOScheduler()
    # Каждые N минут (CIB_RESEARCH_NEWSLETTER_PARAMS) производится проверка на новые отчеты CIB Research в базе,
    # если есть новые отчеты -> рассылка
    scheduler.add_job(
        newsletter.send_new_researches_to_users,
        kwargs={'bot': bot},
        **newsletter_config.CIB_RESEARCH_NEWSLETTER_PARAMS,
    )
    scheduler.start()

    for passive_newsletter_params in newsletter_config.NEWSLETTER_CONFIG:
        executor = passive_newsletter_params['executor']
        newsletter_info = passive_newsletter_params['newsletter_info']

        for param in passive_newsletter_params['params']:
            send_time = param['send_time']
            send_time_dt = datetime.datetime.strptime(send_time, "%H:%M")

            loop.create_task(passive_newsletter(
                newsletter_weekday=param['weekday'],
                newsletter_hour=send_time_dt.hour,
                newsletter_minute=send_time_dt.minute,
                newsletter_executor=executor,
                newsletter_info=newsletter_info,
                apscheduler=scheduler,
                **param['kwargs'],
            ))
    try:
        await start_bot()
    finally:
        await sessions.GigaOauthClient(config.giga_oauth_url).close()
        await sessions.GigaChatClient(config.giga_chat_url).close()
        await sessions.RagQaBankerClient(config.BASE_QA_BANKER_URL).close()
        await sessions.RagStateSupportClient(config.BASE_STATE_SUPPORT_URL).close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("bot was terminated")
