from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import config
import time


class ResearchParser:
    def __init__(self):
        cred = config.research_cred
        research_base_url = config.research_base_url
        tabs = {'all': 'all', 'everyday': '905--910--900', 'reviews': '3--0--5--106--15--63--81--87'}
        self.cred = cred
        self.research_base_url = research_base_url
        self.tabs = tabs

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
        time.sleep(1)
        driver.find_element('id', '905--910--900').click()
        wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'title')))
        time.sleep(1)
        table = driver.find_elements('class name', 'title')
        for i in table[1:6:2]:
            time.sleep(2)
            print(i.text)
            i.click()
            time.sleep(2)
            review = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div/div/div/div[3]')
            review_1 = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div/div/div/div[3]/p[1]').text
            review_3 = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div/div/div/div[3]/p[3]').text
            review.send_keys(Keys.ESCAPE)
            reviews.append('{}\n{}'.format(review_1, review_3))
        return reviews

    def get_eco_review(self, driver, url):
        review = []
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        time.sleep(2)
        wait.until(ec.presence_of_element_located((By.ID, self.tabs['reviews'])))  # Обзоры
        driver.find_element('id', self.tabs['reviews']).click()
        time.sleep(2)
        eco_xpath = '//*[@id="publicationsTableContainer"]/div[2]'
        last_eco_review = driver.find_element(By.XPATH, eco_xpath)
        last_eco_review.click()
        time.sleep(2)
        eco_review_text = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div/div/div/div[3]/p[1]').text
        # last_eco_review.send_keys(Keys.ESCAPE)
        review.append([last_eco_review.text, eco_review_text])
        print(review)
        return review
