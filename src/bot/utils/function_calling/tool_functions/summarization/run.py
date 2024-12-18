import sqlalchemy as sa
from aiogram import types
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_gigachat.chat_models.gigachat import GigaChat

from configs.config import giga_scope, giga_agent_model, giga_credentials
from constants.texts import texts_manager
from db import models
from db.api.client import get_research_type_id_by_name
from db.database import async_session
from handlers.clients import keyboards
from module.fuzzy_search import FuzzyAlternativeNames
from utils.function_calling.tool_functions.preparing_meeting.config import MESSAGE_RUN_NEWS
from utils.function_calling.tool_functions.tool_prompts import SUMMARIZATION_SYSTEM, SUMMARIZATION_USER
from utils.function_calling.tool_functions.utils import get_answer_giga, send_status_message_for_agent


@tool
async def get_news_by_name(name: str, config: RunnableConfig):
    """Возвращает текст с суммаризированными инфоповодами по компании по заданному названию компании.

    Args:
        name (str): только название компании в именительном падеже.
    return:
        (str): Текст с новостями по компании.
    """
    print(f'Вызвана функция get_news_by_name с параметром: {name}')

    await send_status_message_for_agent(config, MESSAGE_RUN_NEWS)

    limit = 10
    fuzzy_searcher = FuzzyAlternativeNames()
    clients_id = await fuzzy_searcher.find_subjects_id_by_name(
        name,
        subject_types=[models.ClientAlternative],
        score=95,
    )
    if clients_id:
        client_id = clients_id[0]  # больше одного клиента найтись скорее всего не может, если большой процент совпадения стоит
        try:

            buttons = config['configurable']['buttons']
            buttons.append(
                {
                    'keyboard': keyboards.get_client_menu_kb(
                        client_id,
                        current_page=0,
                        research_type_id=await get_research_type_id_by_name(name),
                        with_back_button=False,
                    ),
                    'message': texts_manager.CLIENT_CHOOSE_SECTION.format(name=name.capitalize())
                }
            )
            print('Добавлено меню в новостях')
        except Exception as e:
            print('Не добавлено меню в новостях ;(')
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
                   model=giga_agent_model,
                   verify_ssl_certs=False,
                   profanity_check=False,
                   temperature=0.00001
                   )
    text = await get_answer_giga(llm, SUMMARIZATION_SYSTEM, SUMMARIZATION_USER, '\n'.join(result))
    print(f'Закончен вызов функции get_news_by_name')

    return text
