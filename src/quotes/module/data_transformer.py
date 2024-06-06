"""Набор инструментов для получения данных из различных источников и обработка даты"""
import datetime
import os

import pandas as pd

from configs import config
from module import weekly_pulse_parse as wp_parse


class Transformer:
    """Класс для выполнения различных операций по преобразованию данных."""

    @staticmethod
    def load_urls_as_list(path: str, filed_name: str) -> pd.DataFrame:
        """
        Загрузить список ссылок из Excel

        :param path: Путь до .xlsx файла
        :param filed_name: Название колонки, где хранится все ссылки
        :return: Список ссылок
        """
        return pd.read_excel(path)[['Алиас', 'Блок', filed_name]].values.tolist()

    @staticmethod
    def get_table_from_html(euro_standard: bool, html: str):
        """
        Получение всех таблиц из html

        :param euro_standard: Использовать европейский стандарт разделителя в числах?
        :param html: HTML как string
        :return: Список таблиц со страницы
        """
        # if euro_standard:
        #     return pd.read_html(html)
        html_rep = html.replace('.', ',')
        return pd.read_html(html_rep, decimal=',', thousands='.')

    @staticmethod
    def unix_to_default(timestamp):
        """
        Преобразовать UNIX-время в мировой стандарт времени

        :param timestamp: Временная отметка в формате UNIX
        """
        date_time = datetime.datetime.fromtimestamp(timestamp / 1000)
        formatted_date = date_time.strftime('%Y-%m-%dT%H:%M:%S')
        return formatted_date

    @staticmethod
    def default_to_unix():
        """Преобразовать мировое время в UNIX-формат"""
        now = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        date_time = datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
        unix_timestamp = int(date_time.timestamp())
        return str(unix_timestamp)


class Newsletter:
    """Создает текста для рассылок"""

    __newsletter_dict = dict(weekly_result='Основные события прошедшей недели', weekly_event='Календарь и прогнозы текущей недели')

    @classmethod
    def get_newsletter_dict(cls):
        """Возвращает словарь с типами рассылок и их описаниями."""
        return cls.__newsletter_dict

    @classmethod
    def make_weekly_result(cls):
        """Создает текст для рассылки 'Итоги недели'"""
        title = 'Итоги недели'
        weekly_dir = os.path.join(config.path_to_source, 'weeklies')
        slides_fnames = wp_parse.ParsePresentationPDF.get_fnames_by_type(wp_parse.ReportTypes.weekly_results)
        img_path_list = [os.path.join(weekly_dir, i) for i in slides_fnames]
        newsletter = f'<b>{title}</b>\n' f''
        return title, newsletter, img_path_list

    @classmethod
    def make_weekly_event(cls):
        """Создает текст для рассылки 'Что нас ждет на этой неделе?'"""
        title = 'Что нас ждет на этой неделе?'
        weekly_dir = os.path.join(config.path_to_source, 'weeklies')
        slides_fnames = wp_parse.ParsePresentationPDF.get_fnames_by_type(wp_parse.ReportTypes.weekly_event)
        img_path_list = [os.path.join(weekly_dir, i) for i in slides_fnames]
        newsletter = f'<b>{title}</b>\n' f''
        return title, newsletter, img_path_list
