"""Апи"""

import asyncio

import config
from agent_app import logger
from utils.tool_functions.preparing_meeting.run import get_preparing_for_meeting

logger.info('Инициализация приложения')

loop = asyncio.get_event_loop()
# TODO: Для работы всех функций по апи надо получить:
#  название компании, специальный параметр, id пользователя, thread_id (надо для каждого запроса делать уникальный)
client_name = 'Газпром'
special_info = ''
user_id = '1'
thread_id = '1'
loop.run_until_complete(get_preparing_for_meeting(client_name, special_info, user_id, thread_id))
# TODO: отправляем как итоговый ответ, так и промежуточные изменения
