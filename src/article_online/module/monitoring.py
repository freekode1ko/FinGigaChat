"""Модуль с методами по обновлению дат парсинга и сохранения новостей."""
from sqlalchemy import text

from configs.config import SUBJECT_ARTICLES, TG_ARTICLES
from db import database


def update_get_datetime(name: str) -> None:
    """
    Обновляет время сбора данных.

    :param name: Имя собираемых данных.
    """
    query = text(
        'UPDATE parser_source '
        'SET previous_update_datetime=last_update_datetime, last_update_datetime=CURRENT_TIMESTAMP '
        'WHERE name=:name;'
    )
    with database.engine.connect() as conn:
        conn.execute(query.bindparams(name=name))
        conn.commit()


def update_save_datetime(name: str) -> None:
    """
    Обновляет время сохранения данных.

    :param name: Имя собираемых данных.
    """
    query = text('UPDATE parser_source SET last_save_datetime=CURRENT_TIMESTAMP WHERE name=:name')
    with database.engine.connect() as conn:
        conn.execute(query.bindparams(name=name))
        conn.commit()


def update_parsing_status(len_subject_articles: int, len_tg_articles: int):
    """
    Обновление статуса парсинга новостей от ГигаПарсерс.

    :param len_subject_articles:
    :param len_tg_articles:
    :return:
    """
    if len_tg_articles:
        update_get_datetime(TG_ARTICLES)
    if len_subject_articles > len_tg_articles:
        update_get_datetime(SUBJECT_ARTICLES)


def update_saving_status(subject_links: list[str], tg_links: list[str]):
    """
    Обновление статуса сохранения новостей.

    :param subject_links: Список из ссылок на новости с объектами.
    :param tg_links:      Список из ссылок на новости отраслевые (тг).
    """
    if tg_links:
        update_save_datetime(TG_ARTICLES)
    if subject_links:
        update_save_datetime(SUBJECT_ARTICLES)
