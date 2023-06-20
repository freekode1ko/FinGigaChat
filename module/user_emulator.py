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
        time.sleep(random.uniform(start, end))

    def popup_worker(self, table, driver):
        table.click()
        self.__sleep_some_time(2, 3)
        review_page = driver.find_element(By.XPATH, self.base_popup_xpath)
        rows = review_page.find_elements('tag name', 'p')
        review_first = driver.find_element(By.XPATH, '{}/p[1]'.format(self.base_popup_xpath)).text
        review_last = driver.find_element(By.XPATH, '{}/p[{}]'.format(self.base_popup_xpath, len(rows))).text
        if len(review_last) < 5:
            review_last = driver.find_element(By.XPATH, '{}/p[{}]'.format(self.base_popup_xpath, len(rows)-1)).text
        review_page.send_keys(Keys.ESCAPE)
        return [table.text, '{} {}'.format(review_first, review_last)]

    def auth(self, driver):
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

    def get_everyday_reviews(self, driver, url):
        reviews = []
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        assert 'Экономика' in driver.title
        wait.until(ec.presence_of_element_located((By.ID, self.tabs['everyday'])))  # Ежедневные
        self.__sleep_some_time()

        driver.find_element('id', '905--910--900').click()
        wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'title')))
        self.__sleep_some_time()

        table = driver.find_elements('class name', 'title')
        for i in table[1:6:2]:
            self.__sleep_some_time(2, 3)
            # print(i.text)
            reviews.append(self.popup_worker(i, driver))
        return reviews

    def get_eco_review(self, driver, url):
        review = []
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        self.__sleep_some_time(2, 3)
        wait.until(ec.presence_of_element_located((By.ID, self.tabs['reviews'])))  # Обзоры
        driver.find_element('id', self.tabs['reviews']).click()
        self.__sleep_some_time(2, 3)
        table = driver.find_element(By.XPATH, '//*[@id="publicationsTable"]/tbody/tr[2]/td[1]/div/a')
        review.append(self.popup_worker(table, driver))
        '''
        eco_xpath = '//*[@id="publicationsTableContainer"]/div[2]'
        last_eco_review = driver.find_element(By.XPATH, eco_xpath)
        last_eco_review.click()
        time.sleep(2)
        eco_review_text = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div/div/div/div[3]/p[1]').text
        # last_eco_review.send_keys(Keys.ESCAPE)
        review.append([last_eco_review.text, eco_review_text])
        print(review)
        '''
        return review
