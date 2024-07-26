from enum import Enum

from pydantic import BaseModel


class NewsTypeEnum(str, Enum):
    """
    Типы новостей

    p.s. Так как для фронта разное поведения в зависимости от типа новости
    """

    article = 'article'
    cib = 'cib'


class NewsItem(BaseModel):
    """Данные новости"""

    section: str
    title: str
    text: str
    date: str  # так и задумано, потому что подгоняю по формат
    news_type: NewsTypeEnum = NewsTypeEnum.article


class News(BaseModel):
    """Параметры, которые могут быть у элементов"""

    news: list[NewsItem]
