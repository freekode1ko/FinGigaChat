import datetime
import os

import pandas as pd

from configs import config
from module import weekly_pulse_parse as wp_parse


class Transformer:
    @staticmethod
    def load_urls_as_list(path: str, filedName: str) -> pd.DataFrame:
        """
        Get sources url from excel file
        :param path: path to .xlsx file
        :param filedName: Column name where holding all urls
        :return: return list with urls
        """
        return pd.read_excel(path)[['Алиас', 'Блок', filedName]].values.tolist()

    @staticmethod
    def get_table_from_html(euro_standard: bool, html: str):
        """
        Take all tables from html code
        :param euro_standard: Bool value for separators of decimals and thousands
        :param html: HTML codes as text
        :return: list with DataFrames
        """
        # if euro_standard:
        #     return pd.read_html(html)
        html_rep = html.replace('.', ',')
        return pd.read_html(html_rep, decimal=',', thousands='.')

    @staticmethod
    def unix_to_default(timestamp):
        """
        Transform unix-time to world-time
        :param timestamp: unix formatted timestamp
        """

        date_time = datetime.datetime.fromtimestamp(timestamp / 1000)
        formatted_date = date_time.strftime('%Y-%m-%dT%H:%M:%S')
        return formatted_date

    @staticmethod
    def default_to_unix():
        """
        Transform world-time now to unix-time
        """

        now = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        date_time = datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
        unix_timestamp = int(date_time.timestamp())
        return str(unix_timestamp)


class Newsletter:
    """Создает текста для рассылок"""

    __newsletter_dict = dict(weekly_result='Основные события прошедшей недели', weekly_event='Календарь и прогнозы текущей недели')

    @classmethod
    def get_newsletter_dict(cls):
        return cls.__newsletter_dict

    @classmethod
    def make_weekly_result(cls):
        """Создает текст для рассылки "Итоги недели" """
        title = 'Итоги недели'
        weekly_dir = os.path.join(config.path_to_source, 'weeklies')
        slides_fnames = wp_parse.ParsePresentationPDF.get_fnames_by_type(wp_parse.ReportTypes.weekly_results)
        img_path_list = [os.path.join(weekly_dir, i) for i in slides_fnames]
        newsletter = f'<b>{title}</b>\n' f''
        return title, newsletter, img_path_list

    @classmethod
    def make_weekly_event(cls):
        """Создает текст для рассылки "Что нас ждет на этой неделе?" """
        title = 'Что нас ждет на этой неделе?'
        weekly_dir = os.path.join(config.path_to_source, 'weeklies')
        slides_fnames = wp_parse.ParsePresentationPDF.get_fnames_by_type(wp_parse.ReportTypes.weekly_event)
        img_path_list = [os.path.join(weekly_dir, i) for i in slides_fnames]
        newsletter = f'<b>{title}</b>\n' f''
        return title, newsletter, img_path_list
