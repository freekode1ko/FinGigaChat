"""Тулза для маппинга клиентов и отраслей"""

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

@tool
async def get_industry_by_client_name(text: str, config: RunnableConfig) -> str:
    """Возвращает отрасль клиента по его названию

    Args:
        text (str): название клиента в именительном падеже
    return:
        (str): Отрасль клиента
    """
    return ''
