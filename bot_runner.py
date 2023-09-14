from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hlink
from aiogram.utils.exceptions import MessageIsTooLong
from config import bot_token
import pandas as pd
from sqlalchemy import create_engine, text
from config import psql_engine

bot = Bot(token=bot_token)
dp = Dispatcher(bot)


async def find_subject_id(engine, message: types.Message, subject: str):
    """
    Find id of client or commodity by user alias
    :param engine: engine to database
    :param message: user massage
    :param subject: client or commodity
    :return: id of client(commodity) or False if user alias not about client or commodity
    """

    message_text = message.text.lower().strip()
    df_alternative = pd.read_sql(f'SELECT {subject}_id, other_names FROM {subject}_alternative', con=engine)
    df_alternative['other_names'] = df_alternative['other_names'].apply(lambda x: x.split(';'))

    for subject_id, names in zip(df_alternative[f'{subject}_id'], df_alternative['other_names']):
        if message_text in names:
            return subject_id
    return False


async def get_article(engine, subject_id: int, subject: str):
    """
    Get sorted sum article by subject id.
    :param engine: engine to database
    :param subject_id: id of client or commodity
    :param subject: client or commodity
    :return: name of client(commodity) and sorted sum article
    """
    with engine.connect() as conn:

        query_article_data = (f'SELECT relation.article_id, relation.{subject}_score, '
                              f'article_.date, article_.link, article_.text_sum '
                              f'FROM relation_{subject}_article AS relation '
                              f'INNER JOIN ('
                              f'SELECT id, date, link, text_sum '
                              f'FROM article '
                              f') AS article_ '
                              f'ON article_.id = relation.article_id '
                              f'WHERE relation.{subject}_id = {subject_id} AND relation.{subject}_score <> 0 '
                              f'ORDER BY date DESC, relation.{subject}_score DESC '
                              f'LIMIT 5')

        article_data = [item[3:] for item in conn.execute(text(query_article_data))]
        name = conn.execute(text(f'SELECT name FROM {subject} WHERE id={subject_id}')).fetchone()[0]
        return name, article_data


async def alias_article(engine, message: types.Message):
    """ Check articles and make format message """
    subject_name, articles = '', ''
    client_id = await find_subject_id(engine, message, 'client')
    if client_id:
        subject_name, articles = await get_article(engine, client_id, 'client')
    else:
        commodity_id = await find_subject_id(engine, message, 'commodity')
        if commodity_id:
            subject_name, articles = await get_article(engine, commodity_id, 'commodity')
        else:
            print('user do not want articles')

    if subject_name and not articles:
        return f'Пока нет новостей на эту тему'
    elif not articles:
        return False

    for index, article_data in enumerate(articles):
        link, text_sum = article_data[0], article_data[1]
        marker = '&#128204;'
        # TODO: убрать разделение, когда полианалист удалит лишние пробелы
        text_sum = ' '.join(text_sum.split())
        link_phrase = hlink('Ссылка на источник.', link)
        articles[index] = f'{marker} {text_sum} {link_phrase}'

    all_articles = '\n\n'.join(articles)
    reply_msg = f'<b>{subject_name.capitalize()}</b>\n\n{all_articles}'

    return reply_msg


@dp.message_handler()
async def giga_ask(message: types.Message):
    engine = create_engine(psql_engine)
    reply_msg = await alias_article(engine, message)
    if reply_msg:
        try:
            await message.answer(reply_msg, parse_mode='HTML', protect_content=True, disable_web_page_preview=True)
        except MessageIsTooLong:
            articles = reply_msg.split('\n\n')
            for article in articles:
                await message.answer(article, parse_mode='HTML', protect_content=True, disable_web_page_preview=True)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)