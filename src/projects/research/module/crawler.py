"""Модуль парсера"""
import random

import requests as req

from configs.config import user_agents
from log.logger_base import Logger


class Dictlist(dict):
    """Словарь с переопределенными методами для работы со списками."""

    def __setitem__(self, key, value) -> None:
        """
        Метод задания значения по ключу.

        Задает список со значением value, если key отсутствует в словаре.
        Добавляет значение value в список, если key присутсвует в словаре.

        :param key:     Ключ (хешируемый объект)
        :param value:   Значение, сохраняемое по ключу
        """
        try:
            self[key]
        except KeyError:
            super(Dictlist, self).__setitem__(key, [])
        self[key].append(value)


proxy = Dictlist()


class Parser:
    """Класс парсера"""

    user_agents = user_agents

    def __init__(self, logger: Logger.logger) -> None:
        """Инициализация парсера"""
        self._logger = logger

    def get_proxy_addresses(self) -> None:
        """Метод получения списка бесплатных прокси и сохранение его с переменную proxy"""
        global proxy
        proxy['https'] = ['socks5h://193.23.50.38:10222']
        proxy['https'] = ['socks5h://135.125.212.24:10034']
        proxy['https'] = ['socks5h://141.95.93.35:10112']
        proxy['https'] = ['socks5h://54.37.194.34:10526']
        self._logger.info('Прокси инициализировано')

    def get_html(self, url: str, session: req.sessions.Session):
        """
        Получение html страницы по переданному адресу

        :param session: request "user" session
        :param url:     Where to grab html code
        :return:        html code from page as string
        """
        euro_standard = False
        # http = random.choice(proxy['http'])
        https = random.choice(proxy['https'])
        # if type(http) == list:
        #     http = http[0]
        if type(https) is list:
            https = https[0]
        # proxies = {'http': http, 'https': https}
        proxies = {'https': https}

        html = '<!doctype html><head><title></title></head><body><header>EMPTY PAGE</header></body></html>'
        if '.ru' in url:
            euro_standard = True
        self._logger.info(f'Сайт {url} евростандарта: {euro_standard}')

        try:
            self._logger.info('Генерируем User-Agent для запроса')
            random_user_agent = ''.join((random.choice('qwertyuiopasdfghjklzxcvbnm') for i in range(12)))
            header = {'Accept': '*/*', 'User-Agent': random_user_agent, 'Accept-Encoding': 'gzip, deflate'}
            req_page = session.get(url, verify=False, headers=header, proxies=proxies)
            html = req_page.text
            self._logger.info(f'{url} - Прокси УСПЕХ')

            if 'ddos-guard' in req_page.text.lower():
                print('При сборке нас обнаружил DDoS Guard, попытка другим методом сбора')
                self._logger.warning('При сборке нас обнаружил DDoS Guard, попытка другим методом сбора')
                raise req.exceptions.ConnectionError

            if req_page.status_code == 403:
                self._logger.critical(f'При запросе html страницы по адресу {url} было отказано в доступе')

        except req.exceptions.ConnectionError:
            session = req.Session()
            random_user_agent = ''.join((random.choice('qwertyuiopasdfghjklzxcvbnm') for i in range(12)))
            header = {'Accept': '*/*', 'User-Agent': random_user_agent, 'Accept-Encoding': 'gzip, deflate'}
            req_page = session.get(url, verify=False, headers=header)
            html = req_page.text
            self._logger.info(f'{url} Прокси ПРОВАЛ')

            if req_page.status_code == 403:
                self._logger.critical(f'При запросе html страницы по адресу {url} было отказано в доступе')

        except Exception as ex:
            self._logger.error(f'При сборке данных с {url}, возникла ошибка: {ex}')

        return euro_standard, html
