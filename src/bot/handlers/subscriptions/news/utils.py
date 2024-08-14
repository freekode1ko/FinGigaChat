"""Вспомогательные функции для интерфейса с подписками на новости"""
import pandas as pd

from configs.config import PAGE_ELEMENTS_COUNT

QUOTES = ['\"', '«', '»']


def clear_user_request(message_text: str) -> str:
    """
    Очистить запрос пользователя.

    :param message_text:    Текст запроса
    :return:                Очищенный запрос
    """
    for quote in QUOTES:
        message_text = message_text.replace(quote, '')

    return message_text.strip()


def find_page_by_subject_id(
        all_data_df: pd.DataFrame,
        looking_for_id: int,
        page_elements: int = PAGE_ELEMENTS_COUNT,
) -> int:
    """
    Найти страницу, на которой находится искомый субъект.

    :param all_data_df:     Данные, которые отображаются постранично
    :param looking_for_id:  Искомый субъект
    :param page_elements:   Кол-во элементов на странице
    :return:                Страница, на которой находится искомый субъект, или -1, если не найден субъект
    """
    return found[0] // page_elements if (found := all_data_df.index[all_data_df['id'] == looking_for_id].tolist()) else -1


def find_page_by_subject_name(
        all_data_df: pd.DataFrame,
        looking_for_name: str,
        page_elements: int = PAGE_ELEMENTS_COUNT,
) -> int:
    """
    Найти страницу, на которой находится искомый субъект.

    :param all_data_df:     Данные, которые отображаются постранично
    :param looking_for_name:  Искомый субъект
    :param page_elements:   Кол-во элементов на странице
    :return:                Страница, на которой находится искомый субъект, или -1, если не найден субъект
    """
    return (found[0] // page_elements
            if (found := all_data_df.index[all_data_df['name'].str.lower() == looking_for_name.lower()].tolist())
            else -1)
