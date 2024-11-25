"""Точка входа для сервиса сбора аналитических отчетов с CIB Research и сбора котировок через Selenium."""
import asyncio
import datetime
import time
import warnings

import schedule

from configs import config
from log import sentry
from log.logger_base import Logger, selector_logger
from parsers.cib import ResearchAPIParser


def get_next_collect_datetime(next_research_getting_time: str) -> datetime.datetime:
    """
    Возвращает дату_время следующей сборки

    :param next_research_getting_time: строка формата %H:%M
    """
    now = datetime.datetime.now()
    next_collect_dt = datetime.datetime.strptime(next_research_getting_time, '%H:%M')
    next_collect_dt = datetime.datetime(now.year, now.month, now.day, next_collect_dt.hour, next_collect_dt.minute)

    if next_collect_dt < now:
        next_collect_dt += datetime.timedelta(days=1)
    return next_collect_dt


async def run_parse_cib(logger: Logger.logger) -> None:
    """
    Запуск парсинга портала CIB Research

    :param logger: логгер
    """
    logger.info('Старт парсинга финансовых показателей по клиентам в CIB')
    try:
        await ResearchAPIParser(logger).get_fin_summary()
    except Exception as e:
        logger.error('Во время парсинга финансовых показателей по клиентам в CIB произошла ошибка: %s', e)

    logger.info('Старт парсинга отчетов с CIB')
    try:
        await ResearchAPIParser(logger).parse_pages()
    except Exception as e:
        logger.error('Во время парсинга отчетов c CIB произошла ошибка: %s', e)


def run_researches_getter(next_research_getting_time: str, logger: Logger.logger) -> None:
    """
    Запуск сборки отчетов и котировок.

    :param next_research_getting_time: Время следующей сборки данных в формате HH:MM
    :param logger: логгер
    """
    start_tm = time.time()
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(run_parse_cib(logger))
    except Exception as e:
        logger.error('CIB: сборка завершилась с ошибкой: %s', e)
    else:
        logger.info('CIB: сборка успешно завершилась!')
    finally:
        loop.close()

    work_time = time.time() - start_tm
    end_dt = datetime.datetime.now().strftime(config.INVERT_DATETIME_FORMAT)
    next_collect_dt = get_next_collect_datetime(next_research_getting_time).strftime(config.INVERT_DATETIME_FORMAT)
    end_msg = f'Сборка завершена за {work_time:.3f} секунд в {end_dt}. Следующая сборка в {next_collect_dt}'
    print(end_msg)
    logger.info(end_msg)


def main():
    """Сборщик отчетов с портала CIB Research, время сборки в config.RESEARCH_GETTING_TIMES_LIST."""
    sentry.init_sentry(dsn=config.SENTRY_RESEARCH_PARSER_DSN)

    warnings.filterwarnings('ignore')
    logger = selector_logger(config.log_file, config.LOG_LEVEL_INFO)

    res_get_times_len = len(config.RESEARCH_GETTING_TIMES_LIST)
    if config.DEBUG:
        next_collect_time = config.RESEARCH_GETTING_TIMES_LIST[(0 + 1) % res_get_times_len]
        run_researches_getter(next_collect_time, logger)

    run_researches_getter('12:00', logger)
    for index, collect_time in enumerate(config.RESEARCH_GETTING_TIMES_LIST):
        next_collect_time = config.RESEARCH_GETTING_TIMES_LIST[(index + 1) % res_get_times_len]

        schedule.every().day.at(collect_time).do(
            run_researches_getter,
            next_research_getting_time=next_collect_time,
            logger=logger
        )

    while True:
        schedule.run_pending()
        time.sleep(config.STATS_COLLECTOR_SLEEP_TIME)


if __name__ == '__main__':
    main()
