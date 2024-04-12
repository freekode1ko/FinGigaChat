from aiogram import Bot
from configs import config


bot = Bot(token=config.api_token)

'''
import datetime as dt
from typing import Any

import dramatiq
from dramatiq.middleware.asyncio import AsyncIO
from dramatiq.brokers.redis import RedisBroker

from constants.constants import REMEMBER_TIME
from db.web_app.meeting import get_user_meetings_for_notification

broker = RedisBroker(url='redis://127.0.0.1', middleware=[AsyncIO()])
broker.flush_all()
dramatiq.set_broker(broker=broker)


@dramatiq.actor()
async def send_notification(user_id: int, meeting_theme: str, msg: str):
    msg = msg.format(meeting_theme=meeting_theme)
    await bot.send_message(user_id, text=f'<b>Напоминание:</b>\n{msg}', parse_mode='HTML')


def send_dramatiq_all_data():
    """Формирование и отправка сообщения в очередь."""
    meetings = get_user_meetings_for_notification()
    for rem_time_dict in REMEMBER_TIME.values():
        for meeting in meetings:
            cur_time = dt.datetime.now()
            rem_time = rem_time_dict['minutes']
            dt_notification = meeting['date_start'] + dt.timedelta(hours=meeting['timezone']) - dt.timedelta(minutes=rem_time)
            if dt_notification < cur_time:
                print(meeting['theme'], '-', 'no')
                continue
            delay_val = dt_notification - cur_time
            print(meeting['theme'], '-', 'yes', meeting['theme'], 'in', dt_notification)

            send_notification.send_with_options(
                args=(meeting['user_id'], meeting['theme'], rem_time_dict['msg']),
                delay=delay_val
            )


def send_schedular_new_data(meeting: dict[str, Any]):
    """Формирование и отправка сообщения в очередь."""
    for rem_time_dict in REMEMBER_TIME.values():
        cur_time = dt.datetime.now()
        rem_time = rem_time_dict['minutes']
        dt_notification = meeting['date_start'] + dt.timedelta(hours=meeting['timezone']) - dt.timedelta(minutes=rem_time)
        if dt_notification < cur_time:
            print(meeting['theme'], '-', 'no')
            continue
        delay_val = dt_notification - cur_time
        print(meeting['theme'], '-', 'yes', meeting['theme'], 'in', delay_val)

        send_notification.send_with_options(
            args=(meeting['user_id'], meeting['theme'], rem_time_dict['msg']),
            delay=delay_val)
'''
