"""Перепланировщик"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.base import Runnable

from agent_app import logger
from utils.tool_functions.preparing_meeting.prompts import REPLANER_PROMPT
from utils.tool_functions.preparing_meeting.utils import Replan
from utils.tool_functions.utils import get_model


def create_replanner() -> Runnable:
    """
    Перепланировщик оставщихся задач для выполнения итоговой цели в процессе исполнения графа.

    :return: Инстанс перепланировщика.
    """
    replanner_prompt = ChatPromptTemplate.from_template(REPLANER_PROMPT)
    replanner = replanner_prompt | get_model().with_structured_output(Replan)
    logger.info('Инициализирован репланировщик')
    return replanner
