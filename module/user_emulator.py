""" NEW VERSION OF PARSING CIB RESEARCH """

import selenium
import selenium.webdriver as wb
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import re
import config
import random
import time


class ResearchError(Exception):
    """ Base class for Research exception """
    __module__ = Exception.__module__


class ResearchParser:
    """
    Class for parse pages from CIB Research
    """

    def __init__(self):
        home_page = 'https://research.sberbank-cib.com'
        login = config.research_cred[0]
        password = config.research_cred[1]

        firefox_options = wb.FirefoxOptions()
        self.driver = wb.Remote(command_executor='http://localhost:4444/wd/hub', options=firefox_options)

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
    def process_commodity_text(text_rows: list[str]) -> str:
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

    def close_driver(self) -> None:
        self.driver.close()

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
        time.sleep(3)

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

    def find_reviews_by_name(self, name: str, count: int) -> list:
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
                    count_of_review: int = 1, type_of_review: str = '') -> list[tuple]:
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
            reviews_data.append((title, date, text))

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


'''
    OLD VERSION 
import selenium
import selenium.webdriver as wb
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import config
import random
import time


class ResearchParser:
    def __init__(self):
        cred = config.research_cred
        research_base_url = config.research_base_url
        tabs_eco = {'all': 'all', 'everyday': '905--910--900', 'reviews': '3--0--5--106--15--63--81--87'}
        tabs_money = {'all': 'all', 'everyday': '93', 'reviews': '0--113--123--110--91--82--101--100'}
        tabs_metal = {'all': 'all', 'everyday': '96--905--900', 'reviews': '134--0--137'}
        base_popup_xpath = '/html/body/div[2]/div/div/div/div/div/div/div[3]'

        self.base_popup_xpath = base_popup_xpath
        self.research_base_url = research_base_url
        self.tabs_eco = tabs_eco
        self.tabs_money = tabs_money
        self.tabs_metal = tabs_metal
        self.cred = cred

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

    def __popup_worker_eco(self, table: wb.remote.webelement.WebElement,
                           driver: wb.firefox.webdriver.WebDriver) -> list:
        """
        Get review text from popup menu after a click
        :param table: HTML element to click
        :param driver: Browser session where to work
        :return: list with text from HTML element, first and last <P> tag from review text and date of publicity
        """
        try:
            table.find_elements('tag name', 'a')[0].click()
        except IndexError:
            table.click()
        self.__sleep_some_time(2, 3)
        review_page = driver.find_element(By.XPATH, self.base_popup_xpath)
        rows = review_page.find_elements('tag name', 'p')
        review = ''
        for row in rows:
            review += '\n\n' + row.text
        try:
            review_page.send_keys(Keys.ESCAPE)
        except selenium.common.exceptions.ElementNotInteractableException:
            review_page = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/a')
            review_page.click()
        return [table.text, review]

    def __popup_worker_eco_month(self, driver: wb.firefox.webdriver.WebDriver, url: str,
                         review_filter: str = 'Экономика России. Ежемесячный обзор'):
        """
        Get review from global every month money review
        :param driver: Browser session where to work
        :param review_filter: Find specific review
        :param url: URL with reviews
        :return: list with review info
        """
        review = []
        driver.get(url)
        assert 'Экономика' in driver.title
        self.__sleep_some_time(1.5, 2.5)
        driver.find_element('id', self.tabs_eco['all']).click()
        self.__sleep_some_time(2, 3)

        search = driver.find_element('id', '_cibeconomicspublicationsportlet_WAR_cibpublicationsportlet_'
                                           'INSTANCE_btxt3yIWPKYW_publication-search-input')
        search.click()
        search.send_keys(review_filter, Keys.ENTER)
        self.__sleep_some_time(2.5, 3.2)
        try:
            table = driver.find_element(By.XPATH, '//*[@id="publicationsTable"]/tbody/tr[2]/td[1]/div/a')
            date = driver.find_element(By.XPATH, '//*[@id="publicationsTable"]/tbody/tr[2]/td[4]')
        except selenium.common.exceptions.NoSuchElementException:
            table = driver.find_element(By.XPATH, '//*[@id="publicationsTable"]/tbody/tr[3]/td[1]/div/a')
            date = driver.find_element(By.XPATH, '//*[@id="publicationsTable"]/tbody/tr[3]/td[4]')

        review.append([*self.__popup_worker_eco(table, driver), date.text])
        return review

    def __popup_worker_money(self, table: wb.remote.webelement.WebElement,
                             driver: wb.firefox.webdriver.WebDriver,
                             text_filter: tuple) -> list:
        """
        Get review with filter text from popup menu after a click
        :param table: HTML element to click
        :param text_filter: Keywords for searching in review text
        :param driver: Browser session where to work
        :return: Review name and review without d'>' symbol
        """
        table.click()
        self.__sleep_some_time(2, 3)
        review_page = driver.find_element(By.XPATH, self.base_popup_xpath)
        rows = review_page.find_elements('tag name', 'p')
        output = ''
        start_bool = False
        for row in rows:
            if text_filter[0] in row.text:
                output += '\n\n' + ''.join(row.text)
                start_bool = True
            elif start_bool and (text_filter[1] not in row.text):
                output += '\n\n' + ''.join(row.text)
            else:
                start_bool = False

        # for row in rows:
        #    if (text_filter[0] not in row.text) \
        #            and (text_filter[1] not in row.text) \
        #            and ('@sber' not in row.text):
        #        output += '\n\n' + ''.join(row.text)
        try:
            review_page.send_keys(Keys.ESCAPE)
        except selenium.common.exceptions.ElementNotInteractableException:
            review_page = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/a')
            review_page.click()
        return [table.text, output.replace('>', '')]

    def auth(self, driver: wb.firefox.webdriver.WebDriver) -> wb.firefox.webdriver.WebDriver:
        """
        Authorize in sberbank research platform
        :param driver: Browser session where to work
        :return: Browser session after authorization
        """
        login = self.cred[0]
        password = self.cred[1]
        wait = WebDriverWait(driver, 10)
        driver.get(self.research_base_url)
        assert 'Login' in driver.title
        login_field = driver.find_element('id', '_58_login')
        password_field = driver.find_element('id', '_58_password')

        login_field.send_keys(login)
        password_field.send_keys(password)
        password_field.send_keys(Keys.ENTER)
        wait.until_not(ec.title_is("Login"))
        assert 'Login' not in driver.title

        return driver

    def get_everyday_reviews(self, driver: wb.firefox.webdriver.WebDriver, url: str):
        """
        Get last everyday economical reviews
        :param driver: Browser session where to work
        :param url: URL with reviews
        :return: list with lists filled with reviews info
        """
        reviews = []
        driver.get(url)
        assert 'Экономика' in driver.title
        self.__sleep_some_time()
        driver.find_element('id', self.tabs_eco['everyday']).click()
        self.__sleep_some_time()

        table = driver.find_elements('class name', 'title')
        dates = driver.find_elements('class name', 'date')
        row_numb = 0
        for i in table[1:6:2]:
            self.__sleep_some_time(2, 3)
            row_numb += 1
            reviews.append([*self.__popup_worker_eco(i, driver), dates[row_numb].text])
        return reviews

    def get_eco_review(self, driver: wb.firefox.webdriver.WebDriver, url: str):
        """
        Get review from global every month economic review
        :param driver: Browser session where to work
        :param url: URL with reviews
        :return: list with review info
        """
        review = []
        driver.get(url)
        review_filter = 'Экономика России. Ежемесячный обзор'
        assert 'Экономика' in driver.title
        self.__sleep_some_time(1.5, 2.5)
        driver.find_element('id', self.tabs_money['all']).click()
        self.__sleep_some_time(2, 3)

        search = driver.find_element('id', '_cibeconomicspublicationsportlet_WAR_cibpublicationsportlet'
                                           '_INSTANCE_btxt3yIWPKYW_publication-search-input')
        search.click()
        search.send_keys(review_filter, Keys.ENTER)
        self.__sleep_some_time(2.5, 3.2)
        try:
            table = driver.find_element(By.XPATH, '//*[@id="publicationsTable"]/tbody/tr[2]/td[1]/div/a')
            date = driver.find_element(By.XPATH, '//*[@id="publicationsTable"]/tbody/tr[2]/td[5]')
        except selenium.common.exceptions.NoSuchElementException:
            table = driver.find_element(By.XPATH, '//*[@id="publicationsTable"]/tbody/tr[3]/td[1]/div/a')
            date = driver.find_element(By.XPATH, '//*[@id="publicationsTable"]/tbody/tr[3]/td[5]')

        review.append([*self.__popup_worker_eco(table, driver), date.text])
        return review

    def get_everyday_money(self, driver: wb.firefox.webdriver.WebDriver, url: str, title: str = 'FX & Ставки',
                           text_filter: tuple = (['Процентные ставки', 'Прогноз'])):
        """
        Get last everyday money reviews
        :param title: Name of browser tab (Page name)
        :param text_filter: Keywords for searching in review text
        :param driver: Browser session where to work
        :param url: URL with reviews
        :return: list with lists filled with reviews info
        """
        reviews = []
        driver.get(url)
        assert title in driver.title
        self.__sleep_some_time(2, 3)
        try:
            driver.find_element('id', self.tabs_money['everyday']).click()
        except selenium.common.exceptions.NoSuchElementException:
            driver.find_element('id', self.tabs_metal['everyday']).click()
        self.__sleep_some_time()

        table = driver.find_elements('class name', 'summarylink')
        dates = driver.find_elements('class name', 'date')
        for row_numb, i in enumerate(table[:2]):
            self.__sleep_some_time(2, 3)
            reviews.append(([*self.__popup_worker_money(i, driver, text_filter), dates[row_numb+1].text]))
        return reviews

    def get_money_review(self, driver: wb.firefox.webdriver.WebDriver, url: str,
                         review_filter: str = 'Денежный рынок. Еженедельный обзор'):
        """
        Get review from global every month money review
        :param driver: Browser session where to work
        :param review_filter: Find specific review
        :param url: URL with reviews
        :return: list with review info
        """
        review = []
        driver.get(url)
        assert 'FX & Ставки' in driver.title
        self.__sleep_some_time(1.5, 2.5)
        driver.find_element('id', self.tabs_money['all']).click()
        self.__sleep_some_time(2, 3)

        search = driver.find_element('id', '_cibfxmmpublicationportlet_WAR_cibpublicationsportlet_'
                                           'INSTANCE_K5rpkFlwUUMi_publication-search-input')
        search.click()
        search.send_keys(review_filter, Keys.ENTER)
        self.__sleep_some_time(2.5, 3.2)
        try:
            table = driver.find_element(By.XPATH, '//*[@id="publicationsTable"]/tbody/tr[2]/td[1]/div/a')
            date = driver.find_element(By.XPATH, '//*[@id="publicationsTable"]/tbody/tr[2]/td[4]')
        except selenium.common.exceptions.NoSuchElementException:
            table = driver.find_element(By.XPATH, '//*[@id="publicationsTable"]/tbody/tr[3]/td[1]/div/a')
            date = driver.find_element(By.XPATH, '//*[@id="publicationsTable"]/tbody/tr[3]/td[4]')

        review.append([*self.__popup_worker_eco(table, driver), date.text])
        return review
'''

