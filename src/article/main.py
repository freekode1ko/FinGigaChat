"""Точка входа для сервиса сбора данных Полианалист с почты."""
import datetime as dt
import time
import warnings
from os import PathLike
from pathlib import Path

import pandas as pd

from configs import config
from configs.config import mail_imap_server, mail_password, mail_username
from constants.enums import Environment
from db import parser_source
from log import sentry
from log.logger_base import Logger, selector_logger
from module.article_process import ArticleProcess
from module.mail_parse import ImapParse

CLIENT_FOLDER_DIR = Path('sources/articles/client')
COMMODITY_FOLDER_DIR = Path('sources/articles/commodity')

CLIENT_FOLDER_DIR.mkdir(exist_ok=True, parents=True)
COMMODITY_FOLDER_DIR.mkdir(exist_ok=True, parents=True)

HOUR_TO_PARSE = dt.timedelta(hours=3, minutes=30)


class ParsePolyanalist:
    """Класс парсер полианалиста"""

    def __init__(self, logger: Logger.logger) -> None:
        """Инициализация парсера полианалиста"""
        self.ap_obj = ArticleProcess(logger)
        self.logger = logger

    @staticmethod
    def imap_func(type_of_article: str, folder_name: PathLike) -> str | None:
        """
        Спарсить почту

        :param type_of_article: Тип новостей (client or commodity)
        :param folder_name:     Имя папки, куда сохранять файл
        :return:                Имя файла с почты, который был сохранен в папку.
        """
        imap_obj = ImapParse()
        imap_obj.get_connection(mail_username, mail_password, mail_imap_server)
        index_of_new_message = imap_obj.get_index_of_new_msg(type_of_article)
        imap_obj.msg = imap_obj.get_msg(index_of_new_message)
        date_msg = imap_obj.get_date()

        if date_msg == dt.datetime.now().date():
            filepath = imap_obj.get_and_download_attachment(folder_name)
        else:
            filepath = None

        imap_obj.close_connection()
        time.sleep(10)

        return filepath

    def model_func(self, type_of_article: str, folder_dir: PathLike) -> tuple[bool, str | None]:
        """Обработать данные полианалиста с почты"""
        filepath = self.imap_func(type_of_article, folder_dir)
        if filepath:
            self.logger.info(f'Скачен файл: {filepath}')
            print(f'Скачен файл: {filepath}')
            df = self.ap_obj.load_file(filepath, type_of_article)
            if not df.empty:
                self.logger.info('Старт обработки новостей с помощью моделей')
                print('Старт обработки новостей с помощью моделей')
                df = self.ap_obj.throw_the_models(df, type_of_article)
                print('Окончание обработки новостей с помощью моделей')
                self.logger.info('Окончание обработки новостей с помощью моделей')
            else:
                self.logger.warning(f'{filepath} - пустой')
                print(f'{filepath} - пустой')
                df[['text_sum', f'{type_of_article}_score', 'cleaned_data', f'{type_of_article}_impact']] = None
            self.logger.info('Сохранение новостей в csv файл')
            df.to_csv(filepath, index=False)
            return True, filepath
        return False, None

    def daily_func(self) -> None:
        """Собрать, обработать и сохранить новости от полианалиста"""
        client_flag = commodity_flag = False
        client_filepath = commodity_filepath = ''
        count_of_attempt = 9
        for attempt in range(count_of_attempt):

            if not client_flag:
                client_flag, client_filepath = self.model_func('client', CLIENT_FOLDER_DIR)

            if not commodity_flag:
                commodity_flag, commodity_filepath = self.model_func('commodity', COMMODITY_FOLDER_DIR)

            if client_flag and commodity_flag:
                break
            else:
                self.logger.info('Ожидание 20 минут')
                time.sleep(20 * 60)

        df_client = (
            pd.read_csv(client_filepath, index_col=False)
            if client_flag
            else pd.DataFrame(
                [],
                columns=['link', 'title', 'date', 'text', 'text_sum', 'client', 'client_impact', 'client_score', 'cleaned_data']
            )
        )

        df_commodity = (
            pd.read_csv(commodity_filepath, index_col=False)
            if commodity_flag
            else (
                pd.DataFrame(
                    [],
                    columns=[
                        'link',
                        'title',
                        'date',
                        'text',
                        'text_sum',
                        'commodity',
                        'commodity_impact',
                        'commodity_score',
                        'cleaned_data',
                    ],
                )
            )
        )

        if client_flag or commodity_flag:
            self.logger.info(f'Получение новостей по клиентам - {client_flag}')
            self.logger.info(f'Получение новостей по коммодам - {commodity_flag}')
            if not df_client.empty or not df_commodity.empty:
                self.ap_obj.merge_client_commodity_article(df_client, df_commodity)
                self.ap_obj.drop_duplicate()
                self.ap_obj.make_text_sum()
                self.ap_obj.apply_gigachat_filtering()
                self.ap_obj.remove_html_tags()
                self.ap_obj.save_tables()
                parser_source.update_get_datetime(source_name='Полианалист')
            else:
                self.logger.warning('Таблицы с новостями пустые')
                print('Таблицы с новостями пустые')

            if client_flag and commodity_flag:
                self.logger.info('Новости о клиентах и товарах обработаны')
                print('Новости о клиентах и товарах обработаны')
            elif client_flag:
                self.logger.warning('Обработаны только новости о клиентах')
                print('Обработаны только новости о клиентах')
            else:
                self.logger.warning('Обработаны только новости о товарах')
                print('Обработаны только новости о товарах')
        else:
            self.logger.error('Не были получены новости')
            print('Не были получены новости')


def main() -> None:
    """Запустить сервис сбора данных полианалиста с почты"""
    sentry.init_sentry(dsn=config.SENTRY_POLYANALIST_PARSER_DSN)
    warnings.filterwarnings('ignore')
    # инициализируем логгер
    logger = selector_logger(config.log_file)
    # запускаем ежедневное получение/обработку новостей от полианалиста
    parser = ParsePolyanalist(logger)
    first_try = 1  # запуск на деве сразу же, если это первый прогон
    while True:
        # высчитываем время ожидания
        current_time = dt.datetime.now().time()
        current_time_timedelta = dt.timedelta(hours=current_time.hour, minutes=current_time.minute)
        delta_time = (HOUR_TO_PARSE - current_time_timedelta).seconds
        logger.debug(f'Время ожидания в часах - {delta_time / 3600}')
        if (not config.DEBUG and not config.ENV == Environment.STAGE) or not first_try:
            time.sleep(delta_time)

        logger.info('Запуск pipeline с новостями от полианалиста')
        print('Запуск pipeline с новостями от полианалиста')
        parser.daily_func()
        print('Конец pipeline с новостями от полианалиста\nОжидайте следующий день\n')
        logger.info('Конец pipeline с новостями от полианалиста\n')
        first_try = 0


if __name__ == '__main__':
    main()
