from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from configs import config
from constants import constants
from constants.enums import HTTPMethod
from main import bot
from utils.function_calling.tool_functions.preparing_meeting.config import MESSAGE_RUN_RAG_NEWS, MESSAGE_RUN_RAG_WEB, \
    MESSAGE_RUN_RAG_WEB, MESSAGE_RUN_RAG_CIB
from utils.function_calling.tool_functions.utils import send_status_message_for_agent
from utils.sessions import RagWebClient, RagQaBankerClient, RagQaResearchClient


async def request_to_rag_api(rag_type, query, with_metadata=False):
    try:
        rag = rag_type()
        json = {
            'body': query if (query := query.strip())[-1] == '?' else query + '?'
        }
        if with_metadata:
            json['with_metadata'] = True

        async with rag.session.request(
                method=HTTPMethod.POST,
                url='/api/v1/question',
                json=json,
                timeout=config.POST_TO_SERVICE_TIMEOUT,
        ) as rag_response:
            return await rag_response.json()
    except Exception as e:
        print(e)
        pass


@tool
async def rag_news(request_text: str, config: RunnableConfig):
    """Возвращает текст с ответом из базы знаний по новостям по заданному вопросу.

    Args:
        request_text (str): текст вопроса
    return:
        (str): текст ответа.
    """
    # rag_qa_banker
    print(f"Вызвана функция rag_news с параметром {request_text}")

    await send_status_message_for_agent(config, MESSAGE_RUN_RAG_NEWS)

    msg = await request_to_rag_api(RagQaBankerClient, request_text)
    print(f'Окончен вызов функции rag_news')
    return msg


@tool
async def rag_cib(request_text: str, config: RunnableConfig):
    """Возвращает текст с ответом из базы знаний по аналитическим отчетам CIB по заданному вопросу.

    Args:
        request_text (str): текст вопроса
    return:
        (str): текст ответа.
    """
    print(f"Вызвана функция rag_cib с параметром {request_text}")

    await send_status_message_for_agent(config, MESSAGE_RUN_RAG_CIB)

    msg = await request_to_rag_api(RagQaResearchClient, request_text, with_metadata=True)
    print(f'Окончен вызов функции rag_cib')
    return msg


@tool
async def rag_web(request_text: str, config: RunnableConfig):
    """Возвращает текст с ответом из базы поискового движка по заданному вопросу.

    Args:
        request_text (str): текст вопроса
    return:
        (str): текст ответа.
    """
    print(f"Вызвана функция rag_web с параметром {request_text}")

    await send_status_message_for_agent(config, MESSAGE_RUN_RAG_WEB)

    msg = await request_to_rag_api(RagWebClient, request_text, with_metadata=True)
    print(f'Окончен вызов функции rag_web')
    return msg
