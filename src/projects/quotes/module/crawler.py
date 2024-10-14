"""Набор инструментов для сборки данных с WEB-источников"""
import random
import string

import requests as req

from configs.config import REQUEST_TIMEOUT, user_agents
from log.logger_base import Logger


DEFAULT_USER_AGENT_ALPH = string.ascii_lowercase
DEFAULT_USER_AGENT_LEN = 12


class Dictlist(dict):
    """Класс словаря, в котором значения хранятся в виде списков."""

    def __setitem__(self, key, value) -> None:
        """
        Перегружает стандартный метод __setitem__ в классе словаря, чтобы добавлять значение в список.

        :param key: Где нужно добавить значение
        :param value: Что нужно добавить
        :return: Словарь с добавленным значениям по выбранному ключу
        """
        try:
            self[key]
        except KeyError:
            super(Dictlist, self).__setitem__(key, [])
        self[key].append(value)


proxy = Dictlist()


class Parser:
    """Класс для парсинга данных."""

    user_agents = user_agents

    def __init__(self, logger: Logger.logger) -> None:
        """
        Инициализирует экземпляр класса Parser.

        :param logger: Логгер для записи действий и ошибок.
        """
        self._logger = logger

    @staticmethod
    def get_random_user_agent(alph: str = DEFAULT_USER_AGENT_ALPH, user_agent_len: int = DEFAULT_USER_AGENT_LEN) -> str:
        """
        Получить случайный user agent.

        :param alph:            Алфавит для генерации user agent
        :param user_agent_len:  Длина сгенерированного user agent
        :return:                Случайный user agent
        """
        return ''.join(random.choices(alph, k=user_agent_len))

    def set_proxy_addresses(self) -> None:
        """Метод получения списка доступных прокси и их загрузка"""
        global proxy
        proxy['https'] = ['socks5h://193.23.50.38:10222']
        proxy['https'] = ['socks5h://135.125.212.24:10034']
        proxy['https'] = ['socks5h://141.95.93.35:10112']
        proxy['https'] = ['socks5h://54.37.194.34:10526']
        self._logger.info('Прокси инициализировано')

    def get_html(self, url: str, session: req.sessions.Session) -> tuple[bool, str]:
        """
        Метод получения html страницы

        :param session: Получение сессии якобы пользователя
        :param url: Адрес страницы
        :return: флаг euro_standard, html страницы как string
        """
        euro_standard = False
        # http = random.choice(proxy['http'])
        https = random.choice(proxy['https'])
        if isinstance(https, list):
            https = https[0]
        # proxies = {'http': http, 'https': https}
        proxies = {'https': https}

        html = '<!doctype html><head><title></title></head><body><header>EMPTY PAGE</header></body></html>'
        if '.ru' in url:
            euro_standard = True
        self._logger.info(f'Сайт {url} евростандарта: {euro_standard}')

        try:
            self._logger.info('Генерируем User-Agent для запроса')
            random_user_agent = self.get_random_user_agent()
            header = {'Accept': '*/*', 'User-Agent': random_user_agent, 'Accept-Encoding': 'gzip, deflate'}
            req_page = session.get(url, verify=False, headers=header, proxies=proxies, timeout=REQUEST_TIMEOUT)
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
            random_user_agent = self.get_random_user_agent()
            header = {'Accept': '*/*', 'User-Agent': random_user_agent, 'Accept-Encoding': 'gzip, deflate'}
            req_page = session.get(url, verify=False, headers=header, timeout=REQUEST_TIMEOUT)
            html = req_page.text
            self._logger.info(f'{url} Прокси ПРОВАЛ')

            if req_page.status_code == 403:
                self._logger.critical(f'При запросе html страницы по адресу {url} было отказано в доступе')

        except Exception as ex:
            self._logger.error(f'При сборке данных с {url}, возникла ошибка: {ex}')

        return euro_standard, html
