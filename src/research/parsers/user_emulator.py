import json
import time

import pandas as pd
from bs4 import BeautifulSoup
from configs import config
from log.logger_base import Logger
from module import data_transformer as Transformer
from selenium.webdriver.common.by import By


class InvestingAPIParser:
    """
    Class for InvestingAPI parsing
    """

    def __init__(self, driver, logger: Logger.logger):
        self.driver = driver
        self._logger = logger

    def get_graph_investing(self, url: str):
        """
        Get plot data of investing.com api
        :param url: investing.com api url
        :return: price chart df
        """
        self._logger.info('Начала загрузки данных для графика с investing.com')
        self.driver.get(url)
        data = self.driver.find_element(By.ID, 'json').text
        json_obj = json.loads(data)
        self._logger.info('Обработка данных для графика с investing.com')
        df = pd.DataFrame()
        for day in json_obj['data']:
            date = Transformer.Transformer.unix_to_default(day[0])
            x = day[0]
            y = day[4]
            row = {'date': date, 'x': x, 'y': y}
            df = pd.concat([df, pd.DataFrame(row, index=[0])], ignore_index=True)
        self._logger.info('Данные для графика готовы')
        return df

    def get_streaming_chart_investing(self, url: str):
        """
        Get streaming chart data of investing.com
        :param url: rows of text of money review
        :return: price chart df
        """
        self._logger.info('Обработка данных для стримингового графика с investing.com')
        url = f'{url}-streaming-chart'
        self.driver.get(url)
        data = self.driver.find_element(By.CSS_SELECTOR, "div[data-test='instrument-price-last']").text.replace(',',
                                                                                                                '.')

        return data


class MetalsWireParser:
    """
    Class for MetalsWire table data parsing
    """

    def __init__(self, driver, logger: Logger.logger):
        table_link = config.table_link
        self._logger = logger
        self.driver = driver
        self.table_link = table_link

    def get_table_data(self):
        """
        Get table data of MetalsWire
        :return: commodities price chart df
        """
        self._logger.info('Сборка табличных данных для MetalsWire')
        self.driver.get(self.table_link)
        time.sleep(5)
        page_html = self.driver.page_source
        soup = BeautifulSoup(page_html, 'html.parser')
        self._logger.info('Разметка табличных данных для MetalsWire')
        elems = soup.find(class_='table__container').find_all(class_='sticky-col')
        df = pd.DataFrame()
        for elem in elems:
            if elem.find('div'):
                row_data = []
                for col in elem.parent:
                    row_data.append(col.text)
                row = {
                    'Resource': row_data[0].strip(),
                    'SPOT': row_data[4],
                    '1M diff.': row_data[7],
                    'YTD diff.': row_data[8],
                    "Cons-s'23": row_data[12],
                }
                df = pd.concat([df, pd.DataFrame(row, index=[0])], ignore_index=True)
        self._logger.info('Табличные данные для MetalsWire собраны и обработаны')
        return df
