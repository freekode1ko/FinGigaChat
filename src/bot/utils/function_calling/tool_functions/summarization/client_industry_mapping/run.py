"""Тулза для маппинга клиентов и отраслей"""

import pandas as pd
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from db.database import engine
from utils.function_calling.tool_functions.preparing_meeting.config import DEBUG_GRAPH


def create_client_industry_dict() -> dict:
    """
    Создает словарь с названиями индустрий клиента.

    :return: Словарь индустрий клиентов.
    """
    query = (
        'select industry.name as industry_name, client.name as client_name from client '
        'join industry on client.industry_id = industry.id'
    )
    df = pd.read_sql(query, engine)
    df.index = df['client_name'].str.lower().str.strip()
    client_industry_dict = df['industry_name'].to_dict()
    return client_industry_dict


CLIENT_INDUSTRY_MAPPING = create_client_industry_dict()


@tool
async def get_industry_by_client_name(text: str, config: RunnableConfig) -> str:
    """Возвращает отрасль клиента по его названию

    Args:
        text (str): название клиента в именительном падеже
    return:
        (str): Отрасль клиента
    """
    if DEBUG_GRAPH:
        print(f'Вызвана функция get_industry_by_client_name с параметром: {text}')
    try:
        client_industry = CLIENT_INDUSTRY_MAPPING[text.lower().strip()]
        return client_industry
    except Exception as e:
        print(e)
        return "Ошибка при получении отрасли клиента."
