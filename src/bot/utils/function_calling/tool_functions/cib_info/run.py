from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

@tool
async def get_cib_reports_by_name(name: str, config: RunnableConfig):
    """Возвращает пользователю текст с отчетами из источника "CIB аналитика" по компании по заданному названию компании.

    Args:
        name (str): только название компании в именительном падеже.
    return:
        (str): Текст с отчетами по компании.
    """

    msg = f'CIB отчеты по {name}. Сейчас что-то происходит'
    return msg