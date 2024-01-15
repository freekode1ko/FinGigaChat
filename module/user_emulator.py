from PIL import Image
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from module import data_transformer as Transformer
from module import weekly_pulse_parse
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from pdf2image import convert_from_path
from module.logger_base import Logger
import selenium.webdriver as wb
from bs4 import BeautifulSoup
from typing import List
import pandas as pd

import selenium
import requests
import random
import config
import copy
import json
import time
import re
import os


class ResearchError(Exception):
    """ Base class for Research exception """
    __module__ = Exception.__module__


class ResearchParser:
    """
    Class for parse pages from CIB Research
    """

    def __init__(self, driver, logger: Logger.logger):
        home_page = config.research_base_url[:-1]  # 'https://research.sberbank-cib.com'
        login = config.research_cred[0]
        password = config.research_cred[1]

        self._logger = logger
        self.driver = driver
        self.home_page = home_page
        self.auth(login, password)

    def __sleep_some_time(self, start: float = 1.0, end: float = 2.0):
        """
        Send user emulator to sleep.
        Fake user delay and wait to load HTML elements
        :param start: Wait from...
        :param end: Wait to...
        :return: None
        """
        sleep_time = random.uniform(start, end)
        self._logger.info(f'Уходим в ожидание на: {sleep_time}')
        time.sleep(sleep_time)

    def process_bonds_exchange_text(self, text_rows, start, end=None) -> str:
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
            self._logger.warning('Не найден ежедневный финансовый отчет')
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
        self._logger.info('Авторизация на Sberbank CIB Research')
        self.driver.get(self.home_page)
        login_field = self.driver.find_element('xpath', "//input[@type='text']")
        password_field = self.driver.find_element('xpath', "//input[@type='password']")

        login_field.clear()
        login_field.send_keys(login)
        password_field.send_keys(password)
        password_field.send_keys(Keys.ENTER)
        # TODO: check that I go into research
        self.__sleep_some_time(5.0, 6.0)
        # time.sleep(5)

    def find_tab(self, tab: str):
        """
        Find necessary tab by text
        :param tab: name of tab where place reviews
        :return: web element or error if element didn't find
        """
        self._logger.info(f'Поиск вкладки {tab}')
        li_elements = self.driver.find_elements('tag name', 'li')
        li_element = next((li_elem for li_elem in li_elements if li_elem.text == tab), None)

        if li_element is None:
            self._logger.warning(f'Вкладка {tab} не найдена')
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
        self._logger.info(f'Поиск отчета {name}')
        # if no name for filter take top reviews
        if name == '':
            reviews_elements = self.driver.find_elements('class name', 'title.fading-container')
            # but now economy month locate in everyday tab so there is processing this
            # TODO: если ежемесячный уберут из вкладки ежедневные, то удалить строчку
            reviews_elements = [elem for elem in reviews_elements if 'Ежемесячный обзор' not in elem.text]
            self._logger.info(f'Ежедневный экономический отчет найден')
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
                    self._logger.info(f'Загрузка больше отчетов')
                    button_show_more = self.driver.find_element('id', 'loadMorePublications')
                    button_show_more.click()
                    self.__sleep_some_time(3, 6)

                start = len(elements) - 1
            self._logger.info(f'Отчет {name} найден')
            return reviews_elements[:count]

    def get_date_and_text_of_review(self, element: wb.remote.webelement.WebElement, type_of_review: str) -> (str, str):
        """
        Get and clean text of the review.
        :param type_of_review: type of review which need process
        :param element: web element of the review
        :return: clear text of the review
        """
        self._logger.info('Получаем дату и текст отчета')
        element.find_element('tag name', 'a').click()
        self.__sleep_some_time()

        # get date
        dates = self.driver.find_elements('css selector', 'span.date')
        date = next((date.text for date in dates if date.text != ''), None)
        if date is None:
            self._logger.error('Дата отчета не найдена')
            raise ResearchError('Did not find date of the review')

        # get text
        self._logger.info('Получаем текст отчета и очищаем его')
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
            self._logger.error('Проблема в работе selenium. Не удалось закрыть окно.')
            self.driver.find_element('class name', 'fancybox-item.fancybox-close').click()
        self._logger.info('Получили дату и текст отчета')
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
        self._logger.info(f'Открываем страницу {url}')
        self.driver.get(url)
        self.__sleep_some_time()
        assert title in self.driver.title

        # click on tab
        self._logger.info(f'Открываем вкладку {tab}')
        tab_element = self.find_tab(tab)
        tab_element.click()
        self.__sleep_some_time()

        # find necessary reviews
        self._logger.info(f'Ищем отчет {name_of_review}')
        reviews_elements = self.find_reviews_by_name(name_of_review, count_of_review)

        # get data of all reviews
        reviews_data = []
        reviews_elements_size = len(reviews_elements)
        self._logger.info(f'Собираем содержимое для всех отчетов. Всего в обработке {reviews_elements_size} отчетов')
        for review_num, review_element in enumerate(reviews_elements):
            title = review_element.text
            self._logger.info(f'Отчет {title} в обработке. {review_num+1} из {reviews_elements_size}')
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
        self._logger.info(f'Открываем страницу компании: {url}')
        self.driver.get(url)
        page_html = self.driver.page_source

        return page_html

    def get_key_econ_ind_table(self):
        """
        Get page about company in html format
        :return: table in DataFrame format
        """

        url = f'{self.home_page}/group/guest/econ'
        self._logger.info(f'Открываем страницу о ключевых показателях компании: {url}')
        self.driver.implicitly_wait(5)
        self.driver.get(url)
        self.__sleep_some_time(60.0, 65.0)
        # time.sleep(60)

        page_html = self.driver.page_source

        self._logger.info(f'Ищем в html нужную таблицу')
        soup = BeautifulSoup(page_html, "html.parser")
        table_soup = soup.find('table', attrs={'class': "grid container black right victim"})
        headers = []
        head = table_soup.find('thead').find('tr')
        for td in head:
            col_name = td.text.strip()
            if col_name != '':
                headers.append(col_name)

        data = []
        for tr in table_soup.find_all('tr'):
            data_row = []
            for td in tr.find_all('td'):
                data_row.append(td.text.strip())
            if data_row:
                if len(data_row) == 7:
                    data.append(data_row[1:])
                elif len(data_row) == 6:
                    data.append(data_row)

        self._logger.info('Собираем таблицу')
        df = pd.DataFrame(data, columns=headers)
        df = df[df.astype(str).ne('').all(1)].reset_index(drop=True)
        df = df.drop(index=0).reset_index(drop=True)

        table_soup_al_name = soup.find('table', attrs={'class': "grid container black right"})
        aliases = []
        names = []
        aliases_longevity = []

        for elem in table_soup_al_name:
            col_text = elem.find('td').text.strip()
            if col_text != '':
                if 'name' in elem.find('td').get('class') and 'Норма' not in col_text:
                    names.append(col_text)
                    aliases_longevity.append(1)
                else:
                    aliases.append(col_text)
                    aliases_longevity.append(0)

        df['name'] = names

        counts = []
        counter = 0

        for val in aliases_longevity:
            if val == 0:
                counts.append(counter)
                counter = 0
            else:
                counter += 1

        counts.append(counter)
        del counts[0]

        aliases_series = pd.Series(aliases)
        aliases_series = aliases_series.repeat(counts).reset_index(drop=True)

        df['id'] = range(1, df.shape[0] + 1)
        df['alias'] = aliases_series
        idx_name = list(df.columns).index('name')
        cols = df.columns[idx_name - 4:idx_name + 1]
        df_new = df[cols]
        numeric_cols = []
        for col in df_new.columns:
            if re.match('^\d+(\.\d+)?[Ee]?$', col):
                numeric_cols.append(col)
        df_new = df[['id'] + ['name'] + numeric_cols + ['alias']].copy()

        return df_new

    def __get_client_fin_indicators(self, page_html, company):
        """
        Get singe company financial indicators table
        :param page_html: html page of company
        :param company: company name
        :return: table in DataFrame format
        """
        self._logger.info(f'Получение таблицы финансовых показателей для компании: {company}')
        soup = BeautifulSoup(page_html, "html.parser")
        table_soup = soup.find('div', attrs={'class': "report company-summary-financials"}). \
            find('div', attrs={'class': 'grid_container grid-bottom-border'}). \
            find('div', attrs={'class': 'table-scroll'}). \
            find('table', attrs={'class': 'grid container black right'})

        self._logger.info(f'Обработка найденной таблицы для компании {company}')
        tables = pd.read_html(str(table_soup), thousands='', decimal=',')
        df = tables[0]
        df['Unnamed: 0'].fillna(method='ffill', inplace=True)
        df['alias'] = df['Unnamed: 0'].ffill(limit=1).fillna('')
        df.drop('Unnamed: 0', axis=1, inplace=True)
        df = df.dropna(how='all', subset=df.columns.difference(['alias']))
        df.iloc[:, 1:] = df.iloc[:, 1:].apply(lambda x: x.str.replace('\xa0', ''))
        df.iloc[:, 1:] = df.iloc[:, 1:].apply(lambda x: x.str.replace(',', '.'))
        df = df.rename(columns={'Unnamed: 1': 'name'})

        self._logger.info(f'Выборка нужных значений из собранной таблицы для {company}')
        cols_to_convert = df.columns[~df.columns.isin(['alias', 'name'])]
        mask = ~df.apply(lambda x: 'IFRS' in x.values, axis=1)
        df.loc[mask, cols_to_convert] = df.loc[mask, cols_to_convert].apply(pd.to_numeric, errors='coerce')

        numeric_cols = df.columns[df.columns.str.match(r'^\d{4}')].tolist()[:5]
        df_new = df.loc[:, numeric_cols]
        df_new = df[['name'] + numeric_cols + ['alias']].copy()
        df_new['company'] = company.lower()
        return df_new

    def get_companies_financial_indicators_table(self):
        """
        Get financial indicators' table for all companies
        :return: table in dataframe format
        """
        self._logger.info('Получение таблиц с фин.показателями для всех компаний')
        companies = copy.deepcopy(config.dict_of_companies)
        companies_research_link = f'{config.research_base_url}group/guest/companies?companyId=id_id'

        fin_indicators_tables = {}
        for company in companies:

            link = copy.deepcopy(companies_research_link)
            link = link.replace('id_id', companies[company]['company_id'])
            self.__sleep_some_time(3.0, 4.0)
            # time.sleep(3)
            self.driver.get(link)

            page_html = self.driver.page_source
            fin_indicators_table = self.__get_client_fin_indicators(page_html, company)
            fin_indicators_tables[company] = fin_indicators_table
            self._logger.info(f'Таблица для {company} - получена')

        self._logger.info('Предварительная обработка таблиц')
        result = pd.concat(list(fin_indicators_tables.values()))
        result['id'] = range(1, result.shape[0] + 1)
        result = result.replace('Рентабельность', 'Рентабельность, %')
        result = result.replace('Рост', 'Рост, %')
        result = result.replace('EPS (скорр.), R', 'EPS (скорр.), руб.')
        result = result.replace('Финансовые показатели, R млн.', 'Финансовые показатели, млн руб.')
        result = result.replace('Операционные показатели, R млн.', 'Операционные показатели, млн руб.')
        result = result.replace('BVPS, R', 'BVPS, руб.')
        result = result.replace('EPS (прибыль на акцию), R', 'EPS (прибыль на акцию), руб.')

        return result

    def get_emulator_cookies(self, driver) -> requests.Session():
        """
        Sets selenium session params to requests.Session() object
        :param driver: driver to retrieve session params
        :return session:
        """
        self._logger.info('Загрузка и установка параметров драйвера для selenium')
        cookies = driver.get_cookies()
        headers = {header["name"]: header["value"] for header in
                   driver.execute_script("return window.performance.getEntriesByType('navigation')[0].serverTiming") if
                   header.get("name")}
        session = requests.Session()
        session.verify = False
        session.headers.update(headers)
        for cookie in cookies:
            session.cookies.set(cookie["name"], cookie["value"])
        return session

    def __get_industry_pdf(self, id, value):
        """
        Get pdf for industry review
        :param id: id of industry in SberResearch
        :param value: name of industry in SberResearch
        """
        pdf_dir = f'{config.path_to_source}/reviews'
        self._logger.info(f'Скачивание отчета по индустриям с Research в {pdf_dir}')
        url = config.industry_base_url.format(id)
        filename = None
        date = None
        old = []
        self.driver.get(url)
        self.__sleep_some_time(10.0, 12.0)
        reviews = self.driver.find_element(By.XPATH, '//*[@id="0--1--122--101--113--115--7--90--82--109--83"]').click()
        self.__sleep_some_time(10.0, 12.0)
        reviews_rows = self.driver.find_elements(By.XPATH, f"//div[contains(@title, '{value}')]")
        reviews_size = len(reviews_rows)
        self._logger.info(f'Обработка отчетов по индустриям ({reviews_size})')
        for review_num, review in enumerate(reviews_rows):
            self._logger.info(f'Начало обработки отчет по индустриям № {review_num+1} из {reviews_size}')
            link = review.find_element(By.XPATH, "./a[1]")
            self.driver.execute_script("arguments[0].scrollIntoView();", link)
            filename = review.get_attribute('title').replace(' ', '_')
            self._logger.info(f'Установлено название обрабатываемого отчета: {filename}')
            date = review.find_element(By.XPATH, '..'). \
                find_element(By.XPATH, '..'). \
                find_element(By.CLASS_NAME, 'date').text
            self._logger.info(f'Установлена дата ({date}) для {filename}')
            filename = f'{filename}__{date}.pdf'
            filename = '{}/{}'.format(pdf_dir, filename)
            link.click()
            self._logger.info(f'{filename} - Скачан')
            break

        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)
        old = [f for f in os.listdir(pdf_dir) if value in f]
        if os.path.exists(filename):
            return

        # time.sleep(5)
        self.__sleep_some_time(5.0, 6.0)
        download_report = self.driver.find_element(By.CLASS_NAME, "file")
        href = download_report.get_attribute("href")

        session = self.get_emulator_cookies(self.driver)
        response = session.get(href)

        with open(filename, 'wb') as file:
            file.write(response.content)

        if old.__len__() > 0:
            os.remove(os.path.join(pdf_dir, old[0]))

    def get_industry_reviews(self):
        """
        Get all industry reviews
        """
        self._logger.info('Сборка отчетов по индустриям (отрасли)')
        print('Сборка отчетов по индустриям (отрасли)')
        industry_reviews = config.industry_reviews
        for industry in industry_reviews:
            try:
                self._logger.info(f'Получение отчета по {industry}')
                self.__get_industry_pdf(industry, industry_reviews[industry])
                self._logger.info(f'Отчет по {industry} получен')
                print(f'{industry_reviews[industry]}..ОК')
            except Exception as e:
                self._logger.error(f'{industry_reviews[industry]} Ошибка ({e}) при получении')
                print(f'{industry_reviews[industry]} Ошибка ({e}) при получении')

    @staticmethod
    def crop_image(img: Image, left: int = 70, top: int = 40, right: int = 1350, bottom: int = 1290) -> Image:
        return img.crop((left, top, right, bottom))

    def get_weekly_review(self):
        """
        Get Research Weekly Pulse review pdf
        """
        self._logger.info('Сборка Weekly Pulse')
        base_url = '{}{}'.format(config.research_base_url, 'group/guest/money')
        self.driver.get(base_url)
        self._logger.info('Ожидаем появления на загружаемой странице объектов для перехода на все отчеты')
        WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="all"]')) and
                                             EC.invisibility_of_element_located((By.ID, "all_loading")))
        self.driver.find_element(By.XPATH, '//*[@id="all"]').click()
        self._logger.info('Поиск Weekly Pulse отчета')
        weekly_dir = '{}/{}'.format(config.path_to_source, 'weeklies')
        weeklies = self.driver.find_elements(By.XPATH, f"//div[contains(@title, 'Weekly Pulse')]")

        try:
            self._logger.info('Начало обработки "Weekly Pulse" отчета')
            while len(weeklies) < 1:
                self._logger.info('Ожидание доступности отчета для открытия')
                WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="loadMorePublications"]'))
                    and EC.invisibility_of_element_located((By.ID, "loadMorePublications_loading")))
                self._logger.info('Загрузка большего количества публикаций для поиска там отчета')
                more = self.driver.find_element(By.XPATH, '//*[@id="loadMorePublications"]')
                self.driver.execute_script("arguments[0].scrollIntoView();", more)
                self._logger.info('Загрузка следующих публикаций')
                more.click()
                self._logger.info('Ожидание доступности дополнительных отчетов для открытия')
                WebDriverWait(self.driver, 30).until(EC.element_to_be_selected(
                    (By.XPATH, "//div[contains(@title, 'Weekly Pulse')]")))
                weeklies = self.driver.find_elements(By.XPATH, f"//div[contains(@title, 'Weekly Pulse')]")
                self.__sleep_some_time()
        except Exception as e:
            self._logger.error(f'Ошибка ({e}) в загрузке Weekly Pulse')
            print(f'Ошибка ({e}) в загрузке Weekly Pulse')
            return

        weeklies[0].find_element(By.TAG_NAME, 'a').click()

        filename = f"{weeklies[0].text.replace(' ', '_')}.pdf"
        filename = '{}/{}'.format(weekly_dir, filename)
        self._logger.info('Проверка путей до Weekly Pulse')

        if not os.path.exists(weekly_dir):
            os.makedirs(weekly_dir)

        if os.path.exists(filename):
            self._logger.info('Weekly Pulse отчет собран')
            print('Weekly Pulse отчет собран')
            return
        else:
            old = [f for f in os.listdir(weekly_dir) if 'Research' in f]
            if len(old) > 0:
                os.remove(os.path.join(weekly_dir, old[0]))

        self.__sleep_some_time(5.0, 6.0)
        download_report = self.driver.find_element(By.CLASS_NAME, "file")
        href = download_report.get_attribute("href")

        session = self.get_emulator_cookies(self.driver)
        response = session.get(href)

        with open(filename, 'wb') as file:
            file.write(response.content)

        self._logger.info('Сохранение ключевых слайдов с weekly review')
        images = convert_from_path(filename)
        # PARSE PDF TO GET SPECIAL SLIDES
        weekly_pulse_parser = weekly_pulse_parse.ParsePresentationPDF()
        slides_meta = weekly_pulse_parser.get_slides_meta()
        slides = weekly_pulse_parser.parse(filename)

        for slide_meta in slides_meta:
            slide_info = slides[slide_meta['title']]
            if slide_info['page_number'] < 0:
                continue

            with images[slide_info['page_number']] as img:
                if slide_meta['crop']:
                    img = self.crop_image(img)
                img.save(f"{weekly_dir}/{slide_meta['eng_name']}.png")

        self._logger.info('Weekly review готов')
        print('Weekly review готов')


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
        data = self.driver.find_element(By.ID, 'last_last').text.replace(',', '.')

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
        soup = BeautifulSoup(page_html, "html.parser")
        self._logger.info('Разметка табличных данных для MetalsWire')
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
        self._logger.info('Табличные данные для MetalsWire собраны и обработаны')
        return df
