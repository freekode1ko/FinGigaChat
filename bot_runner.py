import asyncio
import warnings
from typing import Dict

import pandas as pd
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.utils.media_group import MediaGroupBuilder
from sqlalchemy import text

import config
import module.data_transformer as dt
from bot_logger import logger, user_logger
from constants.bot.commands import PUBLIC_COMMANDS
from database import engine
from handlers import admin, common, gigachat, news, quotes, referencebook, subscriptions
from module.article_process import ArticleProcess
from utils.bot_utils import (
    bot_send_msg,
    get_waiting_time,
    wait_until_next_newsletter,
    translate_subscriptions_to_object_id,
)
from utils.sentry import init_sentry

storage = MemoryStorage()
bot = Bot(token=config.api_token)
dp = Dispatcher(storage=storage)


async def send_newsletter(newsletter_data: Dict) -> None:
    """
    Отправляет рассылку

    :param newsletter_data: хранит newsletter_type, sending_weekday, sending_hour, sending_minute
    """

    newsletter_type, sending_weekday, sending_hour, sending_minute = tuple(newsletter_data.values())

    # ждем наступления нужной даты
    time_to_wait = await get_waiting_time(sending_weekday, sending_hour, sending_minute)
    await asyncio.sleep(time_to_wait.total_seconds())

    # получаем текст рассылки
    if newsletter_type == 'weekly_result':
        title, newsletter, img_path_list = dt.Newsletter.make_weekly_result()
    elif newsletter_type == 'weekly_event':
        title, newsletter, img_path_list = dt.Newsletter.make_weekly_event()
    else:
        return

    # отправляем пользователям
    with engine.connect() as conn:
        users_data = conn.execute(text('SELECT user_id, username FROM whitelist')).fetchall()

    users_got_news_cnt = len(users_data)

    for user_data in users_data:
        user_id, user_name = user_data[0], user_data[1]
        media = MediaGroupBuilder()
        for path in img_path_list:
            media.add_photo(types.FSInputFile(path))
        try:
            await bot.send_message(user_id, text=newsletter, parse_mode='HTML', protect_content=True)
            await bot.send_media_group(user_id, media=media.build(), protect_content=True)
            user_logger.debug(f'*{user_id}* Пользователю {user_name} пришла рассылка "{title}"')
        # except BotBlocked:
        #     user_logger.warning(f'*{user_id}* Пользователь не получил рассылку "{title}" : бот в блоке')
        except Exception as e:
            logger.error(f'ERROR *{user_id}* Пользователь не получил рассылку "{title}" : {e}')
            users_got_news_cnt -= 1

    logger.info(f'{users_got_news_cnt} пользователям из {len(users_data)} пришла рассылка "{title}"')

    await asyncio.sleep(100)
    return await send_newsletter(newsletter_data)


# TODO: Добавить синхронизацию времени с методом на ожидание (newsletter_scheduler)
async def send_daily_news(client_hours: int = 7, commodity_hours: int = 7, schedule: int = 0):
    """
    Рассылка новостей по часам и выбранным темам (объектам новостей: клиенты/комоды/отрасли)

    :param client_hours: За какой период нужны новости по клиентам
    :param commodity_hours: За какой период нужны новости по комодам
    :param schedule: Запуск без ожидания
    return None
    """
    await wait_until_next_newsletter(schedule, logger=logger)  # ожидание рассылки
    logger.info('Начинается ежедневная рассылка новостей по подпискам...')
    ap_obj = ArticleProcess(logger)

    # получим свежие новости за определенный промежуток времени
    clients_news = ap_obj.get_news_by_time(client_hours, 'client').sort_values(by=['name', 'date'], ascending=[True, False])
    commodity_news = ap_obj.get_news_by_time(commodity_hours, 'commodity').sort_values(by=['name', 'date'], ascending=[True, False])

    # получим словарь id отрасли и ее название
    industry_name = pd.read_sql_table('industry', con=engine, index_col='id')['name'].to_dict()
    # получим словари новостных объектов {id: [альтернативные названия], ...}
    industry_id_name_dict, client_id_name_dict, commodity_id_name_dict = iter(ap_obj.get_industry_client_com_dict())

    row_number = 0
    users = pd.read_sql_query('SELECT user_id, username, subscriptions FROM whitelist ' 'WHERE subscriptions IS NOT NULL', con=engine)
    for index, user in users.iterrows():
        user_id, user_name, subscriptions = user['user_id'], user['username'], user['subscriptions'].split(', ')
        logger.debug(f'Подготовка новостей для отправки их пользователю {user_name}*{user_id}*')

        # получим списки id объектов, на которые подписан пользователь
        industry_ids = translate_subscriptions_to_object_id(industry_id_name_dict, subscriptions)
        client_ids = translate_subscriptions_to_object_id(client_id_name_dict, subscriptions)
        commodity_ids = translate_subscriptions_to_object_id(commodity_id_name_dict, subscriptions)

        # получим новости по подпискам пользователя
        user_industry_df, user_client_comm_df = ArticleProcess.get_user_article(
            clients_news, commodity_news, industry_ids, client_ids, commodity_ids, industry_name
        )

        if not user_industry_df.empty or not user_client_comm_df.empty:
            row_number += 1
            logger.debug(f'Отправка подписок для: {user_name}*{user_id}*. {row_number}/{users.shape[0]}')
            try:
                industry_name_list = user_industry_df['industry'].drop_duplicates().values.tolist()
                client_commodity_name_list = user_client_comm_df['name'].drop_duplicates().values.tolist()
                await bot.send_message(user_id, text='Ваша новостная подборка по подпискам:')

                for industry in industry_name_list:
                    articles = user_industry_df.loc[user_industry_df['industry'] == industry]
                    msg = ArticleProcess.make_format_industry_msg(articles.values.tolist())
                    await bot_send_msg(bot, user_id, msg)

                for subject in client_commodity_name_list:
                    articles = user_client_comm_df.loc[user_client_comm_df['name'] == subject]
                    _, msg, _ = ArticleProcess.make_format_msg(subject, articles.values.tolist(), None)
                    await bot.send_message(user_id, text=msg, parse_mode='HTML', disable_web_page_preview=True)

                user_logger.debug(
                    f'*{user_id}* Пользователю {user_name} пришла ежедневная рассылка. '
                    f"Активные подписки на момент рассылки: {user['subscriptions']}"
                )
            # except ChatNotFound:  # FIXME 3.3.0
            #     user_logger.error(f'Чата с пользователем *{user_id}* {user_name} не существует')
            # except BotBlocked:
            #     user_logger.warning(f'*{user_id}* Пользователь поместил бота в блок, он не получил сообщения')
            except Exception as e:
                user_logger.error(f'ERROR *{user_id}* {user_name} - {e}')
        else:
            user_logger.info(f'Нет новых новостей по подпискам для: {user_name}*{user_id}*')
    logger.info('Рассылка успешно завершена. Переходим в ожидание следующей рассылки.')

    await asyncio.sleep(100)
    client_hours = 18 if client_hours == 7 else 7
    commodity_hours = 18 if commodity_hours == 7 else 7

    return await send_daily_news(client_hours, commodity_hours)


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
        gigachat.router,
        referencebook.router,
        news.router,
    )
    # Отключаем обработку сообщений, которые прислали в период, когда бот был выключен
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def main():
    init_sentry(dsn=config.SENTRY_CHAT_BOT_DSN)
    warnings.filterwarnings('ignore')

    # запускам рассылки
    print('Инициализация бота')
    loop = asyncio.get_event_loop()
    loop.create_task(send_newsletter(dict(name='weekly_result', weekday=5, hour=18, minute=0)))
    loop.create_task(send_newsletter(dict(name='weekly_event', weekday=1, hour=11, minute=0)))
    loop.create_task(send_daily_news())
    await start_bot()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("bot was terminated")
