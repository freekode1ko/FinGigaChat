"""Файл с дополнительными функциями"""
import ast
import asyncio
import logging
import os
import re
from datetime import date, datetime, timedelta
from math import ceil
from pathlib import Path
from typing import Any, Callable, Optional

import pandas as pd
from aiogram import Bot, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.media_group import MediaGroupBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import module.data_transformer as dt
from configs.config import PAGE_ELEMENTS_COUNT
from constants import constants, enums
from constants.constants import research_footer
from constants.texts import texts_manager
from db import models
from db.database import async_session, engine
from db.user import get_user, get_user_role
from log.bot_logger import user_logger
from log.logger_base import Logger


async def bot_send_msg(bot: Bot,
                       user_id: int | str,
                       msg: str,
                       delimiter: str = '\n\n',
                       prefix: str = '',
                       protect_content: bool = texts_manager.PROTECT_CONTENT) -> list[types.Message]:
    """
    Делит сообщение на батчи, если длина больше допустимой

    :param bot: tg bot instance
    :param user_id: ID пользователя для которого будет произведена отправка
    :param msg: Текст для отправки или подпись к файлу
    :param delimiter: Разделитель текста
    :param prefix: Начало каждого нового сообщения
    :param protect_content: Защищать ли сообщения от скринов и перессылки
    return: list[aiogram.types.Message] Список объетов отправленных сообщений
    """
    batches = []
    current_batch = prefix
    max_batch_length = constants.TELEGRAM_MESSAGE_MAX_LEN
    messages: list[types.Message] = []

    for paragraph in msg.split(delimiter):
        if len(current_batch) + len(paragraph) + len(delimiter) < max_batch_length:
            current_batch += paragraph + delimiter
        else:
            batches.append(current_batch.strip())
            current_batch = prefix + paragraph + delimiter

    if current_batch:
        batches.append(current_batch.strip())

    for batch in batches:
        msg = await bot.send_message(
            user_id,
            text=batch,
            parse_mode='HTML',
            disable_web_page_preview=True,
            protect_content=protect_content,
        )
        messages.append(msg)
    return messages


async def send_msg_to(bot: Bot, user_id, message_text, file_name, file_type) -> types.Message:
    """
    Рассылка текста и/или файлов(документы и фотокарточки) на выбранного пользователя

    :param bot: tg bot instance
    :param user_id: ID пользователя для которого будет произведена отправка
    :param message_text: Текст для отправки или подпись к файлу
    :param file_name: Текст содержащий в себе название сохраненного файла
    :param file_type: Тип файла для отправки. Может быть None, str("Document") и str("Picture")
    return: aiogram.types.Message отправленное сообщение
    """
    if file_name:
        if file_type == 'photo':
            file = types.FSInputFile('sources/{}.jpg'.format(file_name))
            msg = await bot.send_photo(
                photo=file,
                chat_id=user_id,
                caption=message_text,
                parse_mode='HTML',
                protect_content=texts_manager.PROTECT_CONTENT,
            )
        else:
            file = types.FSInputFile('sources/{}'.format(file_name))
            msg = await bot.send_document(
                document=file,
                chat_id=user_id,
                caption=message_text,
                parse_mode='HTML',
                protect_content=texts_manager.PROTECT_CONTENT,
            )
    else:
        msg = await bot.send_message(user_id, message_text, parse_mode='HTML', protect_content=texts_manager.PROTECT_CONTENT)

    return msg


def read_curdatetime() -> datetime:
    """
    Чтение даты последней сборки из базы данных

    return Дата последней сборки
    """
    curdatetime = pd.read_sql_query('SELECT * FROM "date_of_last_build"', con=engine)
    return curdatetime['date_time'][0]


def file_cleaner(filename) -> None:
    """
    Удаление файла по относительному или абсолютному пути

    :param filename: Путь от исполняемого файла (если он не рядом) и имя файла для удаления
    """
    try:
        os.remove(filename)
    except OSError:
        pass


async def __text_splitter(message: types.Message, text: str, name: str, date: str, batch_size: int = 2048) -> None:
    """
    Разбиение сообщения на части по количеству символов

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param text: Содержание отчета
    :param name: Заголовок отчета
    :param date: Дата сборки отчета
    :param batch_size: Размер сообщения в символах. По стандарту это значение равно 2048 символов на сообщение
    return None
    """
    text_group = []
    # import dateutil.parser as dparser
    # date = dparser.parse(date, fuzzy=True)

    # uncommet me if need summory #TODO: исправить порядок параметров и промпт
    # ****************************
    # giga_ans = await giga_ask(message, prompt='{}\n {}'.format(summ_prompt, text), return_ans=True)
    # ****************************
    # giga_ans = text.replace('\n', '\n\n')
    # giga_ans = text.replace('>', '\n\n')

    giga_ans = text
    if len(giga_ans) > batch_size:
        for batch in range(0, len(giga_ans), batch_size):
            text_group.append(text[batch: batch + batch_size])
        for summ_part in text_group:
            await message.answer(
                '<b>{}</b>\n\n{}\n\n<i>{}</i>'.format(name, summ_part, research_footer),
                parse_mode='HTML',
                protect_content=texts_manager.PROTECT_CONTENT,
            )
    else:
        await message.answer(
            '<b>{}</b>\n\n{}\n\n{}\n\n<i>{}</i>'.format(name, giga_ans, research_footer, date),
            parse_mode='HTML',
            protect_content=texts_manager.PROTECT_CONTENT,
        )


async def __sent_photo_and_msg(
    message: types.Message,
    photo: types.InputFile | str | None = None,
    day: list[list] = None,
    month: list[list] = None,
    title: str | None = '',
    source: str = '',
    protect_content: bool = texts_manager.PROTECT_CONTENT,
) -> None:
    """
    Отправка в чат пользователю сообщение с текстом и/или изображения

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param photo: Фотокарточка для отправки
    :param day: Дневной отчет в формате текста
    :param month: Месячный отчет в формате текста
    :param title: Подпись к фотокарточке
    :param source: Не используется на данный момент
    :param protect_content: Булевое значение отвечающее за защиту от копирования сообщения и его текста/фотокарточки
    return None
    """
    batch_size = 3500
    if month:  # 'Публикация месяца
        for month_rev in month[::-1]:
            month_rev_text = month_rev[1].replace('Сегодня', 'Сегодня ({})'.format(month_rev[2]))
            month_rev_text = month_rev_text.replace('cегодня', 'cегодня ({})'.format(month_rev[2]))
            await __text_splitter(message, month_rev_text, month_rev[0], month_rev[2], batch_size)
    if day:  # Публикация дня
        for day_rev in day[::-1]:
            day_rev_text = day_rev[1].replace('Сегодня', 'Сегодня ({})'.format(day_rev[2]))
            day_rev_text = day_rev_text.replace('cегодня', 'cегодня ({})'.format(day_rev[2]))
            await __text_splitter(message, day_rev_text, day_rev[0], day_rev[2], batch_size)
    if photo:
        await message.answer_photo(photo, caption=title, parse_mode='HTML', protect_content=protect_content)


def __replacer(data: str) -> str:
    """
    Форматирование текста

    Если '.' больше чем 1 в числовом значении фин.показателя
    и первый объект равен 0, то форматируем так '{}.{}{}'(*data_list)

    :param data: Значение из ячейки таблицы с фин.показателями
    :return: Форматированный текст
    """
    data_list = data.split('.')
    if len(data_list) > 2:
        if data_list[0] == '0':
            return '{}.{}{}'.format(*data_list)
        else:
            return '{}{}.{}'.format(*data_list)
    return data


async def get_waiting_time(weekday_to_send: int, hour_to_send: int, minute_to_send: int = 0) -> timedelta:
    """
    Рассчитываем время ожидания перед отправкой рассылки

    :param weekday_to_send: день недели, в который нужно отправить рассылку
    :param hour_to_send: час, в который нужно отправить рассылку
    :param minute_to_send: минуты, в которые нужно отправить рассылку
    return время ожидания перед рассылкой
    """
    # получаем текущее датувремя и день недели
    current_datetime = datetime.now()
    current_weekday = current_datetime.isoweekday()

    # рассчитываем разницу до дня недели, в который нужно отправить рассылку
    days_until_sending = (weekday_to_send - current_weekday + 7) % 7

    # определяем следующую дату рассылки
    datetime_ = datetime(current_datetime.year, current_datetime.month, current_datetime.day, hour_to_send, minute_to_send)
    datetime_for_sending = datetime_ + timedelta(days=days_until_sending)

    # добавляем неделю, если дата прошла
    if datetime_for_sending <= current_datetime:
        datetime_for_sending += timedelta(weeks=1)

    # определяем время ожидания
    time_to_wait = datetime_for_sending - current_datetime

    return time_to_wait


async def wait_until_next_newsletter(
    time_to_wait: int = 0, first_time_to_send: int = 37800, last_time_to_send: int = 61200, logger: Logger.logger = None
) -> None:
    """
    Функция ожидания до следующей рассылки

    :param time_to_wait: Параметр для пропуска ожидания. Для пропуска можно передать любое int значение кроме 0
    :param first_time_to_send: Время для отправки первой рассылки. Время в секундах. Default = 37800  # 10:30
    :param last_time_to_send: Время для отправки последней рассылки. Время в секундах. Default = 61200  # 17:00
    :param logger: logger
    """
    logger = logger or logging.getLogger('bot_runner')

    if time_to_wait != 0:
        logger.info('Запуск ручной рассылки новостей по подписке!')
        return None
    end_of_the_day = 86400  # 86400(всего секунд)/3600(секунд в одном часе) = 24 (00:00 или 24:00)
    current_day = datetime.now()
    current_hour = current_day.hour
    current_minute = current_day.minute
    current_sec = current_day.second
    next_send_time = ''

    current_time = (current_hour * 3600) + (current_minute * 60) + current_sec  # Настоящее Время в секундах
    if first_time_to_send <= current_time <= last_time_to_send:
        time_to_wait = last_time_to_send - current_time
        next_send_time = str(timedelta(seconds=last_time_to_send))
    elif current_time > last_time_to_send:
        time_to_wait = (end_of_the_day - current_time) + first_time_to_send
        next_send_time = str(timedelta(seconds=first_time_to_send))
    elif first_time_to_send > current_time:
        time_to_wait = first_time_to_send - current_time
        next_send_time = str(timedelta(seconds=first_time_to_send))

    logger.info(f'В ожидании рассылки в {next_send_time}. До следующей отправки: {str(timedelta(seconds=time_to_wait))}')
    await asyncio.sleep(time_to_wait)
    return None


def translate_subscriptions_to_object_id(object_dict: dict, subscriptions: list) -> list:
    """
    Получает id объектов (клиента/комоды/отрасли) по названиям объектов из подписок пользователя

    :param object_dict: Словарь объектов {ObjectID: [Object_Names], ...}
    :param subscriptions: Список подписок пользователя. Могут быть как названия, так и альтернативные названия
    return Список id объектов
    """
    return [key for word in subscriptions for key in object_dict if word in object_dict[key]]


async def get_industries_id(handbook: pd.DataFrame) -> list:
    """Получение айди отраслей"""
    handbooks = []
    industry_ids = handbook['industry_id'].tolist()
    for industry_id in list(set(industry_ids)):
        handbooks.append(handbook[handbook['industry_id'] == industry_id].drop_duplicates())
    return handbooks


async def show_ref_book_by_request(chat_id, subject: str, logger: Logger.logger) -> list:
    """Получение айди отраслей"""
    logger.info(f'Сборка справочника для *{chat_id}* на тему {subject}')

    if (subject == 'client') or (subject == 'commodity'):
        handbook = pd.read_sql_query(
            f'SELECT {subject}.name AS object, industry_id, '
            f'industry.name AS industry_name FROM {subject} '
            f'LEFT JOIN industry ON {subject}.industry_id = industry.id',
            con=engine,
        )
    else:
        handbook = pd.read_sql_query(
            'SELECT client_alternative.other_name AS object, '
            'client.industry_id, industry.name AS industry_name FROM client_alternative '
            'INNER JOIN client ON client_alternative.client_id = client.id '
            'INNER JOIN industry ON client.industry_id = industry.id',
            con=engine,
        )
    return await get_industries_id(handbook)


async def __create_fin_table(message: types.Message | types.CallbackQuery, client_name: str,
                             table_type: str, client_fin_table: pd.DataFrame) -> None:
    """
    Формирование таблицы под финансовые показатели и запись его изображения

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param client_name: Наименование клиента финансовых показателей
    :param table_type: Название вкладки для таблицы
    :param client_fin_table: Таблица финансовых показателей
    """
    transformer = dt.Transformer()
    client_fin_table = client_fin_table.rename(columns={'': 'Финансовые показатели'})
    for i, row in client_fin_table.iterrows():
        if row['Финансовые показатели'] in row[client_fin_table.keys().to_list()[1:]].values:
            if not row['Финансовые показатели']:
                client_fin_table.drop(index=i, inplace=True)
            else:
                client_fin_table.loc[i] = pd.Series(
                    {'Финансовые показатели': client_fin_table.loc[i]['Финансовые показатели']})
    client_fin_table.where(pd.notnull(client_fin_table), '')

    png_path = transformer.render_mpl_table(
        client_fin_table, f'financial_indicator_{client_name.replace(" ", "").lower()}_{table_type}', header_columns=0,
        col_width=4, alias=f'{client_name} - {table_type}'.strip().upper(), fin=True, font_size=16
    )
    photo = types.FSInputFile(png_path)
    if isinstance(message, types.Message):
        await message.answer_photo(photo, caption='', parse_mode='HTML', protect_content=texts_manager.PROTECT_CONTENT)
    elif isinstance(message, types.CallbackQuery):
        await message.message.answer_photo(photo, caption='', parse_mode='HTML', protect_content=texts_manager.PROTECT_CONTENT)


async def process_fin_table(message: types.Message | types.CallbackQuery, client_name: str,
                            table_type: str, table_data: str,
                            logger: Logger.logger = None) -> None:
    """
    Создание и отправка таблицы как изображения

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param client_name: Наименование клиента
    :param table_type: Название темы таблицы
    :param table_data: Таблица финансовых показателей в формате str
    :param logger: Логгер
    return None
    """
    logger = logger or logging.getLogger('bot_runner')
    table_data = table_data.replace(' NaN', '""')
    if table_data:
        try:
            df = pd.DataFrame(data=ast.literal_eval(table_data))
        except ValueError:
            logger.error(f'Ошибка при создании таблицы финансовых показателей для {client_name}, не верный данных')
            return None
        await __create_fin_table(message, client_name, table_type, df)
        logger.info(f'{table_type} таблица финансовых показателей для клиента: {client_name} - собрана')
    else:
        logger.info(f'Не найдены данные для {table_type} таблицы клиента: {client_name}')


def get_page_data_and_info(
        all_data_df: pd.DataFrame,
        page: int = 0,
        page_elements: int = PAGE_ELEMENTS_COUNT,
) -> tuple[pd.DataFrame, str, int]:
    """
    Получение информации о странице

    1)Вынимает набор данных, которые должны быть отображены на странице номер {page}
    2)Формирует сообщение: какое кол-во данных отображено на странице из всего данных
    3)Вычисляет кол-во страниц

    :param all_data_df: Набор данных для постраничной навигации
    :param page: Текущая страница
    :param page_elements: Число элементов на странице
    return: (Данные для страницы, сбщ о числе элементов на странице, число страниц всего)
    """
    elements_cnt = len(all_data_df)
    from_ = page * page_elements
    to_ = (page + 1) * page_elements
    to_ = to_ if to_ < elements_cnt else elements_cnt
    data_df = all_data_df[from_: to_]

    from_ = (from_ + 1) if from_ < elements_cnt else elements_cnt
    info = f'{from_}-{to_} из {elements_cnt}'
    return data_df, info, ceil(elements_cnt / page_elements)


def wrap_callback_data(data: str) -> str:
    """Замена : на ;"""
    return data.replace(':', ';')


def unwrap_callback_data(data: str) -> str:
    """Замена ; на :"""
    return data.replace(';', ':')


def next_weekday(d: date | datetime, weekday: int) -> date | datetime:
    """
    Вычисляет дату/дату_время следующего дня недели относительно переданной даты/даты_времени

    :param d: переданная дата/дата_время
    :param weekday: числовое значение дня недели 0-6 (0-пн, 6-вс)
    """
    days_ahead = ((weekday - d.weekday()) % 7) or 7
    return d + timedelta(days_ahead)


def next_weekday_time(from_dt: datetime, weekday: int, hour: int = 0, minute: int = 0) -> datetime:
    """
    Вычисляет ближайшую дату_время относительно переданной по заданным параметрам

    next_weekday_time(datetime(2024, 1, 1, 12, 0), 0, 15, 30) -> datetime(2024, 1, 1, 15, 30)
    next_weekday_time(datetime(2024, 1, 1, 16, 0), 0, 15, 30) -> datetime(2024, 1, 8, 15, 30)

    :param from_dt: переданная дата_время
    :param weekday: числовое значение дня недели 0-6 (0-пн, 6-вс) (-1 для ближайшей даты времени сегодня или завтра)
    :param hour: числовое значение часа недели 0-23
    :param minute: числовое значение минуты недели 0-59
    """
    if (from_dt.weekday() == weekday or weekday == -1) and (from_dt.hour < hour or (from_dt.hour == hour and from_dt.minute < minute)):
        return datetime(from_dt.year, from_dt.month, from_dt.day, hour, minute)

    if weekday < 0:
        weekday = from_dt.weekday() + 1
    ndt = next_weekday(from_dt, weekday)
    return datetime(ndt.year, ndt.month, ndt.day, hour, minute)


def previous_weekday_date(from_date: date, weekday: int) -> date:
    """
    Вычисляет дату последнего прошедшего или текущего дня недели weekday

    :param from_date: переданная дата
    :param weekday: числовое значение дня недели 0-6 (0-пн, 6-вс)
    """
    days_ahead = (-1 * (weekday - from_date.weekday())) % 7
    return from_date - timedelta(days=days_ahead)


async def wait_until(to_dt: datetime) -> None:
    """Спит до переданного datetime"""
    await asyncio.sleep((to_dt - datetime.now()).total_seconds())


async def send_or_edit(
        message: types.CallbackQuery | types.Message,
        msg_text: str,
        keyboard: Optional[types.InlineKeyboardMarkup] = None,
        parse_mode: Optional[str] = 'HTML'
) -> None:
    """
    Отправляет новое сообщение, если message это types.Message

    Изменяет текущее сообщение, если message это types.CallbackQuery

    :param message: Объект сообщения или callback
    :param msg_text: Текст сообщения, длина 1-4096
    :param keyboard: Inline клавиатура
    :param parse_mode: Режим парсинга текста для его форматирования
    """
    # Проверяем, что за тип апдейта. Если Message - отправляем новое сообщение
    if isinstance(message, types.Message):
        await message.answer(msg_text, reply_markup=keyboard, parse_mode=parse_mode)

    # Если CallbackQuery - изменяем это сообщение
    else:
        call = message
        await call.message.edit_text(msg_text, reply_markup=keyboard, parse_mode=parse_mode)


async def send_full_copy_of_message(callback_query: types.CallbackQuery) -> types.Message:
    """
    Отправить копию сообщения тому же пользователю и удалить старое сообщение.

    Отправляет копию текста, копию reply_markup, parse_mode='HTML'

    :param callback_query:  Объект, содержащий информацию о пользователе и сообщении
    :return:                Объект отправленного сообщения, содержащий информацию о пользователе и сообщении
    """
    try:
        await callback_query.message.delete()
    except TelegramBadRequest:
        pass

    return await callback_query.message.send_copy(
        callback_query.message.chat.id,
        reply_markup=callback_query.message.reply_markup,
        parse_mode='HTML',
    )


async def send_pdf(
        callback_query: types.CallbackQuery,
        pdf_files: list[Path],
        caption: str,
        protect_content: bool = texts_manager.PROTECT_CONTENT,
) -> bool:
    """
    Отправка сообщения перед файлами

    Отправка файлов группой (если файлов больше 10, то будет несколько сообщений)

    Если файлов нет, то return False и ничего не отправляет
    :param callback_query: Объект, содержащий информацию о пользователе и сообщении
    :param pdf_files: Список файлов для отправки пользователю
    :param caption: Текст сообщения, которое отправляется перед отправкой файлов (если файлы есть)
    :param protect_content: Защищает отправляемый контент от перессылки и сохранения
    return: Если были отправлены файлы, то True, иначе False
    """
    pdf_files = [f for f in pdf_files if f.exists()]
    if not pdf_files:
        return False

    await callback_query.message.answer(caption, parse_mode='HTML', protect_content=protect_content)

    for i in range(0, len(pdf_files), constants.TELEGRAM_MAX_MEDIA_ITEMS):
        media_group = MediaGroupBuilder()
        for fpath in pdf_files[i: i + constants.TELEGRAM_MAX_MEDIA_ITEMS]:
            media_group.add_document(media=types.FSInputFile(fpath))

        await callback_query.message.bot.send_chat_action(callback_query.message.chat.id, 'upload_document')
        await callback_query.message.answer_media_group(media_group.build(), protect_content=protect_content)

    return True


def clear_text_from_url(text: str) -> str:
    """
    Очистка текста от ссылок.

    :param text:    Текст.
    :return:        Текст без ссылок.
    """
    return re.sub(r'<a href="[^"]*">[^<]*</a>(, )?', '', text)


async def check_relevance_features():
    """Проверка соответствия между названиями фичей в коде и в базе данных."""
    async with async_session() as session:
        db_features = await session.scalars(select(models.Feature.name))
        db_features = list(db_features)

    for code_feature in list(enums.FeatureType):
        if code_feature not in db_features:
            raise ValueError(f'Неизвестное название функциональности в коде: "{code_feature}"')


async def is_user_id_has_access_to_feature(user_id: int, feature: str, session: AsyncSession | None = None) -> bool:
    """
    Проверка доступности ID пользователя определенной фичи в боте.

    :param session:     Сессия бд.
    :param user_id:     ID пользователя.
    :param feature:     Проверяемая на доступность функциональность.
    :return:            Флаг доступности. True - пользователь может работать с фичей, False - фича недоступна.
    """
    if session:
        user = await get_user(session, user_id)
        return await is_user_has_access_to_feature(user, feature, session)
    async with async_session() as ses:
        user = await get_user(ses, user_id)
        return await is_user_has_access_to_feature(user, feature, ses)


async def is_user_has_access_to_feature(user: models.RegisteredUser, feature: str, session: AsyncSession) -> bool:
    """
    Проверка доступности пользователю определенной фичи в боте.

    :param session: Сессия бд.
    :param user:    Сущность пользователя.
    :param feature: Проверяемая на доступность функциональность.
    :return:        Флаг доступности. True - пользователь может работать с фичей, False - фича недоступна.
    """
    role = await get_user_role(session, user)
    if not role:
        return False
    return feature in [f.name for f in role.features]


async def has_access_to_feature_logic(
        feature: str,
        is_need_answer: bool,
        func: Callable,
        args: tuple[Any],
        kwargs: dict[str, Any],
        session: AsyncSession,
) -> Any:
    """
    Логика декоратора has_access_to_feature.

    :param feature:         Название функциональности, которую нужно проверить на доступность.
    :param is_need_answer:  Необходимо ли отправить ответ об "отсутствии прав на использование команды".
    :param func:            Декорируемая функция.
    :param args:            Позиционные аргументы.
    :param kwargs:          Именованные аргументы.
    :param session:         Сессия бд.
    :return:                Обработчик, если пользователю доступна функциональность,
                            либо None с сообщением о недоступности,
                            либо None без сообщения (задекорирована промежуточная функция).
    """
    tg_obj: types.Message | types.CallbackQuery = args[0]
    user_id = tg_obj.from_user.id
    full_name = tg_obj.from_user.full_name
    user_msg = tg_obj.text if isinstance(tg_obj, types.Message) else tg_obj.data
    func_name = func.__name__

    user = await get_user(session, user_id)
    if not user:
        await tg_obj.answer('Неавторизованный пользователь. Отказано в доступе.')
        user_logger.info(f'*{user_id}* Неавторизованный пользователь {full_name} - {user_msg}. Функция: {func_name}()')
        return

    access = await is_user_has_access_to_feature(user, feature, session)
    if access:
        return await func(*args, **kwargs)

    if is_need_answer:
        user_logger.warning(f'*{user_id}* {full_name} - {user_msg} : недостаточно прав. Функция: {func_name}()')
        await tg_obj.answer('У Вас недостаточно прав для использования данной команды.')
    # без отправки сообщения, если это промежуточная функция (обработчик в обработчике)
