"""Модуль для периодического сбора котировок."""
import datetime
import multiprocessing
import time
import warnings

import click

from configs import config
from log import sentry
from log.logger_base import Logger, logger
from utils.cli_utils import get_period
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


# ADD check if cant get new data from source
# ADD save updated data time
@click.command()
@click.option(
    '-p',
    '--period',
    default=config.COLLECT_PERIOD,
    show_default=True,
    type=str,
    help='Периодичность сборки котировок\ns - секунды\nm - минуты (значение по умолчанию)\nh - часы\nd - дни',
)
def main(period):
    """Сборщик котировок"""
    sentry.init_sentry(dsn=config.SENTRY_QUOTES_PARSER_DSN)
    try:
        period, scale, scale_txt = get_period(period)
    except ValueError as e:
        print(e)
        return

    warnings.filterwarnings('ignore')
    # логгер для сохранения действий программы + пользователей
    groups_logger_list = [(quotes_class, logger) for quotes_class in get_groups()]

    while True:
        current_period = period
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

        print(f'Ожидание {current_period} {scale_txt} перед следующей сборкой...')
        logger.info(f'Ожидание {current_period} {scale_txt} перед следующей сборкой...')

        for i in range(current_period, 0, -1):
            time.sleep(scale)
            print(f'Ожидание сборки. {i} из {current_period} {scale_txt}')
            logger.info(f'Ожидание сборки. {i} из {current_period} {scale_txt}')


if __name__ == '__main__':
    first_load_quotes()
    main()
