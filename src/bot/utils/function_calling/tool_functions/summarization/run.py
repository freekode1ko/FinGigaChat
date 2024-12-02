import sqlalchemy as sa
from aiogram import types
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_gigachat.chat_models.gigachat import GigaChat

from configs.config import giga_chat_url, giga_scope, giga_model, giga_credentials
from constants import constants
from db import models
from db.database import async_session
from main import bot
from module.fuzzy_search import FuzzyAlternativeNames
from utils.function_calling.tool_functions.tool_prompts import SUMMARIZATION_SYSTEM, SUMMARIZATION_USER
from utils.function_calling.tool_functions.utils import get_answer_giga


@tool
async def get_news_by_name(name: str, config: RunnableConfig):
    """Возвращает текст с суммаризированными инфоповодами по компании по заданному названию компании.

    Args:
        name (str): только название компании в именительном падеже.
    return:
        (str): Текст с новостями по компании.
    """
    print(f'Вызвана функция get_news_by_name с параметром: {name}')

    message = config['configurable']['message']
    buttons = config['configurable']['buttons']
    message_text = config['configurable']['message_text']
    final_message: types.Message = config['configurable']['final_message']

    message_text.append('-Обработка новостей\n')

    await final_message.edit_text(''.join(message_text) + f'{constants.LOADING_EMOJI_HTML}', parse_mode='HTML')
    limit = 10
    fuzzy_searcher = FuzzyAlternativeNames()
    clients_id = await fuzzy_searcher.find_subjects_id_by_name(
        name,
        subject_types=[models.ClientAlternative],
        score=95,
    )
    if clients_id:
        client_id = clients_id[0]
    else:
        return 'Ничего не найдено'
    async with async_session() as session:
        client_articles = await session.execute(
            sa.select(models.Article.text_sum)
            .join(models.RelationClientArticle)
            .filter(models.RelationClientArticle.client_id == client_id)
            .order_by(models.Article.date)
            .limit(limit)
        )
    result = client_articles.scalars().all()

    llm = GigaChat(verbose=True,
                   credentials=giga_credentials,
                   scope=giga_scope,
                   model=giga_model,
                   verify_ssl_certs=False,
                   profanity_check=False,
                   temperature=0.00001
                   )
    text = await get_answer_giga(llm, SUMMARIZATION_SYSTEM, SUMMARIZATION_USER, '\n'.join(result))
    return text
