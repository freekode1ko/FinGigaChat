from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool


@tool
async def get_news_by_name(name: str, config: RunnableConfig):
    msg = f'Новости по: {name}. Что-то произошло, а что-то не произошло'
    return msg
