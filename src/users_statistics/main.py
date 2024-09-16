"""
Точка входа для сервиса сбора статистики по пользователям.

Собирает статистику использования бота в пн в 9 утра.
"""
import time
import warnings
from datetime import date
from pathlib import Path
from typing import Callable

import schedule

from configs import config
from log.logger_base import Logger, selector_logger
from module.users_statistics import UserStatistics


def get_file_name_with_date(base_file_name: str, dop_info: str = '') -> Path:
    """
    Возвращает путь до файла со статистикой по использованию бота с текущей датой в имени файла

    :param base_file_name: Изначальное имя файла
    :param dop_info: Доп инфа, которая будет добавлена в имя файла
    """
    today = date.today().strftime('%d_%m_%Y')
    stat_fname = Path(base_file_name)
    stat_fname = f'{stat_fname.stem}{("_" + dop_info) if dop_info else ""}_{today}.xlsx'
    return Path(stat_fname)


def collect_stat(collect: Callable[[Path], None], output_fname: str, logger: Logger.logger) -> Path | None:
    """
    Сборка полной статистики

    :param collect: собирает статистику и сохраняет ее в xlsx формате
    :param output_fname: Имя файла, в который будет сохранена статистика
    :param logger: логгер
    :return: Имя файла со статистикой или None
    """
    bot_usage_stat_save_path = get_file_name_with_date(output_fname)

    try:
        logger.info(f'Начало сборки полной статистики {collect.__name__}')
        collect(bot_usage_stat_save_path)
        logger.info(f'Сборка полной статистики {collect.__name__} завершена')
    except Exception as e:
        logger.error(f'Ошибка при сборке полной статистики {collect.__name__}: %s', e)
    else:
        return bot_usage_stat_save_path


def collect_stat_and_send(runner: UserStatistics, logger: Logger.logger) -> None:
    """
    Собирает статистику и отправляет ее на заданные почты

    :param runner: Сборщик статистик
    :param logger: логгер
    """
    stats_funcs = [
        (runner.collect_activity, 'Промты'),
        (runner.collect_users_subscriptions, 'Подписки'),
        (runner.collect_handler_calls, 'Функции'),
    ]

    files_to_send = []
    for collect, output in stats_funcs:
        try:
            fname = collect_stat(collect, output, logger)
        except Exception as e:
            logger.error(f'An error occur: {e}')
        else:
            files_to_send.append(fname)

    # send()


def main():
    """Сборщик статистики использования бота и справочника пользователей"""
    warnings.filterwarnings('ignore')
    # логгер для сохранения действий программы + пользователей
    logger = selector_logger(config.log_file, config.LOG_LEVEL_INFO)
    runner = UserStatistics()

    logger.info('Инициализация сборщика статистики использования бота')

    if config.DEBUG:
        while True:
            collect_stat_and_send(runner, logger)
            time.sleep(5 * 50)

    # сборка происходит каждый понедельник в 09:00
    schedule.every().monday.at('09:00').do(collect_stat_and_send, collect=runner, logger=logger)

    while True:
        schedule.run_pending()
        time.sleep(config.STATS_COLLECTOR_SLEEP_TIME)


if __name__ == '__main__':
    main()
