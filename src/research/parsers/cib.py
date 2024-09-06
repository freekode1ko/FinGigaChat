"""
Модуль парсинга портала CIB Research.

Парсит аналитические отчеты по отраслям и клиентам.
Парсит weekly pulse.
Парсит фин. показатели.
"""
import asyncio
import datetime
import json
import os
import random
import re
import time
from pathlib import Path

import pandas as pd
import requests
import selenium
import selenium.webdriver as wb
import sqlalchemy as sa
from aiohttp import ClientSession
from aiohttp.web_exceptions import HTTPNoContent
from bs4 import BeautifulSoup
from pdf2image import convert_from_path
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from sqlalchemy.dialects.postgresql import insert as insert_psql

from configs import config
from db import parser_source
from db.database import async_session
from db.models import FinancialSummary, ParserSource, Research, ResearchResearchType, ResearchType
from log.logger_base import Logger
from module import data_transformer, weekly_pulse_parse
from parsers.exceptions import ResearchError
from utils.selenium_utils import get_driver


class ResearchParser:
    """Класс для парсинга страниц с портала CIB Research"""

    def __init__(self, driver: WebDriver, logger: Logger.logger) -> None:
        """Инициализация парсера портала CIB Research"""
        home_page = config.research_base_url[:-1]  # 'https://research.sberbank-cib.com'
        login = config.research_cred[0]
        password = config.research_cred[1]

        self._logger = logger
        self.driver = driver
        self.home_page = home_page
        self.auth(login, password)

    def __sleep_some_time(self, start: float = 1.0, end: float = 2.0) -> None:
        """
        Send user emulator to sleep.

        Fake user delay and wait to load HTML elements

        :param start:   Wait from...
        :param end:     Wait to...
        :return:        None
        """
        sleep_time = random.uniform(start, end)
        self._logger.info(f'Уходим в ожидание на: {sleep_time}')
        time.sleep(sleep_time)

    def process_bonds_exchange_text(self, text_rows, start, end=None) -> str:
        """
        Get necessary part of the money review.

        :param text_rows:   rows of text of money review
        :param start:       word to start with
        :param end:         word to end with
        :return:            part of text
        """
        text = '\n\n'.join(text_rows)
        pattern = rf'{start}(.*?)$' if end is None else rf'{start}(.*?)(?=\s*{end})'
        match = re.search(pattern, text, flags=re.DOTALL)
        if not match:
            self._logger.warning('Не найден ежедневный финансовый отчет')
            raise ResearchError('Did not match in money everyday review.')
        return match.group(0)

    @staticmethod
    def process_commodity_text(text_rows: list[str]) -> str:
        """
        Get necessary part of the commodity review.

        :param text_rows:   rows of text of money review
        :return:            part of text
        """
        # TODO: for summarization WHILE for without summarization
        new_text_rows = []
        for row in text_rows:
            if row.isupper():
                break
            new_text_rows.append(row)

        return '\n\n'.join(new_text_rows)

    def auth(self, login, password) -> None:
        """Авторизация в CIB Research"""
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

    def find_tab(self, tab: str) -> WebElement:
        """
        Поиск необходимой вкладки по тексту

        :param tab: название вкладки, где находятся отчеты
        :return:    WebElement или ошибка, если не получилось найти элемент
        """
        self._logger.info(f'Поиск вкладки {tab}')
        li_elements = self.driver.find_elements('tag name', 'li')
        li_element = next((li_elem for li_elem in li_elements if li_elem.text == tab), None)

        if li_element is None:
            self._logger.warning(f'Вкладка {tab} не найдена')
            raise ResearchError('Did not find necessary tab')
        return li_element

    def find_reviews_by_name(self, name: str, count: int) -> list:
        """
        Find reviews elements by review's name.

        :param name:    name of the review for filter
        :param count:   necessary count of reviews
        :return:        list of reviews' elements
        """
        self._logger.info(f'Поиск отчета {name}')
        # if no name for filter take top reviews
        if name == '':
            reviews_elements = self.driver.find_elements('class name', 'title.fading-container')
            # but now economy month locate in everyday tab so there is processing this
            # TODO: если ежемесячный уберут из вкладки ежедневные, то удалить строчку
            reviews_elements = [elem for elem in reviews_elements if 'Ежемесячный обзор' not in elem.text]
            self._logger.info('Ежедневный экономический отчет найден')
            return reviews_elements[:count]

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
            # load more reviews
            self._logger.info('Загрузка большего числа отчетов')
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
        self._logger.info(f'Получаем дату и текст {type_of_review} отчета')
        element.find_element('tag name', 'a').click()
        self.__sleep_some_time()

        # get date
        try:
            dates = self.driver.find_elements('css selector', 'span.date')
        except Exception as e:
            dates = []
            self._logger.error(f'Ошибка при получении даты {type_of_review} отчета: %s', e)
        date = next((date.text for date in dates if date.text != ''), None)
        if date is None:
            self._logger.error(f'Дата {type_of_review} отчета не найдена')
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

    def get_reviews(
            self,
            url_part: str,
            tab: str,
            title: str,
            name_of_review: str = '',
            count_of_review: int = 1,
            type_of_review: str = '',
    ) -> list[tuple]:
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
            self._logger.info(f'Отчет {title} в обработке. {review_num + 1} из {reviews_elements_size}')
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

    def get_key_econ_ind_table(self) -> pd.DataFrame:
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

        self._logger.info('Ищем в html нужную таблицу')
        soup = BeautifulSoup(page_html, 'html.parser')
        table_soup = soup.find('table', attrs={'class': 'grid container black right victim'})
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
                # clear data from line space characters
                data_row.append(re.sub(r'\s+', ' ', td.text).strip())
            if data_row:
                if len(data_row) == 7:
                    data.append(data_row[1:])
                elif len(data_row) == 6:
                    data.append(data_row)

        self._logger.info('Собираем таблицу')
        df = pd.DataFrame(data, columns=headers)
        df = df[df.astype(str).ne('').all(1)].reset_index(drop=True)
        df = df.drop(index=0).reset_index(drop=True)

        table_soup_al_name = soup.find('table', attrs={'class': 'grid container black right'})
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
        cols = df.columns[idx_name - 4: idx_name + 1]
        df_new = df[cols]
        numeric_cols = []
        for col in df_new.columns:
            if re.match(r'^\d+(\.\d+)?[Ee]?$', col):
                numeric_cols.append(col)
        df_new = df[['id'] + ['name'] + numeric_cols + ['alias']].copy()

        return df_new

    def get_emulator_cookies(self, driver: WebDriver) -> requests.Session():
        """
        Sets selenium session params to requests.Session() object

        :param driver: driver to retrieve session params
        :return: session
        """
        self._logger.info('Загрузка и установка параметров драйвера для selenium')
        cookies = driver.get_cookies()
        headers = {
            header['name']: header['value']
            for header in
            driver.execute_script("return window.performance.getEntriesByType('navigation')[0].serverTiming")
            if header.get('name')
        }
        session = requests.Session()
        session.verify = False
        session.headers.update(headers)
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        return session

    def __get_industry_pdf(self, id_: str, value: str) -> None:
        """
        Get pdf for industry review

        :param id_:     id of industry in SberResearch
        :param value:   name of industry in SberResearch
        """
        pdf_dir = config.PATH_TO_SOURCES / 'reviews'
        self._logger.info(f'Скачивание отчета по индустриям с Research в {pdf_dir}')
        url = config.industry_base_url.format(id_)
        filename = None
        self.driver.get(url)
        self.__sleep_some_time(10.0, 12.0)
        self.driver.find_element(By.XPATH, '//*[@id="0--1--122--101--113--115--7--90--82--109--83"]').click()
        self.__sleep_some_time(10.0, 12.0)
        reviews_rows = self.driver.find_elements(By.XPATH, f"//div[contains(@title, '{value}')]")
        reviews_size = len(reviews_rows)
        self._logger.info(f'Обработка отчетов по индустриям ({reviews_size})')
        for review_num, review in enumerate(reviews_rows):
            self._logger.info(f'Начало обработки отчет по индустриям № {review_num + 1} из {reviews_size}')
            link = review.find_element(By.XPATH, './a[1]')
            self.driver.execute_script('arguments[0].scrollIntoView();', link)
            filename = review.get_attribute('title').replace(' ', '_')
            self._logger.info(f'Установлено название обрабатываемого отчета: {filename}')
            date = review.find_element(By.XPATH, '..').find_element(By.XPATH, '..').find_element(By.CLASS_NAME,
                                                                                                 'date').text
            self._logger.info(f'Установлена дата ({date}) для {filename}')
            filename = f'{filename}__{date}.pdf'
            filename = pdf_dir / filename
            link.click()
            self._logger.info(f'{filename} - Скачан')
            break

        if not pdf_dir.exists():
            pdf_dir.mkdir(exist_ok=True, parents=True)
        old = [f for f in os.listdir(pdf_dir) if value in f]
        if filename is not None and filename.exists():
            return
        if filename is None:
            raise ResearchError('Не удалось получить файл для отчета по индустрии')

        # time.sleep(5)
        self.__sleep_some_time(5.0, 6.0)
        download_report = self.driver.find_element(By.CLASS_NAME, 'file')
        href = download_report.get_attribute('href')

        session = self.get_emulator_cookies(self.driver)
        response = session.get(href)

        with open(filename, 'wb') as file:
            file.write(response.content)

        if len(old):
            os.remove(os.path.join(pdf_dir, old[0]))

    def get_industry_reviews(self) -> None:
        """Get all industry reviews"""
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
                self.driver.quit()
                self.driver = get_driver(self._logger)


class ResearchAPIParser:
    """Класс парсера страниц с портала CIB Research"""

    report_title_tr_pattern = re.compile(r'publication-\d+')

    def __init__(self, logger: Logger.logger) -> None:
        """Инициализация парсера страниц с портала CIB Research"""
        self._logger = logger

        login = config.research_cred[0]
        password = config.research_cred[1]
        self.auth = (login, password)

        self.REPEAT_TRIES = config.REPEAT_TRIES
        self.content_len = config.CONTENT_LENGTH__HTML_WITH_ARTICLE
        self.month_dict = config.MONTH_NAMES_DICT

        self.home_page = config.research_base_url[:-1]

        self.cookies = {
            'JSESSIONID': config.CIB_JSESSIONID,
            'LOGIN': config.CIB_LOGIN,
            'PASSWORD': config.CIB_PASSWORD,
            'ID': config.CIB_ID,
            'REMEMBER_ME': 'true',
        }
        self.update_cookies()

    @staticmethod
    def crop_image(img: Image, left: int = 70, top: int = 40, right: int = 1350, bottom: int = 1290) -> Image:
        """Обрезка картинки"""
        return img.crop((left, top, right, bottom))

    def update_cookies(self) -> None:
        """Метод для обновления JSESSIONID в куках, для того чтобы проходили все запросы"""
        self._logger.info('Начало обновления куков')
        with requests.get(
                url=f'{self.home_page}/group/guest/strat',
                params={
                    'p_p_id': 'cibstrategypublictaionportlet_WAR_cibpublicationsportlet_INSTANCE_lswn',
                    'p_p_lifecycle': '2',
                    'p_p_state': 'normal',
                    'p_p_mode': 'view',
                    'p_p_resource_id': 'getPublications',
                    'p_p_cacheability': 'cacheLevelPage',
                },
                cookies=self.cookies,
                verify=False,
        ) as req:
            if req.status_code == 200 and 'JSESSIONID' in req.cookies:
                self.cookies['JSESSIONID'] = req.cookies['JSESSIONID']
                self._logger.info('Куки успешно обновлены')
            elif req.status_code == 200:
                self._logger.info('CIB: Куки не нуждаются в обновлении')
            else:
                self._logger.error('CIB: Ошибка обновления куков')

    async def get_pages_to_parse_from_db(self) -> list[dict[str, int | str | dict | list]]:
        """
        Метод возвращает список источников, из которых необходимо взять отчеты

        return: возвращает список источников с доп параметрами
        """
        async with async_session() as session:
            all_sources = await session.execute(
                sa.select(
                    ResearchType.id.label('research_type_id'),
                    ParserSource.source.label('url'),
                    ParserSource.params,
                    ParserSource.alt_names,
                    ParserSource.before_link,
                    ParserSource.response_format.label('request_method'),
                ).select_from(ResearchType).join(ParserSource)
            )
            return [_._asdict() for _ in all_sources]

    def cib_date_to_normal_date(self, cib_date: str) -> datetime.date:
        """
        Метод приводящий из "04 мар. 24" в питоновский date

        :param cib_date: строка с датой из новости CIB
        :return:         дата в питоновском формате
        """
        year = int('20' + cib_date[-2:])
        month = self.month_dict[cib_date[3:6]]
        day = int(cib_date[:2])
        return datetime.date(year=year, month=month, day=day)

    @staticmethod
    def is_suitable_report(header: str, starts_with: list[str] | None = None) -> bool:
        """
        Метод для определения подходит ли отчет для парсинга на основе регулярок из разделов

        :param header: Заголовок отчета
        :param starts_with: Список регулярных выражений для проверки новости
        return Булевое значение говорящее о том что новость подошла или нет
        """
        if starts_with:
            return any([re.search(x, header) for x in starts_with])
        return True

    async def report_exist_in_db(self, report_id: str, research_type_id: int) -> bool:
        """
        Проверка о том загружен ли отчет в БД или нет

        :param report_id: уникальный айди отчета
        :param research_type_id: айди тип отчета
        :return: булевое значение с ифнормацией о том есть отчет или нет
        """
        async with async_session() as session:
            report_for_report_type = (
                sa.select(Research.id)
                .select_from(ResearchType)
                .join(ResearchType.researches)
                .filter(ResearchType.id == research_type_id, Research.report_id == report_id,)
            )
            reports = await session.execute(report_for_report_type)
            reports = reports.all()

            return bool(len(reports))

    async def save_report_to_db(self, report: dict) -> None:
        """
        Метод для сохранения отчетов в базу данных

        :param report: Отчет
        """
        async with async_session() as session:
            research_type = await session.get(ResearchType, report['research_type_id'])
            session.add(research_type)
            stmt = sa.select(Research).filter_by(report_id=report['report_id'])
            research = await session.execute(stmt)
            research = research.scalar_one_or_none()

            if research is None:
                research = Research(
                    filepath=str(report['filepath']),
                    header=report['header'].replace("'", "''"),
                    text=report['text'].replace("'", "''"),
                    parse_datetime=report['parse_datetime'],
                    publication_date=report['publication_date'],
                    report_id=report['report_id'],
                )
                session.add(research)
                await session.commit()

            session.add(
                ResearchResearchType(
                    research_id=research.id,
                    research_type_id=research_type.id
                )
            )
            await session.commit()

    async def parse_reports_by_id(
            self,
            report_id: str,
            session: ClientSession,
            params: dict[str, int | str | dict | None],
            save_report: bool = True,
    ) -> dict[str, int | str | datetime.datetime | datetime.date | Path | None]:
        """
        Метод для выгрузки новости по айди из разделов

        :param report_id: айди отчета
        :param session: сессия aiohttp
        :param params: словарь с параметрами страницы
        :param save_report: сохранять ли полученный отчет в БД
        :returns: dict[research_type_id, filepath, header, text, parse_datetime,publication_date,report_id]
        """
        self._logger.info('CIB: задача для получения отчета начата: %s', report_id)

        async with session.get(
                url=config.ARTICLE_URL,
                params={'publicationId': report_id},
                cookies=self.cookies,
                verify_ssl=False,
        ) as req:
            report_html = BeautifulSoup(await req.text(), 'html.parser')

        header = str(report_html.find('h1', class_='popupTitle').text).strip()

        self._logger.info('CIB: сохранение отчета: %s', report_id)

        date = self.cib_date_to_normal_date(str(report_html.find('span',
                                                                 class_='date').text).strip())
        report_texts = []
        for paragraph_tag in report_html.find('div', class_='summaryContent').find_all('p'):
            # Удаляем все ссылки
            if paragraph_tag.find('a'):
                continue
            # Удаление пустых paragraph
            if text := str(paragraph_tag.text).strip():
                report_texts.append(text)
        report_text = '\n\n'.join(report_texts).replace('>', '-')

        if file_element_with_href := report_html.find('a', class_='file', href=True):
            async with session.get(
                    url=file_element_with_href['href'].strip(),
                    cookies=self.cookies,
                    verify_ssl=False,
            ) as req:
                if req.status == 200:

                    file_path = config.PATH_TO_REPORTS / f'{report_id}.pdf'
                    with open(file_path, 'wb') as f:
                        while True:
                            chunk = await req.content.readany()
                            if not chunk:
                                break
                            f.write(chunk)
            self._logger.info('CIB: успешное сохранение файла: %s', report_id)
        else:
            file_path = None

        data = {
            'research_type_id': params['research_type_id'],
            'filepath': file_path,
            'header': header,
            'text': report_text,
            'parse_datetime': datetime.datetime.utcnow(),
            'publication_date': date,
            'report_id': report_id,
        }
        if save_report:
            await self.save_report_to_db(data)
        return data

    async def get_report_ids_from_page(
            self,
            params: dict[str, int | str | list | dict | None],
            session: ClientSession,
            check_existing: bool = True,
            **kwargs,
    ) -> list[dict[str, int | str | datetime.datetime | datetime.date | Path | None]]:
        """
        Метод для получений айди новостей из разделов

        :param params: Параметры для выгрузки отчетов
        :param session: сессия aiohttp
        :param check_existing: Делать ли проверку на то, что report_id есть в БД
        :returns: list[dict[research_type_id, filepath, header, text, parse_datetime,publication_date,report_id]]
        """
        self._logger.info('CIB: Начат парсинг страницы %s', params['url'])
        for i in range(self.REPEAT_TRIES):
            if params['before_link']:
                # Тут нужно запрашивать отчеты по порядку
                try:
                    requests.get(url=params['before_link'], cookies=self.cookies, verify=False, timeout=10)
                    req = requests.request(
                        method=params['request_method'],
                        url=params['url'],
                        params=params['params'],
                        cookies=self.cookies,
                        verify=False,
                        timeout=10,
                    )
                except Exception as e:
                    self._logger.error(f'Во время запроса отчетов со страницы {params["url"]} произошла ошибка: %s', e)
                    continue
                status_code = req.status_code
                content = req.content
            else:
                try:
                    req = await session.post(
                        url=params['url'],
                        params=params['params'],
                        cookies=self.cookies,
                        ssl=False,
                        timeout=10
                    )
                    content = await req.text()
                    status_code = req.status
                except Exception as e:
                    self._logger.error(f'Во время запроса отчетов со страницы {params["url"]} произошла ошибка: %s', e)
                    continue
            if status_code == 200 and len(content) > self.content_len:
                break
        else:
            self._logger.error('CIB: не получилось запросить отчеты со страницы: %s', params['url'])
            raise HTTPNoContent

        # loop = asyncio.get_event_loop()
        html_parser = BeautifulSoup(content, 'html.parser')

        reports_ids = html_parser.find_all('div', class_='hidden publication-id')
        reports_titles = html_parser.find_all('tr', class_=self.report_title_tr_pattern)

        self._logger.info('CIB: получен успешный ответ со страницы c id: %s ;url: %s. И найдено %s отчетов', str(params['research_type_id']), params['url'], len(reports_ids))

        new_reports = []
        for report_id, report_name in zip(reports_ids, reports_titles):
            report_name = str(report_name.find_next('div', class_='title').text).strip()
            if not self.is_suitable_report(report_name, params['alt_names']):
                continue

            element_with_id = str(report_id.text)
            if not element_with_id:
                continue

            if not check_existing or not await self.report_exist_in_db(element_with_id, params['research_type_id']):
                self._logger.info('CIB: создание задачи для получения отчета: %s', str(element_with_id))
                data = await self.parse_reports_by_id(element_with_id, session, params, **kwargs)
                self._logger.info('CIB: задача для получения отчета завершена: %s', str(element_with_id))
                new_reports.append(data)
        return new_reports

    async def parse_weekly_pulse(self, session) -> None:
        """
        Получение отчета Weekly Pulse

        :param session: сессия aiohttp
        """
        self._logger.info('Сборка Weekly Pulse')
        page = await parser_source.get_research_type_source_by_name(source_name='Weekly Pulse')

        self._logger.info('Поиск Weekly Pulse отчета')
        try:
            report_data = await self.get_report_ids_from_page(page, session, check_existing=False, save_report=False)
        except HTTPNoContent as e:
            self._logger.error('CIB: Ошибка при соединении c CIB: %s', e)
            return
        except Exception as e:
            self._logger.error('CIB: Ошибка при работе с CIB: %s', e)
            return

        if not report_data or not report_data[0]['filepath']:
            self._logger.info('CIB: Не удалось получить отчет Weekly Pulse')
            return
        report_data = report_data[0]

        weekly_dir = config.PATH_TO_SOURCES / 'weeklies'

        filename = f"{report_data['header'].replace(' ', '_')}.pdf"
        filename = weekly_dir / filename
        self._logger.info('Проверка путей до Weekly Pulse')

        if not weekly_dir.exists():
            weekly_dir.mkdir(parents=True, exist_ok=True)

        if filename.exists():
            self._logger.info('Weekly Pulse отчет собран')
            print('Weekly Pulse отчет собран')
            return

        old = [f for f in os.listdir(weekly_dir) if 'Research' in f]
        if len(old) > 0:
            os.remove(os.path.join(weekly_dir, old[0]))

        # Перемещаем скачанный файл в папку с данными по викли пульсу
        report_data['filepath'].replace(filename)

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
                width, height = img.size
                useful_height = height * weekly_pulse_parse.PERCENT_HEIGHT_OF_USEFUL_INFO // 100
                img = self.crop_image(img, 0, 0, width, useful_height)
                if slide_meta['crop']:
                    img = self.crop_image(img, **slide_meta['crop_params'])

                for sub_img_params in slide_meta['sub_images']:
                    crop_params = sub_img_params['crop_params'].copy()
                    if sub_img_params['relative']:
                        width, height = img.size

                        crop_params = {
                            'left': int(width * sub_img_params['crop_params']['left']),
                            'top': int(height * sub_img_params['crop_params']['top']),
                            'right': int(width * sub_img_params['crop_params']['right']),
                            'bottom': int(height * sub_img_params['crop_params']['bottom']),
                        }
                    sub_img = self.crop_image(img, **crop_params)
                    sub_img.save(f"{weekly_dir}/{sub_img_params['name']}.png")

                img.save(f"{weekly_dir}/{slide_meta['eng_name']}.png")

        parser_source.update_get_datetime(source_name='Weekly Pulse')
        self._logger.info('Weekly review готов')
        print('Weekly review готов')

    async def parse_pages(self) -> None:
        """Стартовая точка, метод который запускает весь парсинг отчетов"""
        self._logger.info('CIB: Начало парсинга CIB')

        pages_list = await self.get_pages_to_parse_from_db()

        loop = asyncio.get_event_loop()
        async with ClientSession() as session:
            for page in pages_list:
                try:
                    await loop.create_task(
                        self.get_report_ids_from_page(page, session),
                    )
                except HTTPNoContent as e:
                    self._logger.error('CIB: Ошибка при соединении c CIB: %s', e)
                except Exception as e:
                    self._logger.error('CIB: Ошибка при работе с CIB: %s', e)

            # weekly pulse
            await loop.create_task(self.parse_weekly_pulse(session))

        self._logger.info('CIB: Конец парсинга CIB')

    @staticmethod
    async def save_fin_summary(df: pd.DataFrame) -> None:
        """
        Сохранение финансовых показателей по клиентам в БД

        :param df: pandas.DataFrame() с таблицей для записи в бд
        """
        async with async_session() as session:
            stmt = insert_psql(FinancialSummary).values(df.to_dict('records'))
            stmt = stmt.on_conflict_do_update(
                index_elements=[FinancialSummary.sector_id, FinancialSummary.company_id, FinancialSummary.client_id],
                set_={
                    'review_table': stmt.excluded.review_table,
                    'pl_table': stmt.excluded.pl_table,
                    'balance_table': stmt.excluded.balance_table,
                    'money_table': stmt.excluded.money_table,
                },
            )
            await session.execute(stmt)
            await session.commit()

    async def get_fin_summary(self) -> None:
        """Стартовая точка для парсинга финансовых показателей по клиентам"""
        self._logger.info('Чтение таблицы financial_summary')
        query = sa.select(FinancialSummary.sector_id, FinancialSummary.company_id,
                          FinancialSummary.client_id, FinancialSummary.review_table, FinancialSummary.pl_table,
                          FinancialSummary.balance_table, FinancialSummary.money_table)
        async with async_session() as session:
            metadata = await session.execute(query)
            metadata = metadata.fetchall()
        metadata_df = pd.DataFrame(metadata)
        metadata_df.columns = metadata_df.keys()

        self._logger.info('Очистка прошлых записей в таблице financial_summary')

        sectors_id = metadata_df.drop_duplicates(subset=['sector_id'])['sector_id'].tolist()
        metadata_df[['review_table', 'pl_table', 'balance_table', 'money_table']] = None
        tf = data_transformer.Transformer(self._logger)
        df_parts = pd.DataFrame(columns=metadata_df.columns)

        async with ClientSession() as session:
            for sector_id in sectors_id:
                self._logger.info(f'Обработка сектора {sector_id} для поиска фин. показателей')
                # выберем блок из DF по обрабатываемому сектору
                sector_df = metadata_df.loc[metadata_df['sector_id'] == sector_id]
                for company_id in sector_df['company_id'].values.tolist():
                    url = f'{self.home_page}/group/guest/companies?companyId={company_id}'
                    try:
                        for i in range(config.POST_TO_SERVICE_ATTEMPTS):
                            sector_page = await session.post(url=url, verify_ssl=False, cookies=self.cookies)
                            if sector_page.ok:
                                break
                            else:
                                time.sleep(1)

                        content = await sector_page.text()
                        part = tf.process_fin_summary_table(content, company_id, sector_df)
                        df_parts = pd.concat([part, df_parts], ignore_index=True)
                        parser_source.update_get_datetime_by_source(source=url)
                    except HTTPNoContent as e:
                        self._logger.error('CIB: Ошибка при соединении c CIB: %s', e)
                    except Exception as e:
                        self._logger.error('CIB: Ошибка при работе с CIB: %s', e)
                self._logger.info(f'Сектор {sector_id} с фин. показателями обработан')

        self._logger.info('Запись таблицы financial_summary')
        df_parts.dropna(subset=['review_table', 'pl_table', 'balance_table', 'money_table'], inplace=True)
        df_parts.drop_duplicates(subset=['company_id', 'client_id'], inplace=True)
        df_parts.sort_values(by=['sector_id', 'company_id'], ascending=[True, True]).reset_index(drop=True,
                                                                                                 inplace=True)
        df_parts['review_table'] = df_parts['review_table'].apply(json.dumps)
        df_parts['pl_table'] = df_parts['pl_table'].apply(json.dumps)
        df_parts['balance_table'] = df_parts['balance_table'].apply(json.dumps)
        df_parts['money_table'] = df_parts['money_table'].apply(json.dumps)
        # df_parts.to_sql('financial_summary', if_exists='replace', index=False, con=engine)
        await self.save_fin_summary(df_parts)
        self._logger.info('Таблица financial_indicators записана')
