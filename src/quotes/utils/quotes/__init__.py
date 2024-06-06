"""
Модуль для получения групп обработчиков котировок.

Этот модуль предоставляет доступ к различным обработчикам котировок, таким как обработчики облигаций,
экономических данных, обменных курсов и металлов. Функция `get_groups` возвращает список этих обработчиков.
"""
from utils.quotes.bonds import BondsGetter
from utils.quotes.eco import EcoGetter
from utils.quotes.exc import ExcGetter
from utils.quotes.metals import MetalsGetter


def get_groups() -> list:
    """
    Возвращает список обработчиков котировок.

    :return: Список обработчиков котировок.
    """
    return [BondsGetter, EcoGetter, ExcGetter, MetalsGetter]
