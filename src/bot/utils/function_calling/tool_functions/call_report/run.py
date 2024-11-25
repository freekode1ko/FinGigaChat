from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

@tool
async def get_call_reports_by_name(name: str, config: RunnableConfig):
    """Возвращает текст с историей взаимодействия пользователя с данным клиентом.

    Args:
        name (str): название клиента в именительном падеже
    return:
        (str): суммаризованный текст предыдущих взаимодействий с пользователем.
    """
    pass