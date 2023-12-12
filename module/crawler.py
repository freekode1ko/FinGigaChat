from module.logger_base import Logger
from config import user_agents
import requests as req
import random


class Dictlist(dict):
    def __setitem__(self, key, value) -> dict:
        """
        Overwrite default method setitem in class dict to append in list new urls
        :param key: Where need to add
        :param value: What need to add
        :return: dict with appended value in list for selected key
        """
        try:
            self[key]
        except KeyError:
            super(Dictlist, self).__setitem__(key, [])
        self[key].append(value)


proxy = Dictlist()


class Parser:
    def __init__(self, logger: Logger.logger):
        self._logger = logger

    user_agents = user_agents

    def get_proxy_addresses(self) -> None:
        """
        Method to get free proxy list from web
        and load it to package variable
        :return: None
        """
        global proxy
        proxy['https'] = ['socks5h://193.23.50.38:10222']
        proxy['https'] = ['socks5h://135.125.212.24:10034']
        proxy['https'] = ['socks5h://141.95.93.35:10112']
        proxy['https'] = ['socks5h://54.37.194.34:10526']
        self._logger.info('Прокси инициализировано')

    def get_html(self, url: str, session: req.sessions.Session):
        """
        Method return html from requester page
        :param session: request "user" session
        :param url: Where to grab html code
        :return: html code from page as string
        """
        euro_standard = False
        # http = random.choice(proxy['http'])
        https = random.choice(proxy['https'])
        # if type(http) == list:
        #     http = http[0]
        if type(https) == list:
            https = https[0]
        # proxies = {'http': http, 'https': https}
        proxies = {'https': https}

        html = '<!doctype html><head><title></title></head><body><header>EMPTY PAGE</header></body></html>'
        if '.ru' in url:
            euro_standard = True
        self._logger.debug(f'Сайт {url} евростандарта: {euro_standard}')

        try:
            self._logger.debug(f'Генерируем User-Agent для запроса')
            random_user_agent = ''.join((random.choice('qwertyuiopasdfghjklzxcvbnm') for i in range(12)))
            header = {'Accept': '*/*',
                      'User-Agent': random_user_agent,
                      'Accept-Encoding': 'gzip, deflate'}
            req_page = session.get(url, verify=False, headers=header, proxies=proxies)
            html = req_page.text
            self._logger.info(f'{url} - Прокси УСПЕХ')

            if 'ddos-guard' in req_page.text.lower():
                print('При сборке нас обнаружил DDoS Guard, попытка другим методом сбора')
                self._logger.warning('При сборке нас обнаружил DDoS Guard, попытка другим методом сбора')
                raise req.exceptions.ConnectionError

        except req.exceptions.ConnectionError:
            session = req.Session()
            random_user_agent = ''.join((random.choice('qwertyuiopasdfghjklzxcvbnm') for i in range(12)))
            header = {'Accept': '*/*',
                      'User-Agent': random_user_agent,
                      'Accept-Encoding': 'gzip, deflate'}
            req_page = session.get(url, verify=False, headers=header)
            html = req_page.text
            self._logger.info(f'{url} Прокси ПРОВАЛ')

        except Exception as ex:
            self._logger.error(f'При сборке данных с{url}, возникла ошибка: {ex}')

        return euro_standard, html
