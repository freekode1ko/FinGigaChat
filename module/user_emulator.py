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

    def __popup_worker_eco(self, table: wb.remote.webelement.WebElement, driver: wb.firefox.webdriver.WebDriver):
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
            review += row.text
        try:
            review_page.send_keys(Keys.ESCAPE)
        except selenium.common.exceptions.ElementNotInteractableException:
            review_page = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/a')
            review_page.click()
        return [table.text, review]

    def __popup_worker_money(self, table: wb.remote.webelement.WebElement,
                             driver: wb.firefox.webdriver.WebDriver,
                             text_filter: tuple):
        """
        Get review with filter text from popup menu after a click
        :param table: HTML element to click
        :param text_filter: Keywords for searching in review text
        :param driver: Browser session where to work
        :return: Review name and review without '>' symbol
        """
        table.click()
        self.__sleep_some_time(2, 3)
        review_page = driver.find_element(By.XPATH, self.base_popup_xpath)
        rows = review_page.find_elements('tag name', 'p')
        output = ''
        for row in rows:
            if (text_filter[0] not in row.text) \
                    and (text_filter[1] not in row.text) \
                    and ('@sber' not in row.text):
                output += ''.join(row.text)
        try:
            review_page.send_keys(Keys.ESCAPE)
        except selenium.common.exceptions.ElementNotInteractableException:
            review_page = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/a')
            review_page.click()
        return [table.text, output.replace('>', '')]

    def auth(self, driver: wb.firefox.webdriver.WebDriver):
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
        assert 'Экономика' in driver.title
        self.__sleep_some_time(1.5, 2.5)
        driver.find_element('id', self.tabs_eco['reviews']).click()
        self.__sleep_some_time(2, 3)

        table = driver.find_element(By.XPATH, '//*[@id="publicationsTable"]/tbody/tr[2]/td[1]/div/a')
        date = driver.find_element(By.XPATH, '//*[@id="publicationsTable"]/tbody/tr[2]/td[5]')
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
