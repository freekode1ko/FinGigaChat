"""Модуль для обработки котировок от GigaParsers"""
import datetime
import re
from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from constants.gigaparsers import GIGAPARSERS_API, GIGAPARSERS_RULES
from db import crud, models
from db.database import async_session
from log.logger_base import logger
from utils.common import parse_timestamp, parse_value


@dataclass
class QuoteRule:
    """Класс, представляющий набор значений по правилам для котировок от GigaParsers"""

    section_name: str
    section_params: dict[str, Any]
    value_fields: list[str]
    field_mapping: dict[str, str]
    quote_name: str


def _get_quote_rule(source: str, quote: str) -> QuoteRule | None:
    """Поиск правила для котировки.

    Ищет правило для данной котировки по источнику.
    Возвращает объект QuoteRule.

    :param str source: Источник котировки
    :param str quote: Котировка
    :return: Объект QuoteRule
    """
    rules = GIGAPARSERS_RULES.get(source)
    if not rules:
        return None
    for rule in rules:
        pattern = re.compile(rule['pattern'])
        if match := pattern.match(quote):
            section_name = rule['get_section_name'](match)
            section_params = rule.get('section_params', {})
            value_fields = rule.get('value_fields', ['value'])
            field_mapping = rule.get('field_mapping', {})
            quote_name = match.group('quote')
            return QuoteRule(
                section_name=section_name,
                section_params=section_params,
                value_fields=value_fields,
                field_mapping=field_mapping,
                quote_name=quote_name
            )
    return None


async def _process_quote_by_quote_rule(
        session: AsyncSession,
        quote_data: dict[str, Any],
        quote_rule: QuoteRule,
) -> list[dict[str, Any]]:
    """Функция для обработки котировки по заданному правилу.

    :param AsyncSession session: Сессия SQLAlchemy
    :param dict[str, Any] quote_data: Данные по котировке от GigaParsers
    :param QuoteRule quote_rule: Правила обработки данной котировки

    :return: Список значений для вставки в таблицу QuotesValues базы данных
    """
    last_update = datetime.datetime.now()
    section = await crud.get_or_load_quote_section_by_name(
        session,
        quote_rule.section_name,
        params=quote_rule.section_params,
        autocommit=False,
    )
    db_quote = await crud.get_or_load_quote_by_name(
        session,
        quote_rule.quote_name,
        section_id=section.id,
        insert_content={
            'source': GIGAPARSERS_API,
            'last_update': last_update,
        },
        autocommit=False,
    )
    values_to_insert = []
    for timestamp, values in quote_data.items():
        if isinstance(values, dict):
            quote_to_insert = {
                'quote_id': db_quote.id,
                'date': parse_timestamp(timestamp),
            }
            for field in quote_rule.value_fields:
                target_field = quote_rule.field_mapping.get(field)
                value = values.get(field)
                if value is None:
                    continue
                quote_to_insert[target_field] = parse_value(value)
                # Иногда в данных нет value, тогда на место value пробуем подставить close
                if 'value' not in quote_to_insert:
                    quote_to_insert['value'] = quote_to_insert.get('close', 0)
        else:
            quote_to_insert = {
                'quote_id': db_quote.id,
                'date': parse_timestamp(timestamp),
                'value': parse_value(values),
            }
        values_to_insert.append(quote_to_insert)
    return values_to_insert


async def process_gigaparser_source(
    source: str,
    data: dict[str, Any],
) -> None:
    """
    Общая функция обработки данных для разных источников.

    :param str source: Источник котировки
    :param dict[str, Any] data: Данные по источнику от GigaParsers
    """
    async with async_session() as session:
        insert_quotes = []
        for quote, quote_data in data.items():
            if quote_data is None:
                logger.warning(f'Некорректные данные для {quote} из {source}')
                continue
            quote_rule = _get_quote_rule(source, quote)
            if quote_rule is None:
                logger.warning(f'Нет правил для котировки {quote} из {source}')
                continue
            try:
                values_to_insert = await _process_quote_by_quote_rule(
                    session,
                    quote_data=quote_data,
                    quote_rule=quote_rule,
                )
                insert_quotes.extend(values_to_insert)
            except Exception as e:
                logger.exception(f'Ошибка во время обработки {quote}: {e}')
                continue
        await crud.custom_insert_or_update_to_postgres(
            session,
            models.QuotesValues,
            insert_quotes,
            constraint='uq_quote_and_date',
        )
