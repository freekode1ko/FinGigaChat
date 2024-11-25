from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

@tool
async def get_cib_reports_by_name(name: str, config: RunnableConfig):
    msg = f'CIB отчеты по {name}. Сейчас что-то происходит'
    return msg