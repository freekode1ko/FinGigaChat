import time
import warnings
from datetime import date, timedelta
from pathlib import Path

import schedule

import config
from module.logger_base import Logger, selector_logger
from module.statistics import UserStatistics


def get_file_name_with_date(base_file_name: str, dop_info: str = '') -> Path:
    """
    Возвращает путь до файла со статистикой по использованию бота с текущей датой в имени файла

    :param base_file_name: Изначальное имя файла
    :param dop_info: Доп инфа, которая будет добавлена в имя файла
    """
    today = date.today().strftime('%d_%m_%Y')
    stat_fname = Path(base_file_name)
    stat_fname = f'{stat_fname.stem}_{dop_info}_{today}.{stat_fname.suffix}'
    return Path(stat_fname)


def collect_all_stat(runner: UserStatistics, logger: Logger.logger) -> None:
    """
    Сборка полной статистики по использованию бота

    :param runner: UserStatistics собирает статистику и сохраняет ее в xlsx формате
    :param logger: логгер
    """
    bot_usage_stat_save_path = get_file_name_with_date(config.BOT_USAGE_STAT_FILE_NAME, 'all')

    try:
        logger.info('Начало сборки полной статистики использования бота')
        runner.collect_bot_usage_over_period(bot_usage_stat_save_path)
        logger.info('Сборка полной статистики использования бота завершена')
    except Exception as e:
        logger.error('Ошибка при сборке полной статистики использования бота: %s', e)


def collect_last_days_stat(runner: UserStatistics, logger: Logger.logger, days: int = config.NUM_DAYS_FOR_WHICH_STATS_COLLECT) -> None:
    """
    Сборка статистики по использованию бота за последнюю неделю

    :param runner: UserStatistics собирает статистику и сохраняет ее в xlsx формате
    :param logger: логгер
    :param days: количество дней, за которые собирается статистика вплоть до текущего дня
    """
    to_date = date.today()
    from_date = to_date - timedelta(days=days)
    bot_usage_stat_save_path = get_file_name_with_date(config.BOT_USAGE_STAT_FILE_NAME, 'last_week_upto')

    try:
        logger.info(f'Начало сборки статистики использования бота за последние {days} дней')
        runner.collect_bot_usage_over_period(bot_usage_stat_save_path, from_date=from_date, to_date=to_date)
        logger.info(f'Сборка статистики по использованию бота за последние {days} дней завершена')
    except Exception as e:
        logger.error('Ошибка при сборке статистики по использованию бота за последние %s дней: %s', days, e)


def collect_users_data(runner: UserStatistics, logger: Logger.logger) -> None:
    """
    Сборка каталога пользователей AI-помощника

    :param runner: UserStatistics собирает статистику и сохраняет ее в xlsx формате
    :param logger: логгер
    """
    users_data_save_path = get_file_name_with_date(config.USERS_DATA_FILE_NAME, 'all')

    try:
        logger.info('Начало сборки каталога пользователей AI-помощника')
        runner.collect_users_data(users_data_save_path)
        logger.info('Сборка каталога пользователей завершена')
    except Exception as e:
        logger.error('Ошибка при сборке каталога пользователей: %s', e)


def main():
    """Сборщик статистики использования бота и справочника пользователей"""
    warnings.filterwarnings('ignore')
    # логгер для сохранения действий программы + пользователей
    logger = selector_logger(Path(__file__).stem, config.LOG_LEVEL_INFO)
    runner = UserStatistics()

    logger.info('Инициализация сборщика статистики использования бота')

    # сборка происходит каждый понедельник в 09:00
    schedule.every().monday.at('09:00').do(collect_all_stat, runner=runner, logger=logger)
    schedule.every().monday.at('09:00').do(collect_last_days_stat, runner=runner, logger=logger)
    schedule.every().monday.at('09:00').do(collect_users_data, runner=runner, logger=logger)

    while True:
        schedule.run_pending()
        time.sleep(config.STATS_COLLECTOR_SLEEP_TIME)


if __name__ == '__main__':
    main()
