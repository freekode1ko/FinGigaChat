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
        tabs = {'all': 'all', 'everyday': '905--910--900', 'reviews': '3--0--5--106--15--63--81--87'}
        base_popup_xpath = '/html/body/div[2]/div/div/div/div/div/div/div[3]'
        self.base_popup_xpath = base_popup_xpath
        self.research_base_url = research_base_url
        self.tabs = tabs
        self.cred = cred

    @staticmethod
    def __sleep_some_time(start: int = 1, end: int = 2):
        """
        Send user emulator to sleep.
        Fake user delay and wait to load HTML elements
        :param start: Wait from...
        :param end: Wait to...
        :return: None
        """
        time.sleep(random.uniform(start, end))

    def __popup_worker(self, table: wb.remote.webelement.WebElement, driver: wb.firefox.webdriver.WebDriver):
        """
        Get review text from popup menu after a click
        :param table: HTML element to click
        :param driver: Browser session where to work
        :return: list with text from HTML element and first and last <P> tag from review text
        """
        table.click()
        self.__sleep_some_time(2, 3)
        review_page = driver.find_element(By.XPATH, self.base_popup_xpath)
        rows = review_page.find_elements('tag name', 'p')
        review_first = driver.find_element(By.XPATH, '{}/p[1]'.format(self.base_popup_xpath)).text
        review_last = driver.find_element(By.XPATH, '{}/p[{}]'.format(self.base_popup_xpath, len(rows))).text
        # if last <P> tag is empty or to small - take previously 
        if len(review_last) < 5:
            review_last = driver.find_element(By.XPATH, '{}/p[{}]'.format(self.base_popup_xpath, len(rows)-1)).text
        review_page.send_keys(Keys.ESCAPE)
        return [table.text, '{} {}'.format(review_first, review_last)]

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
        Get last everyday reviews
        :param driver: Browser session where to work
        :param url: URL with reviews
        :return: list with lists filled with reviews info
        """
        reviews = []
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        assert 'Экономика' in driver.title
        wait.until(ec.presence_of_element_located((By.ID, self.tabs['everyday'])))  # Ежедневные
        self.__sleep_some_time()

        driver.find_element('id', self.tabs['everyday']).click()
        wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'title')))
        self.__sleep_some_time()

        table = driver.find_elements('class name', 'title')
        for i in table[1:6:2]:
            self.__sleep_some_time(2, 3)
            reviews.append(self.__popup_worker(i, driver))
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
        wait = WebDriverWait(driver, 10)
        assert 'Экономика' in driver.title
        self.__sleep_some_time(2, 3)

        wait.until(ec.presence_of_element_located((By.ID, self.tabs['reviews'])))  # Обзоры
        driver.find_element('id', self.tabs['reviews']).click()
        self.__sleep_some_time(2, 3)

        table = driver.find_element(By.XPATH, '//*[@id="publicationsTable"]/tbody/tr[2]/td[1]/div/a')
        review.append(self.__popup_worker(table, driver))

        return review
