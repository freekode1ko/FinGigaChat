"""Модуль с текстовыми константами по новостям."""
from pydantic_settings import BaseSettings


class NewsTexts(BaseSettings):
    """Класс с текстовками по новостям."""

    NEWS_HEADER: str = 'Новости'

    NEWS_END: str = 'Просмотр новостей завершен'

    NEWS_CHOOSE_INDUSTRY: str = 'Выберите отрасль для получения новостей'

    NEWS_CHOOSE_INDUSTRY_SOURCE: str = 'Выберите откуда вы хотите получить новости по отрасли <b>{name}</b>'

    NEWS_CHOOSE_TELEGRAM_INDUSTRY_CHANNEL: str = (
        'Телеграм-каналы по отрасли "{section}"\n\n'
        'Выберите телеграм каналы, по которым хотите получить новости'
    )

    NEWS_ABOUT_INDUSTRY_FOR_PERIOD: str = 'Новости по отрасли <b>{name}</b> за {days} дней'

    NEWS_CHOOSE_SUBJECT_FROM_SUBS: str = 'Выберите {subject} из списка ваших подписок\n<b>{page_info}</b>'

    NEWS_CHOOSE_SUBJECT_FROM_LIST: str = 'Выберите {subject} из списка'

    NEWS_CHOOSE_PERIOD: str = 'Выберите период для получения новостей по <b>{values}</b>'

    NEWS_WRITE_SUBJECT_NAME: str = 'Для поиска введите сообщение с именем {subject}.'

    NEWS_SUBJECT_NOT_FOUND: str = 'Не нашелся, введите имя по-другому'

    NEWS_ABOUT_SUBJECT_FOR_PERIOD: str = 'Новости по {subject} за {days} дней\n'

    NEWS_ABOUT_SUBJECT_FOR_PERIOD_NOT_FOUND: str = 'Новости по <b>{values}</b> за {days} дней отсутствуют'

    NEWS_RETRY: str = 'Пожалуйста, перезапустите меню новостей'

    NEWS_NOT_FOUND: str = 'Пока нет новостей на эту тему'
