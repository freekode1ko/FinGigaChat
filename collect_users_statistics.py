import config
import schedule
import time
import warnings
from datetime import date, timedelta
from module.logger_base import Logger, selector_logger
from module.statistics import UserStatistics
from pathlib import Path
from sqlalchemy import Engine, NullPool, create_engine


def get_stat_save_path_with_date(base_file_name: str, dop_info: str = '') -> Path:
    """Возвращает путь до файла со статистикой по использованию бота с текущей датой в имени файла"""
    today = date.today().strftime('%d_%m_%Y')
    stat_fname = Path(base_file_name)
    stat_fname = f'{stat_fname.stem}_{dop_info}_{today}.{stat_fname.suffix}'
    return Path(config.STATISTICS_PATH, stat_fname)


def collect_all_stat(engine: Engine, logger: Logger.logger) -> None:
    """Сборка полной статистики по использованию бота"""
    runner = UserStatistics(engine)

    bot_usage_stat_save_path = get_stat_save_path_with_date(config.BOT_USAGE_STAT_FILE_NAME, 'all')

    try:
        logger.info('Начало сборки полной статистики использования бота')
        runner.collect_bot_usage(bot_usage_stat_save_path)
        logger.info('Сборка завершена')
    except Exception as e:
        logger.error(f'Ошибка при сборке статистикии: {e}')


def collect_last_days_stat(
        engine: Engine, logger: Logger.logger, days: int = config.NUM_DAYS_FOR_WHICH_STATS_COLLECT
) -> None:
    """Сборка статистики по использованию бота за последнюю неделю"""
    runner = UserStatistics(engine)

    to_date = date.today()
    from_date = to_date - timedelta(days=days)
    bot_usage_stat_save_path = get_stat_save_path_with_date(config.BOT_USAGE_STAT_FILE_NAME, 'last_week_upto')

    try:
        logger.info(f'Начало сборки статистики использования бота за последние {days} дней')
        runner.collect_bot_usage_over_period(bot_usage_stat_save_path, from_date=from_date, to_date=to_date)
        logger.info('Сборка завершена')
    except Exception as e:
        logger.error(f'Ошибка при сборке статистикии: {e}')


def collect_users_data(engine: Engine, logger: Logger.logger) -> None:
    """Сборка каталога пользователей AI-помощника"""
    runner = UserStatistics(engine)

    users_data_save_path = get_stat_save_path_with_date(config.USERS_DATA_FILE_NAME, 'all')

    try:
        logger.info('Начало сборки каталога пользователей AI-помощника')
        runner.collect_users_data(users_data_save_path)
        logger.info('Сборка завершена')
    except Exception as e:
        logger.error(f'Ошибка при сборке статистикии: {e}')


def main() -> None:
    """Сборщик статистики использования бота и справочника пользователей"""
    warnings.filterwarnings('ignore')
    # логгер для сохранения действий программы + пользователей
    logger = selector_logger(Path(__file__).stem, config.LOG_LEVEL_INFO)
    engine = create_engine(config.psql_engine, poolclass=NullPool)  # FIXME унести в класс работы с БД
    stat_path = Path(config.STATISTICS_PATH)

    if not stat_path.exists():
        stat_path.mkdir()

    logger.info('Инициализация сборщика статистики использования бота')

    # сборка происходит каждый понедельник в 09:00
    schedule.every().monday.at('9:00').do(collect_all_stat, engine=engine, logger=logger)
    schedule.every().monday.at('9:00').do(collect_last_days_stat, engine=engine, logger=logger)
    schedule.every().monday.at('9:00').do(collect_users_data, engine=engine, logger=logger)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    main()
