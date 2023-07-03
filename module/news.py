import time, random, re
import pandas as pd
import openpyxl
import datetime as dt
from selenium import webdriver

class RiaNewsParser:
    def __init__(self, driver):
        ria_url = 'https://ria.ru/economy/'
        date_format = '%H:%M %d.%m.%Y'

        self.ria_url = ria_url
        self.date_format = date_format
        self.driver = driver

    def _get_article_date(self):
        """
        Get last date of the article
        :param driver: driver
        :return: last date of the article
        """
        date_first = self.driver.find_element('css selector', '.article__info-date a').text
        # Нужно проверить на новостях, у которых к дате приписывается слово "дополняется"
        # date_update = self.driver.find_element('css selector', '.article__info-date span').text
        # date = date_update[:date_update.find(')')].replace('(обновлено: ', '') if date_update else date_first
        # if re.search('(.*) дополняется', date):
        #     date = date[:date.find('д')]
        # date = dt.datetime.strptime(date, self.date_format)
        date = dt.datetime.strptime(date_first, self.date_format)
        return date

    def _get_article_title(self):
        """
        Get title of the article
        :param driver: driver
        :return: title of the article
        """
        title = self.driver.find_element('class name', 'article__title').text
        return title

    def _get_atricle_text(self):
        """
        Get all text of the article
        :param driver: driver
        :return: text of the article
        """
        blocks = self.driver.find_elements('css selector', '.article__block')
        blocks = [block for block in blocks if block.get_attribute('data-type') == 'text' or block.get_attribute('data-type') == 'quote']
        return '\n'.join([block.text for block in blocks])

    def _get_article_info(self, url: str, difference: bool = False):
        """
        Get information about article.
        :param driver: driver
        :param url: url of the article
        :return: date of article, title of article, text of article
        """
        date, title, text = None, None, None
        self.driver.execute_script(f'window.open("{url}")')
        self.driver.switch_to.window(self.driver.window_handles[1])
        time.sleep(3)

        if not difference:
            title = self._get_article_title()
            text = self._get_atricle_text()
            print(title)
        date = self._get_article_date()

        time.sleep(1)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

        return [date, title, text]

    def _get_articles_for_period(self, period: int = 1):
        """
        Get list of links of articles for the period.
        :param period: period in days.
        :return: List of the article links.
        """
        self.driver.get(self.ria_url)
        RiaNewsParser.__sleep_some_time(4, 5)
        flag, new_date, links_news = True, None, []
        remove_lenta = self.driver.find_element('class name', 'lenta__close')
        remove_lenta.click()

        while flag:
            button = self.driver.find_element('class name', 'list-more.color-btn-second-hover')
            button.click()
            news = self.driver.find_elements('css selector', 'a.list-item__title.color-font-hover-only')
            links_news = [new.get_attribute('href') for new in news]
            if new_date is None:
                new_date = self._get_article_info(links_news[0], True)[0]
            old_date = self._get_article_info(links_news[-1], True)[0]
            flag = RiaNewsParser.__get_timedelta(new_date, old_date, period)

        print(len(links_news))
        return links_news

    def get_articles(self, period: int = 1):
        """
        Make list with info about atricles for period.
        :param period: period in days.
        :return: list with data about articles [[date, title, text]]
        """
        links_news = self._get_articles_for_period(period)
        articles_data = []
        for link in links_news:
            article_data = self._get_article_info(link)
            articles_data.append(article_data)
        return articles_data

    @staticmethod
    def __sleep_some_time(start: float = 2.0, end: float = 3.0):
        """
        Send user emulator to sleep.
        Fake user delay and wait to load HTML elements
        :param start: Wait from...
        :param end: Wait to...
        :return: None
        """
        time.sleep(random.uniform(start, end))

    @staticmethod
    def __get_timedelta(new_date: dt.datetime, old_date: dt.datetime, period: int = 1):
        """
        Find difference between first and last articles dates.
        :param new_date:
        :param old_date:
        :return:True if difference between first and last articles dates is bigger or equal one month and False if less.
        """
        time_delta = new_date - old_date
        print(new_date, ' - ', old_date, ' = ', time_delta.days)
        return False if time_delta.days >= period else True


def save_articles(articles,  file_name: str):
    df = pd.DataFrame(articles, columns=['date', 'title', 'article'])
    df.to_excel(file_name, index=False)

def main():
    start = time.time()
    driver = webdriver.Firefox()
    driver.implicitly_wait(5)
    ria_parser = RiaNewsParser(driver)
    ria_articles = ria_parser.get_articles(period=1)
    print('Done! Closing Browser after 10 sec...')
    end = int((time.time() - start)/60)
    print(end)
    time.sleep(10)
    driver.close()

    save_articles(ria_articles, 'Ria news.xlsx')

if __name__ == '__main__':
    main()