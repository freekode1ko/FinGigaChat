import time
import warnings
from pathlib import Path

import schedule
from sqlalchemy import Engine, NullPool, create_engine

import config
from module.logger_base import Logger, selector_logger
from module.statistics import UserStatistics


def collect_stat(engine: Engine, logger: Logger.logger) -> None:
    runner = UserStatistics(engine)

    try:
        logger.info('Начало сборки статистики использования бота')
        runner.collect_bot_usage()
        logger.info('Сборка завершена')
    except Exception as e:
        logger.error(f'Ошибка при сборке статистикии: {e}')


def main():
    """Сборщик статистики использования бота и справочника пользователей"""
    warnings.filterwarnings('ignore')
    # логгер для сохранения действий программы + пользователей
    logger = selector_logger(Path(__file__).stem, config.LOG_LEVEL_INFO)
    engine = create_engine(config.psql_engine, poolclass=NullPool)  # FIXME унести в класс работы с БД

    logger.info('Инициализация сборщика статистики использования бота')
    schedule.every().monday.at('9:00').do(collect_stat, engine=engine, logger=logger)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    main()
