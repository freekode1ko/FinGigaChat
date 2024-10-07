"""Функция для запуска асинхронной функции"""
import asyncio

from configs import config
from log.logger_base import selector_logger

logger = selector_logger(config.log_file, config.LOG_LEVEL_INFO)


def run_async(func, *args, **kwargs):
    """Функция для запуска асинхронной функции"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(func(*args, **kwargs))
    except Exception as e:
        logger.error('CIB: сборка завершилась с ошибкой: %s', e)
        raise e
    else:
        logger.info('CIB: сборка успешно завершилась!')
    finally:
        loop.close()
