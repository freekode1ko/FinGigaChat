"""Общие утилиты, которые могут использоваться в разных частях приложения"""
import datetime


def parse_timestamp(timestamp: str) -> datetime.datetime:
    """Преобразование временной метки к datetime.

    Временные метки могут приходить в секундах (10 знаков)
    или в миллисекундах (13 знаков). Данная функция приводит
    все временные метки в соответствие секундному формату и
    возвращает datetime.

    :param str timestamp: Строковая временная метка
    :return: Объект datetime
    """
    if len(timestamp) > 10:
        timestamp = timestamp[:10]
    return datetime.datetime.fromtimestamp(int(timestamp))


def parse_value(value: str) -> float | None:
    """Преобразование значения к float.

    Функция обрабатывает значения в разных форматах и приводит
    их к float. Если значение отсутствует или имеет некорректный формат,
    то функция возвращает None.

    Правила форматирования:
    * Удаление пробелов
    * Удаление знака %
    * Замена "," на "."

    :param str value: Строковое значение
    :return: Число с плавающей точкой
    """
    value = value.replace(' ', '').replace(',', '.').replace('%', '')
    try:
        output = float(value)
    except ValueError:
        output = None
    return output
