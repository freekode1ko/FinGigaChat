import datetime as dt
from typing import Any, Optional

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_API_TOKEN, REMEMBER_TIME, BASE_TIME_FORMAT
from db.meeting import change_notify_counter, get_user_meetings_for_notification
from log.logger_base import Logger


bot = Bot(BOT_API_TOKEN)
scheduler = AsyncIOScheduler()


async def send_notification(
        logger: Logger.logger,
        meeting_id: int,
        user_id: int,
        meeting_theme: str,
        meeting_date_start: dt.datetime,
        msg: str
) -> None:
    """
    Отправка напоминания о встрече.

    :param meeting_id: id встречи
    :param user_id: id пользователя
    :param logger: логгер
    :param meeting_theme: тема встречи
    :param meeting_date_start: время начала встречи
    :param msg: сообщение с ботом
    """
    msg = msg.format(meeting_theme=meeting_theme, time=meeting_date_start.time().strftime(BASE_TIME_FORMAT))
    await bot.send_message(user_id, text=f'<b>Напоминание:</b>\n{msg}', parse_mode='HTML')
    await change_notify_counter(meeting_id)
    logger.info('Пользователь %s получил напоминание о встрече в %s UTC', user_id, str(dt.datetime.utcnow()))


async def add_notify_job(logger: Logger.logger, meeting: Optional[dict[str, Any]] = None):
    """
    Добавление задач-напоминалок по только что созданной встрече или по всем предстоящим встречам из базы данных.

    :param logger: логгер
    :param meeting: данные о только что созданной встрече
    """
    meetings = [meeting, ] if meeting else await get_user_meetings_for_notification()

    for rem_time_dict in REMEMBER_TIME.values():
        for meeting in meetings:
            dt_notification = meeting['date_start'] + dt.timedelta(hours=meeting['timezone'])
            dt_notification -= dt.timedelta(minutes=rem_time_dict['minutes'])

            if dt_notification < dt.datetime.now():
                continue

            try:
                scheduler.add_job(
                    send_notification,
                    args=(logger, meeting['meeting_id'], meeting['user_id'], meeting['theme'],
                          meeting['date_start'], rem_time_dict['msg']),
                    trigger='date',
                    run_date=dt_notification,
                    timezone='Europe/Moscow'
                )
                logger.info('Для встречи %s добавлена задача-напоминание в %s', meeting['meeting_id'], dt_notification)
            except Exception as e:
                logger.error('При добавлении задачи-напоминание по встрече %s возникла ошибка: %s', meeting['meeting_id'], e)
