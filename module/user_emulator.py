import re
import random
import time
import json
from typing import List

import numpy as np
import selenium
import selenium.webdriver as wb
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import pandas as pd

from module import data_transformer as Transformer
import config


class ResearchError(Exception):
    """ Base class for Research exception """
    __module__ = Exception.__module__


class ResearchParser:
    """
    Class for parse pages from CIB Research
    """

    def __init__(self, driver):
        home_page = 'https://research.sberbank-cib.com'
        login = config.research_cred[0]
        password = config.research_cred[1]

        self.driver = driver
        self.home_page = home_page
        self.auth(login, password)

    @staticmethod
    def __sleep_some_time(start: float = 1.0, end: float = 2.0):
        """
        Send user emulator to sleep.
        Fake user delay and wait to load HTML elements
        :param start: Wait from...
        :param end: Wait to...
        :return: None
        """
        time.sleep(random.uniform(start, end))

    @staticmethod
    def process_bonds_exchange_text(text_rows, start, end=None) -> str:
        """
        Get necessary part of the money review.
        :param text_rows: rows of text of money review
        :param start: word to start with
        :param end: word to end with
        :return: part of text
        """

        text = '\n\n'.join(text_rows)
        pattern = rf'{start}(.*?)$' if end is None else rf'{start}(.*?)(?=\s*{end})'
        match = re.search(pattern, text, flags=re.DOTALL)
        if not match:
            raise ResearchError('Did not match in money everyday review.')

        return match.group(0)

    @staticmethod
    def process_commodity_text(text_rows: List[str]) -> str:
        """
        Get necessary part of the commodity review.
        :param text_rows: rows of text of money review
        :return: part of text
        """

        # TODO: for summarization WHILE for without summarization
        new_text_rows = []
        for row in text_rows:
            if row.isupper():
                break
            else:
                new_text_rows.append(row)

        return '\n\n'.join(new_text_rows)

    def auth(self, login, password) -> None:
        """
        Authorization in Sberbank CIB Research
        """

        self.driver.get(self.home_page)
        login_field = self.driver.find_element('xpath', "//input[@type='text']")
        password_field = self.driver.find_element('xpath', "//input[@type='password']")

        login_field.clear()
        login_field.send_keys(login)
        password_field.send_keys(password)
        password_field.send_keys(Keys.ENTER)
        # TODO: check that I go into research
        time.sleep(5)

    def find_tab(self, tab: str):
        """
        Find necessary tab by text
        :param tab: name of tab where place reviews
        :return: web element or error if element didn't find
        """

        li_elements = self.driver.find_elements('tag name', 'li')
        li_element = next((li_elem for li_elem in li_elements if li_elem.text == tab), None)

        if li_element is None:
            raise ResearchError('Did not find necessary tab')
        else:
            return li_element

    def find_reviews_by_name(self, name: str, count: int) -> List:
        """
        Find reviews elements by review's name.
        :param name: name of the review for filter
        :param count: necessary count of reviews
        :return: list of reviews' elements
        """

        # if no name for filter take top reviews
        if name == '':
            reviews_elements = self.driver.find_elements('class name', 'title.fading-container')
            # but now economy month locate in everyday tab so there is processing this
            # TODO: если ежемесячный уберут из вкладки ежедневные, то удалить строчку
            reviews_elements = [elem for elem in reviews_elements if 'Ежемесячный обзор' not in elem.text]
            return reviews_elements[:count]
        else:
            # TODO: если наладится поиск по поисковой строке, то переделать
            reviews_elements = []
            start = 0

            while len(reviews_elements) < count:
                # find review by name and add it
                elements = self.driver.find_elements('class name', 'title.fading-container')
                for element in elements[start:]:
                    if name in element.text:
                        reviews_elements.append(element)

                if len(reviews_elements) >= count:
                    break
                else:
                    # load more reviews
                    button_show_more = self.driver.find_element('id', 'loadMorePublications')
                    button_show_more.click()
                    self.__sleep_some_time(3, 6)

                start = len(elements) - 1

            return reviews_elements[:count]

    def get_date_and_text_of_review(self, element: wb.remote.webelement.WebElement, type_of_review: str) -> (str, str):
        """
        Get and clean text of the review.
        :param type_of_review: type of review which need process
        :param element: web element of the review
        :return: clear text of the review
        """

        element.find_element('tag name', 'a').click()
        self.__sleep_some_time()

        # get date
        dates = self.driver.find_elements('css selector', 'span.date')
        date = next((date.text for date in dates if date.text != ''), None)
        if date is None:
            raise ResearchError('Did not find date of the review')

        # get text
        rows = self.driver.find_elements('tag name', 'p')
        text_rows = [row.text.replace('> ', '') for row in rows if row.text.strip() != '' and '@sber' not in row.text]
        if type_of_review == 'commodity':
            text = self.process_commodity_text(text_rows)
        elif type_of_review == 'bonds':
            text = self.process_bonds_exchange_text(text_rows, start='Процентные ставки')
        elif type_of_review == 'exchange':
            text = self.process_bonds_exchange_text(text_rows, start='Валютный рынок', end='Процентные ставки')
        else:
            text = '\n\n'.join(text_rows)

        # close review page
        try:
            element.send_keys(Keys.ESCAPE)
        except selenium.common.exceptions.ElementNotInteractableException:
            self.driver.find_element('class name', 'fancybox-item.fancybox-close').click()

        return date, text

    def get_reviews(self, url_part: str, tab: str, title: str, name_of_review: str = '',
                    count_of_review: int = 1, type_of_review: str = '') -> List[tuple]:
        """
        Get data of reviews from CIB Research
        :param url_part: link for page where locate the reviews
        :param tab: name of tab where locate the reviews
        :param title: title of the page where locate the reviews
        :param name_of_review: name of review which need to parse
        :param count_of_review: count of the reviews which need to parse
        :param type_of_review: type of review for text processing
        :return: data of reviews [(title, date, text)]
        """

        # open page
        url = f'{self.home_page}/group/guest/{url_part}'
        self.driver.get(url)
        self.__sleep_some_time()
        assert title in self.driver.title

        # click on tab
        tab_element = self.find_tab(tab)
        tab_element.click()
        self.__sleep_some_time()

        # find necessary reviews
        reviews_elements = self.find_reviews_by_name(name_of_review, count_of_review)

        # get data of all reviews
        reviews_data = []
        for review_element in reviews_elements:
            title = review_element.text
            date, text = self.get_date_and_text_of_review(review_element, type_of_review)
            reviews_data.append((title, text, date))

        return reviews_data

    def get_company_html_page(self, url_part: str):
        """
        Get page about company in html format
        :param url_part: id company for search by url
        :return: page in html format
        """

        url = f'{self.home_page}/group/guest/companies?companyId={url_part}'
        self.driver.get(url)
        page_html = self.driver.page_source

        return page_html

    def get_key_econ_ind_table(self):
        """
        :return: table in dataframe format
        """
        url = f'{self.home_page}/group/guest/econ'
        self.driver.implicitly_wait(5)
        self.driver.get(url)
        page_html = self.driver.page_source
        tables = pd.read_html(page_html.replace(',', '.'))
        df = tables[-1].dropna(how='all')
        df = df.rename(columns={'Unnamed: 0': 'Name'})
        left_column = df[df.isnull().any(axis=1)]
        table_without_nan = df.dropna().reset_index(drop=True)
        counts = []
        count = 0
        for cell in df.iloc[:, 1]:
            if not np.isnan(cell):
                count += 1
            elif np.isnan(cell) and count > 0:
                counts.append(count)
                count = 0
        counts.append(count)
        alias = left_column['Name'].repeat(counts).reset_index(drop=True)
        table_without_nan['Alias'] = alias
        table_without_nan['Id'] = range(1, table_without_nan.shape[0] + 1)
        table_without_nan = table_without_nan[['Id', 'Name', '2019', '2020', '2021', '2022', '2023E', '2024E', 'Alias']]
        return table_without_nan

class InvestingAPIParser:
    """
    Class for InvestingAPI parsing
    """

    def __init__(self, driver):
        self.driver = driver

    def get_graph_investing(self, url: str):
        """
        Get plot data of investing.com api
        :param url: investing.com api url
        :return: price chart df
        """

        self.driver.get(url)
        data = self.driver.find_element(By.ID, 'json').text
        json_obj = json.loads(data)

        df = pd.DataFrame()
        for day in json_obj['data']:
            date = Transformer.Transformer.unix_to_default(day[0])
            x = day[0]
            y = day[4]
            row = {'date': date, 'x': x, 'y': y}
            df = pd.concat([df, pd.DataFrame(row, index=[0])], ignore_index=True)

        return df

    def get_streaming_chart_investing(self, url: str):
        """
        Get streaming chart data of investing.com
        :param url: rows of text of money review
        :return: price chart df
        """

        url = f'{url}-streaming-chart'
        self.driver.get(url)
        data = self.driver.find_element(By.ID, 'last_last').text

        return data


class MetalsWireParser:
    """
    Class for MetalsWire table data parsing
    """

    def __init__(self, driver):
        table_link = config.table_link
        self.driver = driver
        self.table_link = table_link

    def get_table_data(self):
        """
        Get table data of MetalsWire
        :return: commodities price chart df
        """
        self.driver.get(self.table_link)
        time.sleep(5)
        page_html = self.driver.page_source
        soup = BeautifulSoup(page_html, "html.parser")

        elems = soup.find(class_='table__container').find_all(class_='sticky-col')
        df = pd.DataFrame()
        for elem in elems:
            if elem.find('div'):
                row_data = []
                for col in elem.parent:
                    row_data.append(col.text)
                row = {'Resource': row_data[0].strip(), 'SPOT': row_data[4], '1M diff.': row_data[7],
                       'YTD diff.': row_data[8], "Cons-s'23": row_data[12]}
                df = pd.concat([df, pd.DataFrame(row, index=[0])], ignore_index=True)

        return df
