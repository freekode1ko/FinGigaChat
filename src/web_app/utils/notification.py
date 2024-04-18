import datetime as dt
from typing import Any

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_API_TOKEN, REMEMBER_TIME, BASE_TIME_FORMAT
from db.meeting import change_notify_flag, get_user_meetings_for_notification
from log.logger_base import Logger


bot = Bot(BOT_API_TOKEN)
scheduler = AsyncIOScheduler()


async def send_notification(
        logger: Logger.logger,
        user_id: int,
        meeting_theme: str,
        meeting_date_start: dt.datetime,
        col_key: str,
        msg: str
):
    """
    Отправка напоминания о встрече.

    :param user_id: id пользователя
    :param logger: логгер
    :param meeting_theme: тема встречи
    :param meeting_date_start: время начала встречи
    :param col_key: ключ, по которому будет находиться нужный столбец в UserMeeting
                    для изменения флага отправки напоминания
    :param msg: сообщение с ботом
    """
    msg = msg.format(meeting_theme=meeting_theme, time=meeting_date_start.time().strftime(BASE_TIME_FORMAT))
    await bot.send_message(user_id, text=f'<b>Напоминание:</b>\n{msg}', parse_mode='HTML')
    change_notify_flag(user_id, col_key)
    logger.info('Пользователь %s получил напоминание о встрече в %s UTC' % (user_id, str(dt.datetime.utcnow())))


def add_notify_job(logger: Logger.logger, meeting: dict[str, Any] | None = None):
    """
    Добавление задач-напоминалок по только что созданной встрече или по всем предстоящим встречам из базы данных.

    :param logger: логгер
    :param meeting: данные о только что созданной встрече
    """
    meetings = [meeting, ] if meeting else get_user_meetings_for_notification()

    for key, rem_time_dict in REMEMBER_TIME.items():
        for meeting in meetings:
            dt_notification = meeting['date_start'] + dt.timedelta(hours=meeting['timezone'])
            dt_notification -= dt.timedelta(minutes=rem_time_dict['minutes'])

            if dt_notification < dt.datetime.now():
                continue

            scheduler.add_job(
                send_notification,
                args=(logger, meeting['user_id'], meeting['theme'], meeting['date_start'], key, rem_time_dict['msg']),
                trigger='date',
                run_date=dt_notification,
                timezone='Europe/Moscow'
            )
            logger.info('Для пользователя %s добавлена задача-напоминание в %s' % (meeting['user_id'], dt_notification))
