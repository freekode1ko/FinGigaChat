import asyncio
import datetime

import pandas as pd
from aiogram import Bot, types
from aiogram.utils.media_group import MediaGroupBuilder

from configs import config
import module.data_transformer as dt
from log.bot_logger import logger, user_logger
from db.database import engine
from module.article_process import ArticleProcess
from utils.base import bot_send_msg, translate_subscriptions_to_object_id
from utils.industry import get_tg_channel_news_msg, group_news_by_tg_channels
from db import research_source
from db.industry import get_industry_tg_news


async def tg_newsletter(
        bot: Bot,
        user_df: pd.DataFrame,
        *args,
        **kwargs,
) -> None:
    newsletter_timedelta = kwargs.get('newsletter_timedelta', datetime.timedelta(0))
    next_newsletter_datetime = kwargs.get('next_newsletter_datetime', datetime.datetime.min)

    if not newsletter_timedelta or next_newsletter_datetime == datetime.datetime.min:
        return

    # получим словарь id отрасли и ее название (в цикле, потому что справочник может пополняться)
    industry_dict = pd.read_sql_table('industry', con=engine, index_col='id')['name'].to_dict()

    for index, user in user_df.iterrows():
        user_id, user_name = user['user_id'], user['username']
        logger.debug(
            f'Подготовка сводки новостей из telegram каналов для отправки их пользователю {user_name}*{user_id}*')

        for industry_id, industry_name in industry_dict.items():
            tg_news = get_industry_tg_news(industry_id, True, user_id, newsletter_timedelta, next_newsletter_datetime)
            if tg_news.empty:
                continue

            start_msg = f'Ваша новостная подборка по подпискам на telegram каналы по отрасли <b>{industry_name.capitalize()}</b>:'
            await bot.send_message(user_id, text=start_msg, parse_mode='HTML')

            tg_news = group_news_by_tg_channels(tg_news)

            for tg_chan_name, articles in tg_news.items():
                msg_text = get_tg_channel_news_msg(tg_chan_name, articles)
                await bot_send_msg(bot, user_id, msg_text)

            user_logger.debug(
                f'*{user_id}* Пользователю {user_name} пришла рассылка сводки новостей из telegram каналов по отрасли '
                f'{industry_name}. '
            )
            await asyncio.sleep(1.1)


async def subscriptions_newsletter(
        bot: Bot,
        user_df: pd.DataFrame,
        *args,
        **kwargs,
) -> None:
    client_hours = kwargs.get('client_hours', 0)
    commodity_hours = kwargs.get('commodity_hours', 0)

    ap_obj = ArticleProcess(logger)

    # получим свежие новости за определенный промежуток времени
    clients_news = ap_obj.get_news_by_time(client_hours, 'client').sort_values(by=['name', 'date'],
                                                                               ascending=[True, False])
    commodity_news = ap_obj.get_news_by_time(commodity_hours, 'commodity').sort_values(by=['name', 'date'],
                                                                                       ascending=[True, False])

    # получим словарь id отрасли и ее название
    industry_name = pd.read_sql_table('industry', con=engine, index_col='id')['name'].to_dict()
    # получим словари новостных объектов {id: [альтернативные названия], ...}
    industry_id_name_dict, client_id_name_dict, commodity_id_name_dict = iter(ap_obj.get_industry_client_com_dict())

    row_number = 0
    for index, user in user_df.iterrows():
        user_id, user_name, subscriptions = user['user_id'], user['username'], user['subscriptions']
        if not subscriptions:
            continue
        subscriptions = subscriptions.split(', ')
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
            logger.debug(f'Отправка подписок для: {user_name}*{user_id}*. {row_number}/{user_df.shape[0]}')
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


async def weekly_pulse_newsletter(
        bot: Bot,
        user_df: pd.DataFrame,
        *args,
        **kwargs,
) -> None:
    newsletter_type = kwargs.get('newsletter_type', '')
    base_url = f'{config.research_base_url}group/guest/money'
    source_name = 'Weekly Pulse'
    # проверяем, что данные обновились с последней рассылки
    last_update_time = research_source.get_source_last_update_datetime(source_name=source_name, source_link=base_url)
    now = datetime.datetime.now()

    # получаем текст рассылки
    if newsletter_type == 'weekly_result':
        # рассылается в пятницу
        check_days = 1
        title, newsletter, img_path_list = dt.Newsletter.make_weekly_result()
    elif newsletter_type == 'weekly_event':
        # рассылается в пн
        check_days = 3
        title, newsletter, img_path_list = dt.Newsletter.make_weekly_event()
    else:
        return

    while not last_update_time >= (now - datetime.timedelta(days=check_days)):
        # check if weekly pulse was updated
        warn_msg = 'Данные по Weekly Pulse не были обновлены, рассылка приостановлена'
        logger.warning(warn_msg)
        last_update_time = research_source.get_source_last_update_datetime(source_name=source_name, source_link=base_url)
        now = datetime.datetime.now()
        await asyncio.sleep(config.CHECK_WEEKLY_PULSE_UPDATE_SLEEP_TIME)

    weekly_pulse_date_str = last_update_time.strftime(config.BASE_DATE_FORMAT)
    weekly_pulse_date_str = f'Данные на {weekly_pulse_date_str}'

    for _, user_data in user_df.iterrows():
        user_id, user_name = user_data['id'], user_data['username']
        media = MediaGroupBuilder(caption=weekly_pulse_date_str)
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
