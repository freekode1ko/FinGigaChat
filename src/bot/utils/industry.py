import collections
from typing import List, Dict

import pandas as pd

from module.article_process import FormatText
from db.api.industry import get_industry_name


def group_news_by_tg_channels(news: pd.DataFrame) -> Dict[str, list]:
    """
    Группирует новости из тг каналов по тг каналам

    return: Словарь, где ключ это имя тг канала, а значение это список отформатированных новостей
    """
    tg_chan_names2data = collections.defaultdict(list)

    for index, article in news.iterrows():
        format_text = FormatText(title=article['title'], date=article['date'], link=article['telegram_article_link'])
        formatted_article = format_text.make_industry_text()

        tg_chan_names2data[article['telegram_channel_name']].append(formatted_article)

    return tg_chan_names2data


def get_tg_channel_news_msg(tg_chan_name: str, news: List[str], delimiter: str = '\n\n') -> str:
    """Формирует подсообщение с новостями из тг-канала"""
    msg_text = f'<b>{tg_chan_name}:</b>\n'
    msg_text += delimiter.join(news) + delimiter
    return msg_text


async def get_msg_text_for_tg_newsletter(industry_id: int, news: pd.DataFrame, by_my_subscriptions: bool = True) -> str:
    """
    Формирует сообщение со сводкой новостей из тг каналов по подпискам за {days} дней

    :param industry_id: ID отрасли, по которой формируется сводка
    :param news: новости DataFrame['telegram_channel_name', 'telegram_article_link', 'title', 'date']
    :param by_my_subscriptions: Флаг указания, что сводка по подпискам или по всем тг каналам отрасли
    return: При формировании сводки используется FormatText.make_industry_text
    """
    industry_name = get_industry_name(industry_id)
    msg_text = (
        f'Сводка новостей по '
        f'<b>{"подпискам на telegram каналы" if by_my_subscriptions else "всем telegram каналам"}</b> '
        f'по отрасли '
        f'<b>{industry_name.capitalize()}</b>\n\n'
    )

    if not news.empty:
        news = group_news_by_tg_channels(news)

        for tg_chan_name, articles in news.items():
            msg_text += get_tg_channel_news_msg(tg_chan_name, articles)

    else:
        msg_text += 'За выбранный период новых новостей не нашлось'

    return msg_text
