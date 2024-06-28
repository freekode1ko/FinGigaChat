"""Модуль для получения и обработки данных обменных курсов."""
import logging
import re

import requests as req
import sqlalchemy as sa
from bs4 import BeautifulSoup, Tag

from db import database
from module import crawler, websocket_parser
from utils.quotes.base import QuotesGetter


def get_value(data: str) -> str:
    """
    Получить значение курса валюты.

    Ищет цифры и запятые. Все точки заменяет на запятые.

    :param data:    Текст со значением курса валюты
    :return:        значение курса валюты
    """
    return ''.join(re.findall(r',|\d', data.replace('.', ',')))


def parse_by_params(
    source_page: str,
    session: req.sessions.Session,
    parse_params: dict[str, str | dict],
    logger: logging.Logger,
) -> Tag | None:
    """
    Распарсить по параметрам.

    :param source_page:     Ссылка на источник
    :param session:         Сессия для выполнения HTTP-запросов.
    :param parse_params:    Параметры парсинга источника данных.
    :param logger:          Логгер.
    :return:                Тэг с данными о курсе валют или None
    """
    parser_obj = crawler.Parser(logger)
    euro_standard, page_html = parser_obj.get_html(source_page, session)
    html_parser = BeautifulSoup(page_html, 'html.parser')
    return html_parser.find(parse_params['name'], **parse_params['kwargs'])


def parse_cbr(
    source_page: str,
    session: req.sessions.Session,
    parse_params: dict[str, str | dict],
    logger: logging.Logger,
) -> str:
    """
    Распарсить данные о курсах с сайта cbr

    :param source_page:     Ссылка на источник
    :param session:         Сессия для выполнения HTTP-запросов.
    :param parse_params:    Параметры парсинга источника данных.
    :param logger:          Логгер.
    :return:                Текущий курс
    """
    data = parse_by_params(source_page, session, parse_params, logger)
    return get_value(data.parent.find_all(parse_params['children_name'])[-1].get_text())


def parse_investing(
    source_page: str,
    session: req.sessions.Session,
    parse_params: dict[str, str | dict],
    logger: logging.Logger,
) -> str:
    """
    Распарсить данные о курсах с сайта investing

    :param source_page:     Ссылка на источник
    :param session:         Сессия для выполнения HTTP-запросов.
    :param parse_params:    Параметры парсинга источника данных.
    :param logger:          Логгер.
    :return:                Текущий курс
    """
    return get_value(parse_by_params(source_page, session, parse_params, logger).get_text())


def websocket_parse_finam(
    source_page: str,
    session: req.sessions.Session,
    parse_params: dict[str, str | dict],
    logger: logging.Logger,
) -> str:
    """
    Распарсить данные о курсах с сайта finam

    :param source_page:     Ссылка на источник
    :param session:         Сессия для выполнения HTTP-запросов.
    :param parse_params:    Параметры парсинга источника данных.
    :param logger:          Логгер.
    :return:                Текущий курс
    """
    val = websocket_parser.parse_by_params(parse_params)
    return str(val).replace('.', ',')


class WrongSource(Exception):
    """Неподдерживаемый источник данных"""


class ExcGetter(QuotesGetter):
    """Класс для получения и обработки данных об обменных курсах."""

    NAME = 'exc'
    # Поддерживаемые источники
    SupportedSources = dict(
        tradingview=None,
        finam=websocket_parse_finam,
        cbr=parse_cbr,
        investing=parse_investing,
    )

    @staticmethod
    def filter(table_row: list) -> bool:
        """
        Проверяет, является ли строка таблицы строкой с данными об обменных курсах.

        :param table_row: Строка таблицы для проверки.
        :return: True, если строка содержит данные об обменных курсах, False в противном случае.
        """
        page = QuotesGetter.get_source_page_from_table_row(table_row)
        pages = ['usd-rub', 'eur-rub', 'cny-rub', 'eur-usd', 'usd-cnh', 'usdollar']
        return table_row[0] == 'Курсы валют' and page in pages

    def get_tables(self, session: req.sessions.Session) -> list:
        """
        Получить список источников.

        :param session: Сессия для выполнения HTTP-запросов.
        :return: Список источников.
        """
        with database.engine.connect() as conn:
            query = sa.text(
                'SELECT sg.name, p.id, p.response_format, p.source, p.params, e.id as exc_id '
                'FROM parser_source p '
                'JOIN source_group sg ON p.source_group_id = sg.id '
                'JOIN exc e ON e.parser_source_id = p.id '
            )
            data = conn.execute(query).all()
            return data

    def parse_source_page(self, source_page: str, session: req.sessions.Session, parse_params: dict) -> str:
        """
        Распарсить данные о курсах

        :param source_page:     Ссылка на источник
        :param session:         Сессия для выполнения HTTP-запросов.
        :param parse_params:    Параметры парсинга источника данных.
        :return:                Текущий курс
        """
        for supported_source, tool in self.SupportedSources.items():
            if supported_source in source_page:
                parse_tool = tool
                break
        else:
            raise WrongSource(f'Данный источник не поддерживается: {source_page}')

        return parse_tool(source_page, session, parse_params, self.logger)

    def preprocess(self, tables: list, session: req.sessions.Session) -> tuple[dict[int, str], set]:
        """
        Предобрабатывает таблицы данных и создает итоговый DataFrame с данными об обменных курсах.

        :param tables: Список таблиц данных.
        :param session: Сессия для выполнения HTTP-запросов.
        :return: Кортеж, содержащий DataFrame с данными об обменных курсах
        и множество идентификаторов обработанных таблиц.
        """
        preprocessed_ids = set()
        group_name = self.get_group_name()
        exchange_kot = {}

        size_tables = len(tables)
        self.logger.info(f'Обработка собранных таблиц ({group_name}) ({size_tables}).')
        for enum, source_data in enumerate(tables, 1):
            self.logger.info(f'{group_name} {enum}/{size_tables}')
            source_page = self.get_source_page_from_table_row(source_data)
            self.logger.info(f'Сборка таблицы {source_page} из блока {source_data[0]} ({group_name})')
            source_page = source_data[3]
            parse_params = source_data[4]
            exc_id = source_data[5]

            # EXCENGE BLOCK
            try:
                exchange_kot[exc_id] = self.parse_source_page(source_page, session, parse_params)
                preprocessed_ids.add(source_data[1])
            except Exception as e:
                self.logger.error(f'При обработке источника {source_page} ({group_name}) произошла ошибка: %s', e)

        return exchange_kot, preprocessed_ids

    def save(self, data: dict[int, str]) -> None:
        """
        Сохранить новые значения курсов.

        :param data: Словарь key=ID курса, value=значение курса
        """
        with database.engine.connect() as conn:
            query = sa.text(
                'UPDATE exc SET value=:value WHERE id=:exc_id'
            )
            for exc_id, value in data.items():
                conn.execute(query.bindparams(exc_id=exc_id, value=value))
            conn.commit()
