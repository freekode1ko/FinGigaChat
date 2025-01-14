"""Точка входа для запуска бота🤡"""
import asyncio
import datetime
import warnings
from contextlib import asynccontextmanager

import uvicorn
from aiogram.types import Update
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from api.router import router as api_router
from configs import config, newsletter_config
from log.bot_logger import logger
from log.sentry import init_sentry
from utils import newsletter, sessions
from utils.base import check_relevance_features

from utils.bot import bot
from utils.bot_init import dp, start_bot, passive_newsletter


async def main():
    """Точка входа для приложения"""
    init_sentry(dsn=config.SENTRY_CHAT_BOT_DSN)
    warnings.filterwarnings('ignore')

    # проверка соответствия между названиями фичей в коде и в базе данных (ролевая модель)
    await check_relevance_features()

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
    scheduler.add_job(
        newsletter.ProductDocumentSender.send_new_products_to_users,
        kwargs={'bot': bot},
        **newsletter_config.CIB_RESEARCH_NEWSLETTER_PARAMS,
    )
    scheduler.start()

    for passive_newsletter_params in newsletter_config.NEWSLETTER_CONFIG:
        executor = passive_newsletter_params['executor']
        newsletter_info = passive_newsletter_params['newsletter_info']

        for param in passive_newsletter_params['params']:
            send_time = param['send_time']
            send_time_dt = datetime.datetime.strptime(send_time, '%H:%M')

            loop.create_task(passive_newsletter(
                newsletter_weekday=param['weekday'],
                newsletter_hour=send_time_dt.hour,
                newsletter_minute=send_time_dt.minute,
                newsletter_executor=executor,
                newsletter_info=newsletter_info,
                apscheduler=scheduler,
                **param['kwargs'],
            ))
    await start_bot()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Fastapi lifespan"""
    await main()
    yield
    await sessions.GigaOauthClient().close()
    await sessions.GigaChatClient().close()
    await sessions.RagQaBankerClient().close()
    await sessions.RagStateSupportClient().close()
    await sessions.RagQaAnalyticalClient().close()
    await sessions.RagWebClient().close()

app = FastAPI(lifespan=lifespan)
app.include_router(api_router, prefix='/api')


@app.post(config.WEBHOOK_LOCAL_URL)
async def bot_webhook(request: Request):
    """Точка входа для сообщений от сервера Telegram"""
    update = Update.model_validate_json(await request.body(), context={'bot': bot})
    try:
        await dp.feed_update(bot, update)
    except Exception as e:
        logger.error(f'Ошибка при отправке ответа: {e}')
    return JSONResponse(status_code=200, content={"ok": True})

if __name__ == '__main__':
    try:
        uvicorn.run(app, host='0.0.0.0', port=config.PORT)
    except KeyboardInterrupt:
        print('bot was terminated')
