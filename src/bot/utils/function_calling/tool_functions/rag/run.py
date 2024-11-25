from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

@tool
async def rag_news(request_text: str, config: RunnableConfig):
    """Возвращает текст с ответом из базы знаний по новостям по заданному вопросу.

    Args:
        request_text (str): текст вопроса
    return:
        (str): текст ответа.
    """
    print(f"Вызвана rag_news с параметром {request_text}")
    msg = "Ответ"
    return msg


@tool
async def rag_cib(request_text: str, config: RunnableConfig):
    """Возвращает текст с ответом из базы знаний по аналитическим отчетам CIB по заданному вопросу.

    Args:
        request_text (str): текст вопроса
    return:
        (str): текст ответа.
    """
    print(f"Вызвана rag_cib с параметром {request_text}")
    msg = "Ответ из CIB"
    return msg


@tool
async def rag_web(request_text: str, config: RunnableConfig):
    """Возвращает текст с ответом из базы поискового движка по заданному вопросу.

    Args:
        request_text (str): текст вопроса
    return:
        (str): текст ответа.
    """
    print(f"Вызвана rag_web с параметром {request_text}")
    msg = "Ответ из интернета"
    return msg