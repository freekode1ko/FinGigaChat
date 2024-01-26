import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import List, Union

import pandas as pd
from aiogram import Bot, types
from aiogram.types import BotCommand

import module.data_transformer as dt
from config import path_to_source
from constants.bot.commands import PUBLIC_COMMANDS
from constants.bot.constants import research_footer
from database import engine
from module.logger_base import Logger


async def set_bot_commands(bot: Bot) -> None:
    commands = []

    for command in PUBLIC_COMMANDS:
        commands.append(BotCommand(command=f'/{command["command"]}', description=command['description']))

    await bot.delete_my_commands()
    await bot.set_my_commands(commands)


async def bot_send_msg(bot: Bot, user_id: Union[int, str], msg: str, delimiter: str = '\n\n') -> None:
    """
    Делит сообщение на батчи, если длина больше допустимой

    :param bot: tg bot instance
    :param user_id: ID пользователя для которого будет произведена отправка
    :param msg: Текст для отправки или подпись к файлу
    :param delimiter: Разделитель текста
    """
    batches = []
    current_batch = ''
    max_batch_length = 4096

    for paragraph in msg.split(delimiter):
        if len(current_batch) + len(paragraph) + len(delimiter) < max_batch_length:
            current_batch += paragraph + delimiter
        else:
            batches.append(current_batch.strip())
            current_batch = paragraph + delimiter

    if current_batch:
        batches.append(current_batch.strip())

    for batch in batches:
        await bot.send_message(user_id, text=batch, parse_mode='HTML', disable_web_page_preview=True)


async def send_msg_to(bot: Bot, user_id, message_text, file_name, file_type) -> None:
    """
    Рассылка текста и/или файлов(документы и фотокарточки) на выбранного пользователя

    :param bot: tg bot instance
    :param user_id: ID пользователя для которого будет произведена отправка
    :param message_text: Текст для отправки или подпись к файлу
    :param file_name: Текст содержащий в себе название сохраненного файла
    :param file_type: Тип файла для отправки. Может быть None, str("Document") и str("Picture")
    return None
    """
    if file_name:
        if file_type == 'photo':
            file = types.FSInputFile('sources/{}.jpg'.format(file_name))
            await bot.send_photo(photo=file, chat_id=user_id, caption=message_text, parse_mode='HTML', protect_content=True)
        elif file_type == 'document':
            file = types.FSInputFile('sources/{}'.format(file_name))
            await bot.send_document(document=file, chat_id=user_id, caption=message_text, parse_mode='HTML', protect_content=True)
    else:
        await bot.send_message(user_id, message_text, parse_mode='HTML', protect_content=True)


async def user_in_whitelist(user: str) -> bool:
    """
    Проверка, пользователя на наличие в списках на доступ

    :param user: Строковое значение по пользователю в формате json. message.from_user.as_json()
    return Булево значение на наличие пользователя в списке
    """
    user_json = json.loads(user)
    user_id = user_json['id']
    whitelist = pd.read_sql_query('SELECT * FROM "whitelist"', con=engine)
    if len(whitelist.loc[whitelist['user_id'] == user_id]) >= 1:
        return True
    return False


async def check_your_right(user: dict) -> bool:
    """
    Проверка прав пользователя

    :param user: Словарь с информацией о пользователе
    return Булевое значение на наличие прав администратора и выше
    """
    user_id = user['id']
    user_series = pd.read_sql_query(f"SELECT user_type FROM whitelist WHERE user_id='{user_id}'", con=engine)
    user_type = user_series.values.tolist()[0][0]
    if user_type == 'admin' or user_type == 'owner':
        return True
    return False


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
    return None
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
            text_group.append(text[batch : batch + batch_size])
        for summ_part in text_group:
            await message.answer(
                '<b>{}</b>\n\n{}\n\n<i>{}</i>'.format(name, summ_part, research_footer, date), parse_mode='HTML', protect_content=True
            )
    else:
        await message.answer(
            '<b>{}</b>\n\n{}\n\n{}\n\n<i>{}</i>'.format(name, giga_ans, research_footer, date), parse_mode='HTML', protect_content=True
        )


async def __sent_photo_and_msg(
    message: types.Message,
    photo: Union[types.InputFile, str],
    day: List[str] = None,
    month: List[str] = None,
    title: str = '',
    source: str = '',
    protect_content: bool = True,
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
    await message.answer_photo(photo, caption=title, parse_mode='HTML', protect_content=protect_content)


def __replacer(data: str) -> str:
    """
    Если '.' больше чем 1 в числовом значении фин.показателя
    и первый объект равен 0, то форматируем так '{}.{}{}'(*data_list)

    :param data: Значение из ячейки таблицы с фин.показателями
    return Форматированный текст
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


async def newsletter_scheduler(
    time_to_wait: int = 0, first_time_to_send: int = 37800, last_time_to_send: int = 61200, logger: Logger.logger = None
) -> None:
    """
    Функция для расчета времени ожидания

    :param time_to_wait: Параметр для пропуска ожидания. Для пропуска можно передать любое int значение кроме 0
    :param first_time_to_send: Время для отправки первой рассылки. Время в секундах. Default = 37800  # 10:30
    :param last_time_to_send: Время для отправки последней рассылки. Время в секундах. Default = 61200  # 17:00
    :param logger: logger
    return None
    """
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

    logger.info(f'В ожидании рассылки в {next_send_time}.' f' До следующей отправки: {str(timedelta(seconds=time_to_wait))}')
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
    handbooks = []
    industry_ids = handbook['industry_id'].tolist()
    for industry_id in list(set(industry_ids)):
        handbooks.append(handbook[handbook['industry_id'] == industry_id].drop_duplicates())
    return handbooks


async def show_ref_book_by_request(chat_id, subject: str, logger: Logger.logger) -> list:
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
            "SELECT REGEXP_REPLACE(client_alternative.other_names, '^.*;', '') AS object, "
            'client.industry_id, industry.name AS industry_name FROM client_alternative '
            'INNER JOIN client ON client_alternative.client_id = client.id '
            'INNER JOIN industry ON client.industry_id = industry.id',
            con=engine,
        )
    return await get_industries_id(handbook)


async def __create_fin_table(message: types.Message, client_name: str, client_fin_table: pd.DataFrame) -> None:
    """
    Формирование таблицы под финансовые показатели и запись его изображения

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param client_name: Наименование клиента финансовых показателей
    :param client_fin_table: Таблица финансовых показателей
    """
    transformer = dt.Transformer()
    client_fin_table = client_fin_table.rename(columns={'name': 'Финансовые показатели'})
    transformer.render_mpl_table(
        client_fin_table, 'financial_indicator', header_columns=0, col_width=4, title='', alias=client_name.strip().upper(), fin=True
    )
    png_path = '{}/img/{}_table.png'.format(path_to_source, 'financial_indicator')
    photo = types.FSInputFile(png_path)
    await message.answer_photo(photo, caption='', parse_mode='HTML', protect_content=True)
