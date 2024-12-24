"""
Реализует функции рассылок

Модуль с функциями рассылки:
- новостей по подпискам на клиентов, сырье, отрасли;
- викли пульса;
- отчетов CIB research по подпискам.
- новых продуктов
"""
import asyncio
import datetime
import itertools
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import List

import pandas as pd
import sqlalchemy as sa
from aiogram import Bot, exceptions, types
from aiogram.utils.media_group import MediaGroupBuilder, MediaType

import module.data_transformer as dt
from configs import config
from constants.texts import texts_manager
from db import message, models, parser_source
from db.api.product_document import product_document_db
from db.api.research import research_db
from db.api.research_section import research_section_db
from db.api.telegram_section import telegram_section_db
from db.api.user_research_subscription import user_research_subscription_db
from db.database import async_session, engine
from db.user import get_users_subscriptions
from keyboards.analytics import constructors as anal_keyboards
from log.bot_logger import logger, user_logger
from module import formatter
from module.article_process import ArticleProcess
from utils.base import bot_send_msg
from utils.macro_view import get_macro_brief_file
from utils.telegram_news import get_tg_channel_news_msg, group_news_by_tg_channels
from utils.watermark import add_watermark_cli


async def tg_newsletter(
        bot: Bot,
        user_df: pd.DataFrame,
        **kwargs,
) -> None:
    """
    Рассылка новостей по подпискам на клиентов, сырье, отрасли

    :param bot: тг бот, который будет отправлять сообщения пользователям
    :param user_df: датафрейм с данными о пользователях, которым будет отправлена рассылка

    Kwargs:
        - newsletter_timedelta (datetime.timedelta): промежуток, за который выгружаются последние новости
        - newsletter_start_datetime (datetime.datetime): время начала рассылки
    """
    newsletter_timedelta = kwargs.get('newsletter_timedelta', datetime.timedelta(0))
    newsletter_start_datetime = kwargs.get('newsletter_start_datetime', datetime.datetime.min)

    if not newsletter_timedelta or newsletter_start_datetime == datetime.datetime.min:
        return

    # получим словарь id отрасли и ее название (в цикле, потому что справочник может пополняться)
    sections = await telegram_section_db.get_all()
    saved_messages: List[dict] = []
    newsletter_type = 'tg_subscriptions_news'

    for index, user in user_df.iterrows():
        user_id, user_name = user['user_id'], user['username']
        logger.info(
            f'Подготовка сводки новостей из telegram каналов для отправки их пользователю {user_name}*{user_id}*')

        for section in sections:
            tg_news = await telegram_section_db.get_section_tg_news(
                section.id,
                True,
                user_id,
                newsletter_timedelta,
                newsletter_start_datetime,
            )
            if tg_news.empty:
                continue

            start_msg = f'Ваша новостная подборка по подпискам на telegram каналы по разделу <b>{section.name}</b>:'
            try:
                msg_title = await bot.send_message(user_id, text=start_msg, parse_mode='HTML')
            except Exception as e:
                user_logger.error(f'ERROR *{user_id}* {user_name} - {e}')
                break
            else:
                saved_messages.append(dict(user_id=user_id, message_id=msg_title.message_id, message_type=newsletter_type))

            tg_news = group_news_by_tg_channels(tg_news)

            for tg_chan_name, articles in tg_news.items():
                msg_text = get_tg_channel_news_msg(tg_chan_name, articles)
                try:
                    messages = await bot_send_msg(bot, user_id, msg_text)
                except Exception as e:
                    user_logger.error(f'ERROR *{user_id}* {user_name} - {e}')
                    break
                else:
                    for m in messages:
                        saved_messages.append(dict(user_id=user_id, message_id=m.message_id, message_type=newsletter_type))

            user_logger.debug(
                f'*{user_id}* Пользователю {user_name} пришла рассылка сводки новостей из telegram каналов по отрасли '
                f'{section.name}. '
            )
            await asyncio.sleep(1.1)

    message.add_all(saved_messages)


async def subscriptions_newsletter(bot: Bot, user_df: pd.DataFrame | None, **kwargs) -> None:
    """
    Рассылка новостей по подпискам на клиентов, сырье, отрасли

    :param bot: тг бот, который будет отправлять сообщения пользователям
    :param user_df: датафрейм с данными о пользователях, которым будет отправлена рассылка

    Kwargs:
        - newsletter_timedelta (datetime.timedelta): промежуток, за который выгружаются последние новости
        - newsletter_start_datetime (datetime.datetime): время начала рассылки
    """
    newsletter_timedelta = kwargs.get('newsletter_timedelta', datetime.timedelta(hours=0))
    newsletter_start_datetime = kwargs.get('newsletter_start_datetime', datetime.datetime.min)

    if not newsletter_timedelta or newsletter_start_datetime == datetime.datetime.min:
        return

    ap_obj = ArticleProcess(logger)

    # получим свежие новости за определенный промежуток времени
    clients_news = ap_obj.get_news_by_time(
        newsletter_timedelta, 'client', newsletter_start_datetime
    ).sort_values(by=['name', 'date'], ascending=[True, False])
    commodity_news = ap_obj.get_news_by_time(
        newsletter_timedelta, 'commodity', newsletter_start_datetime
    ).sort_values(by=['name', 'date'], ascending=[True, False])

    # получим словарь id отрасли и ее название
    industry_name = pd.read_sql_table('industry', con=engine, index_col='id')['name'].to_dict()
    # получим словари новостных объектов {id: [альтернативные названия], ...}
    saved_messages: list[dict] = []
    newsletter_type = 'subscriptions_news'

    user_df = await get_users_subscriptions()

    row_number = 0
    for _, user in user_df.iterrows():
        user_id = user['user_id']
        user_name = user['username']
        industry_ids = user['industry_ids']
        client_ids = user['client_ids']
        commodity_ids = user['commodity_ids']

        if not industry_ids and not client_ids and not commodity_ids:
            continue

        logger.info(f'Подготовка новостей для отправки их пользователю {user_name}*{user_id}*')
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
                msg_title = await bot.send_message(user_id, text='Ваша новостная подборка по подпискам:')
                saved_messages.append(dict(user_id=user_id, message_id=msg_title.message_id, message_type=newsletter_type))

                for industry in industry_name_list:
                    articles = user_industry_df.loc[user_industry_df['industry'] == industry]
                    msg = ArticleProcess.make_format_industry_msg(articles.values.tolist())
                    messages = await bot_send_msg(bot, user_id, msg)
                    for m in messages:
                        saved_messages.append(dict(user_id=user_id, message_id=m.message_id, message_type=newsletter_type))

                for subject in client_commodity_name_list:
                    articles = user_client_comm_df.loc[user_client_comm_df['name'] == subject]
                    _, msg = ArticleProcess.make_format_msg(subject, articles.values.tolist(), None)
                    msg = await bot.send_message(user_id, text=msg, parse_mode='HTML', disable_web_page_preview=True)
                    saved_messages.append(dict(user_id=user_id, message_id=msg.message_id, message_type=newsletter_type))

                user_logger.debug(
                    f'*{user_id}* Пользователю {user_name} пришла ежедневная рассылка. '
                    f'Активные подписки на момент рассылки: {industry_ids=:}, {client_ids=:}, {commodity_ids=:}'
                )
            # except ChatNotFound:  # FIXME 3.3.0
            #     user_logger.error(f'Чата с пользователем *{user_id}* {user_name} не существует')
            # except BotBlocked:
            #     user_logger.warning(f'*{user_id}* Пользователь поместил бота в блок, он не получил сообщения')
            except Exception as e:
                user_logger.error(f'ERROR *{user_id}* {user_name} - {e}')
        else:
            user_logger.info(f'Нет новых новостей по подпискам для: {user_name}*{user_id}*')

    message.add_all(saved_messages)


async def weekly_pulse_newsletter(
        bot: Bot,
        user_df: pd.DataFrame,
        **kwargs,
) -> None:
    """
    Рассылка новостей по подпискам на клиентов, сырье, отрасли

    :param bot: тг бот, который будет отправлять сообщения пользователям
    :param user_df: датафрейм с данными о пользователях, которым будет отправлена рассылка

    Kwargs:
        - newsletter_type (str): тип, указывающий, что идет рассылка итогов недели или "что нас ждет на следующей неделе"
    """
    newsletter_type = kwargs.get('newsletter_type', '')
    source_name = 'Weekly Pulse'
    # проверяем, что данные обновились с последней рассылки
    last_update_time = parser_source.get_source_last_update_datetime(source_name=source_name)
    now = datetime.datetime.now()

    # получаем текст рассылки
    if newsletter_type == 'weekly_result':
        # рассылается в пятницу
        check_days = 2
        title, newsletter, img_path_list = dt.Newsletter.make_weekly_result()
    elif newsletter_type == 'weekly_event':
        # рассылается в пн
        check_days = 4
        title, newsletter, img_path_list = dt.Newsletter.make_weekly_event()
    else:
        return

    while not last_update_time >= (now - datetime.timedelta(days=check_days)):
        # check if weekly pulse was updated
        warn_msg = 'Данные по Weekly Pulse не были обновлены, рассылка приостановлена'
        logger.warning(warn_msg)
        last_update_time = parser_source.get_source_last_update_datetime(source_name=source_name)
        now = datetime.datetime.now()
        await asyncio.sleep(config.CHECK_WEEKLY_PULSE_UPDATE_SLEEP_TIME)

    weekly_pulse_date_str = last_update_time.strftime(config.BASE_DATE_FORMAT)
    weekly_pulse_date_str = f'Данные на {weekly_pulse_date_str}'
    saved_messages: List[dict] = []

    for _, user_data in user_df.iterrows():
        user_id, user_name = user_data['user_id'], user_data['username']
        media = MediaGroupBuilder(caption=weekly_pulse_date_str)
        for path in img_path_list:
            media.add_photo(types.FSInputFile(path))
        try:
            msg_title: types.Message = await bot.send_message(
                user_id,
                text=newsletter,
                parse_mode='HTML',
                protect_content=texts_manager.PROTECT_CONTENT,
            )
            msg_photos: List[types.Message] = await bot.send_media_group(
                user_id,
                media=media.build(),
                protect_content=texts_manager.PROTECT_CONTENT,
            )

            saved_messages.append(dict(user_id=user_id, message_id=msg_title.message_id, message_type=newsletter_type))
            for msg in msg_photos:
                saved_messages.append(dict(user_id=user_id, message_id=msg.message_id, message_type=newsletter_type))

            user_logger.debug(f'*{user_id}* Пользователю {user_name} пришла рассылка "{title}"')
        # except BotBlocked:
        #     user_logger.warning(f'*{user_id}* Пользователь не получил рассылку "{title}" : бот в блоке')
        except Exception as e:
            logger.error(f'ERROR *{user_id}* Пользователь не получил рассылку "{title}" : {e}')

    message.add_all(saved_messages)


async def send_researches_to_user(bot: Bot, user: models.RegisteredUser, research_df: pd.DataFrame) -> list[types.Message]:
    """
    Отправка отчетов пользователю с форматированием

    :param bot: объект тг бота
    :param user: телеграм пользователь, которому отправляются отчеты
    :param research_df: DataFrame[id, research_type_id, filepath, header, text, parse_datetime, publication_date, report_id]
    :returns: Список объектов отправленных сообщений
    """
    sent_msg_list = []

    for _, research in research_df.iterrows():
        user_logger.debug(f'*{user.user_id}* Пользователю {user.username} отправляется рассылка отчета {research["id"]}.')

        # Если есть текст, то чисто тайтл и кнопку.
        # Если есть текст и файл, то тайтл и кнопку.
        if research['text']:
            formatted_msg_txt = formatter.ResearchFormatter.format_min(research)
            keyboard = anal_keyboards.get_full_research_kb(research['id'])
            msg = await bot.send_message(
                user.user_id,
                formatted_msg_txt,
                reply_markup=keyboard,
                protect_content=texts_manager.PROTECT_CONTENT,
                parse_mode='HTML',
            )
        # Если есть файл, но нет текста - тайтл с файлом
        elif research['filepath'] and os.path.exists(research['filepath']):
            tmp_file_name = f'{os.path.basename(research["filepath"])}_{user.user_id}_watermarked.pdf'
            user_anal_filepath = Path(tempfile.gettempdir()) / tmp_file_name

            try:
                add_watermark_cli(
                    research['filepath'],
                    user_anal_filepath,
                    user.user_email,
                )
            except subprocess.SubprocessError as e:
                logger.error(f'*{user.user_id}* При рассылке отчета {research["id"]} произошла ошибка: {e}.')
                continue
            else:
                file = types.FSInputFile(user_anal_filepath)
                msg_txt = f'<b>{research["header"]}</b>'
                msg = await bot.send_document(
                    document=file,
                    chat_id=user.user_id,
                    caption=msg_txt,
                    parse_mode='HTML',
                    protect_content=texts_manager.PROTECT_CONTENT,
                )
        else:
            continue

        sent_msg_list.append(msg)
        user_logger.debug(f'*{user.user_id}* Пользователю {user.username} пришла рассылка отчета {research["id"]}.')
        await asyncio.sleep(1.1)

    return sent_msg_list


async def send_new_researches_to_users(bot: Bot) -> None:
    """
    Функция рассылки новых отчетов CIB Research по подпискам

    :param bot: телеграм бот, который отправляет сообщения пользователям
    """
    now = datetime.datetime.now()
    newsletter_dt_str = now.strftime(config.INVERT_DATETIME_FORMAT)
    logger.info(f'Начинается рассылка новостей в {newsletter_dt_str} по CIB Research')
    start_tm = time.time()

    # получаем список отчетов, которые надо разослать
    research_df = await research_db.get_new_researches()
    research_type_ids = research_df['research_type_id'].drop_duplicates().values.tolist()

    # Получаем список пользователей, которым требуется разослать отчеты
    user_df = await user_research_subscription_db.get_users_by_research_types_df(research_type_ids)
    # Словарь key=research_type.id, value=research_section
    research_section_dict = await research_section_db.get_research_sections_by_research_types_df(research_type_ids)

    # Сохранение отправленных сообщений
    saved_messages = []
    newsletter_type = 'cib_research_newsletter'

    research_df['research_section_name'] = research_df['research_type_id'].apply(lambda x: research_section_dict[x]['name'])

    for _, user_row in user_df.iterrows():
        user_id = user_row['user_id']
        user = models.RegisteredUser(user_id=user_id, username=user_row['username'], user_email=user_row['user_email'])
        logger.info(f'Рассылка отчетов пользователю {user_id}')

        # filter by user`s subs and group research_df by research_section_name
        research_df_group_by_section = (
            research_df[
                research_df['research_type_id'].isin(user_row['research_types'])
            ]
            .groupby('research_section_name')
        )
        for research_section_name, section_researches_df in research_df_group_by_section:
            # отправка отчета пользователю
            start_msg = f'Ваша новостная рассылка по подпискам на отчеты по разделу <b>{research_section_name}</b>:'
            try:
                msg = await bot.send_message(user_id, start_msg, protect_content=texts_manager.PROTECT_CONTENT, parse_mode='HTML')
                sent_msg_list = await send_researches_to_user(bot, user, section_researches_df)
            except exceptions.TelegramForbiddenError as e:
                logger.error(f'При рассылке по подпискам на отчеты пользователю {user_id} произошла ошибка: %s', e)
                break
            except exceptions.TelegramAPIError as e:
                logger.error(f'При рассылке по подпискам на отчеты пользователю {user_id} произошла ошибка: %s', e)
                continue
            else:
                saved_messages.append(dict(user_id=user_id, message_id=msg.message_id, message_type=newsletter_type))
                saved_messages.extend(
                    dict(user_id=user_id, message_id=m.message_id, message_type=newsletter_type)
                    for m in sent_msg_list
                )

    message.add_all(saved_messages)

    work_time = time.time() - start_tm
    users_cnt = len(user_df)
    logger.info(
        f'Рассылка в {newsletter_dt_str} для {users_cnt} пользователей успешно завершена за {work_time:.3f} секунд. '
        f'Переходим в ожидание следующей рассылки.'
    )


async def send_weekly_check_up(bot: Bot, user_df: pd.DataFrame, **kwargs) -> None:
    """
    Функция рассылки weekly check up

    :param bot: телеграм бот, который отправляет сообщения пользователям
    :param user_df: Датафрейм с пользователями, которым рассылается weekly check up
    """
    now = datetime.datetime.now()
    newsletter_dt_str = now.strftime(config.INVERT_DATETIME_FORMAT)
    logger.info(f'Начинается рассылка Weekly Check up в {newsletter_dt_str}')
    start_tm = time.time()

    # получаем отчет, который надо разослать
    if document_path := get_macro_brief_file():
        weekly_check_up_document = types.FSInputFile(document_path)
    else:
        logger.error('Не удалось найти документ Weekly Check up')
        return

    # Сохранение отправленных сообщений
    saved_messages = []
    newsletter_type = 'weekly_check_up_newsletter'
    msg_text = "Weekly 'Check up'"

    for _, user_row in user_df.iterrows():
        user_id = user_row['user_id']
        logger.info(f'Рассылка Weekly Check up пользователю {user_id}')
        # отправка отчета пользователю
        try:
            msg = await bot.send_document(user_id, document=weekly_check_up_document, caption=msg_text,
                                          protect_content=texts_manager.PROTECT_CONTENT, parse_mode='HTML')
        except exceptions.TelegramAPIError as e:
            logger.error(f'При рассылке weekly check up пользователю {user_id} произошла ошибка: %s', e)
        else:
            saved_messages.append(dict(user_id=user_id, message_id=msg.message_id, message_type=newsletter_type))

    message.add_all(saved_messages)

    work_time = time.time() - start_tm
    users_cnt = len(user_df)
    logger.info(
        f'Рассылка Weekly Check up в {newsletter_dt_str} для {users_cnt} пользователей успешно завершена за {work_time:.3f} секунд. '
        f'Переходим в ожидание следующей рассылки.'
    )


class ProductDocumentSender:
    """Функции для отправки новых продуктов пользователям"""

    @staticmethod
    async def get_new_products() -> list[models.Product]:
        """
        Получить новые продукты

        :return: Продукты с is_new == True
        """
        async with async_session() as session:
            products = await session.execute(
                sa.select(models.Product)
                .join(models.ProductDocument, models.Product.documents)
                .filter(models.Product.is_new == True).distinct()  # noqa:E712
            )
            return products.scalars().all()

    @staticmethod
    async def get_users_for_product(product_id: int) -> list[int]:
        """
        Получение id пользователей которым нужно отправить продукт

        :param product_id: ID продукта
        :return: Айди пользователей
        """
        async with async_session() as session:
            users_ids = await session.execute(
                sa.select(models.RegisteredUser.user_id)
                .join(models.RelationUsersProducts, models.RegisteredUser.user_id == models.RelationUsersProducts.user_id)
                .filter(models.RelationUsersProducts.product_id == product_id)
            )
            return users_ids.scalars().all()

    @staticmethod
    async def get_product_documents(product_id: int) -> list[models.ProductDocument]:
        """
        Получение документов привязанных к продукту

        :param product_id: ID продукта
        :return: Список документов
        """
        try:
            documents = await product_document_db.get_all_by_product_id(product_id)
        except Exception as e:
            logger.error(f'Документы по Продукту id={product_id} не получены из-за ошибки {str(e)}')
            raise
        else:
            logger.info(f'Документы по Продукту id={product_id} получены')
            return documents

    @staticmethod
    async def create_documents_media_group(
            product_id: int,
            documents: list[models.ProductDocument],
            broadcast_message: str,
    ) -> list[MediaType]:
        """
        Создание MediaGroup для группы документов

        :param product_id: ID продукта
        :param documents: Список документов
        :param broadcast_message: Сообщение к файлам
        :return: Медиа группа
        """
        try:
            logger.info(f'Старт формирования telegram медиа группы по Продукту id={product_id}')
            media = MediaGroupBuilder(
                caption=(
                    broadcast_message
                    if broadcast_message else
                    texts_manager.BROADCAST_PRODUCT_DEFAULT_ANSWER
                )
            )

            for document in documents:
                path = Path(document.file_path)
                if not path.exists():
                    logger.error(f'В рассылку по Продукту id={product_id} НЕ добавлен файл {str(document.name)} '
                                 f'по пути {str(document.file_path)}')
                    continue
                media.add_document(media=types.FSInputFile(path))
                logger.info(
                    f'В рассылку по Продукту id={product_id} добавлен файл {document.name} по пути {document.file_path}')
            media = media.build()
        except Exception as e:
            logger.error(f'Формирования telegram медиа группы по Продукту id={product_id} завершилось с ошибкой {str(e)}')
            raise
        else:
            logger.info(f'Формирования telegram медиа группы по Продукту id={product_id} завершилось успешно')
            return media

    @staticmethod
    async def send_media_to_users(users_ids: list[int], media: list[MediaType], bot: Bot, product_id: int) -> None:
        """
        Отправка медиа группы пользователям

        :param users_ids: Список ID пользователей для отправки сообщения
        :param media: Медиа группа для отправки
        :param bot: Бот
        :param product_id: ID продукта
        """
        logger.info(f'Начало отправки пользователям по Продукту id={product_id}')
        for user_ids_batch in itertools.batched(users_ids, config.MAX_MESSAGES_PER_SECOND):
            for user_id in user_ids_batch:
                try:
                    await bot.send_media_group(chat_id=user_id, media=media)
                except Exception as e:
                    logger.error(f'Во время отправки сообщения пользователю {user_id} Продукта с id={product_id} '
                                 f'произошла ошибка {str(e)}')
                else:
                    logger.info(f'Сообщение пользователю {user_id} по Продукту с id={product_id} отправлено')
            await asyncio.sleep(1)

    @staticmethod
    async def update_product_in_new_field(product_id: int) -> None:
        """
        Обновление is_new у продукта на False

        :param product_id: ID продукта
        """
        async with async_session() as session:
            try:
                await session.execute(
                    sa.update(models.Product).values(is_new=False).where(models.Product.id == product_id)
                )
                await session.commit()
            except Exception as e:
                logger.error(f'Не получилось проставить is_new=False Продукта с id={product_id} произошла ошибка {str(e)}')
            else:
                logger.info(f'Продукта с id={product_id} обновлен is_new=False')

    @classmethod
    async def send_new_products_to_users(cls, bot: Bot) -> None:
        """
        Рассылка документов по продуктам пользователям

        :param bot: Бот
        """
        now = datetime.datetime.now()
        newsletter_dt_str = now.strftime(config.INVERT_DATETIME_FORMAT)

        logger.info(f'Начинается рассылка Продуктов пользователям в {newsletter_dt_str}')

        # Получение продуктов
        products = await cls.get_new_products()
        if not products:
            logger.info('Не найдено новых продуктов, рассылка завершена (P.s. или у продуктов нет документов)')
            return
        logger.info(f'Найдено {len(products)} новых продуктов')

        for product in products:
            try:
                logger.info(f'Начинается рассылка Продукта id={product.id}')
                # Получение пользователей для рассылки
                users_ids = await cls.get_users_for_product(product.id)
                if not users_ids:
                    logger.error(f'Не найдено пользователей для рассылки по Продукту id={product.id}')
                    continue
                logger.info(f'Рассылки по Продукту id={product.id} будет осуществлена на {len(users_ids)} пользователей ')

                # Получение документов по продукту для рассылки
                documents = await cls.get_product_documents(product.id)

                # Создание медиа группы для ускорения отправки сообщений
                media = await cls.create_documents_media_group(product.id, documents, product.broadcast_message)
                # Отправка сообщения пользователям
                await cls.send_media_to_users(users_ids, media, bot, product.id)
                # Обновления статуса по продукту
                await cls.update_product_in_new_field(product.id)

            except Exception as e:
                logger.error(f'Рассылка по Продукту с id={product.id} завершилась с ошибкой {str(e)}')
            else:
                logger.info(f'Отправка сообщений по Продукту с id={product.id} завершена')
    logger.info('Рассылка Продуктов пользователям завершена')
