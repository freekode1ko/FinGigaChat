from module.article_process import FormatText
from utils.db_api.industry import get_industry_name, get_industry_tg_news


async def get_msg_text_for_tg_newsletter(industry_id: int, user_id: int, days: int, by_my_subscriptions: bool = True) -> str:
    """
    Формирует сообщение со сводкой новостей из тг каналов по подпискам за {days} дней

    :param industry_id: ID отрасли, по которой формируется сводка
    :param user_id: telegram ID пользователя, для которого формируется сводка
    :param days: Промежуток в днях, за который формируется сводка
    :param by_my_subscriptions: Флаг указания, что сводка по подпискам или по всем тг каналам отрасли
    return: При формировании сводки используется FormatText.make_industry_text
    """
    industry_name = get_industry_name(industry_id)
    news = get_industry_tg_news(industry_id, by_my_subscriptions, days, user_id)
    msg_text = f'Сводка новостей по <b>{"подпискам" if by_my_subscriptions else "всем telegram каналам"}</b> по отрасли ' \
               f'<b>{industry_name.title()}</b>\n\n'

    if not news.empty:
        for index, article in news.iterrows():
            format_text = FormatText(title=article['title'], date=article['date'], link=article['telegram_article_link'])
            article = format_text.make_industry_text()

            msg_text += article + '\n\n'

    else:
        msg_text += 'За выбранный период новых новостей не нашлось'

    return msg_text
