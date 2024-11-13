"""Модуль для периодического сбора котировок."""
import datetime
import multiprocessing
import time
import warnings

from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.blocking import BlockingScheduler

from configs import config
from log import sentry
from log.logger_base import Logger, logger
from utils.quotes import get_groups
from utils.quotes.quotes import load_quotes, update_quote_data
from utils.run_async import run_async


def collect_quotes_group(QuotesGetterClass, logger: Logger.logger) -> bool:
    """
    Функция для сбора котировок для заданной группы котировок.

    :param QuotesGetterClass: Класс, реализующий функциональность получения котировок.
    :param logger: Логгер для записи действий и ошибок.
    :return: True, если сбор данных прошел успешно, False в случае ошибки.
    """
    is_success = True
    group_name = QuotesGetterClass.get_group_name()
    logger.info(f'Инициализация сборщика котировок {group_name}')
    runner = QuotesGetterClass(logger)
    logger.info('Загрузка прокси')
    runner.parser_obj.set_proxy_addresses()

    try:
        logger.info(f'Начало сборки котировок {group_name}')
        runner.collect()
    except Exception as e:
        logger.error(f'Ошибка при сборке котировок {group_name}: %s', e)
        is_success = False

    logger.info(f'Запись даты и времени последней успешной сборки котировок {group_name}')
    runner.save_date_of_last_build()  # FIXME избавиться
    return is_success


def first_load_quotes():
    """Первоначальная загрузка котировок"""
    logger.info('Начата первоначальная загрузка котировок')
    print('Начата первоначальная загрузка котировок')
    try:
        run_async(load_quotes)
    except Exception as e:
        logger.error(f'Загрузка котировок закончилась с ошибкой:{e}')
        print(f'Загрузка котировок закончилась с ошибкой:{e}')
    else:
        logger.info('Загрузка котировок закончилась успешно')
        print('Загрузка котировок закончилась успешно')


def update_quotes():
    """Сборка/обновление котировок"""
    logger.info('Начала сборки котировок')
    try:
        run_async(update_quote_data)
    except Exception as e:
        logger.error(f'Сборка котировок закончилась с ошибкой:{e}')
    else:
        logger.info('Сборка котировок закончилась')


def main():
    """Сборщик котировок"""
    groups_logger_list = [(quotes_class, logger) for quotes_class in get_groups()]

    start_tm = time.time()
    start_msg = 'Запуск пула процессов для сборки котировок по группам'
    print(start_msg)
    logger.info(start_msg)

    with multiprocessing.Pool(config.QUOTES_PROCESSING_PROC_NUM) as pool:
        results = pool.starmap(collect_quotes_group, groups_logger_list)

    work_time = time.time() - start_tm
    end_dt = datetime.datetime.now().strftime(config.INVERT_DATETIME_FORMAT)
    end_msg = f'Сборка в {end_dt} завершена за {work_time:.3f} секунд'
    print(end_msg)
    logger.info(end_msg)

    collect_end_msg = f'Сборщиков упало {results.count(False)} из {len(results)}'
    print(collect_end_msg)
    logger.info(collect_end_msg)

    update_quotes()

    print('Ожидание перед следующей сборкой...')
    logger.info('Ожидание перед следующей сборкой...')


if __name__ == '__main__':
    sentry.init_sentry(dsn=config.SENTRY_QUOTES_PARSER_DSN)
    warnings.filterwarnings('ignore')

    first_load_quotes()

    scheduler = BlockingScheduler()
    trigger = CronTrigger(minute='0,15,30,45')
    scheduler.add_job(main, trigger=trigger)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
