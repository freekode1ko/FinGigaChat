"""Тулза для выдачи котировок по сырьевым товарам"""

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from handlers.commodity.utils import is_commodity_in_message
from utils.function_calling.tool_functions.utils import parse_runnable_config


@tool
async def get_commodity_quote(name: str | None, runnable_config: RunnableConfig) -> str:
    """Возвращает пользователю список котировку (цену) по заданному названию биржевого товара.

    Args:
        name (str): только название биржевого товара в именительном падеже.
    return:
        (str): Строка с ценой на интересующий биржевой товар.
    """
    runnable_config = parse_runnable_config(runnable_config)

    if not await is_commodity_in_message(runnable_config.message, name):
        raise Exception
