"""Планировщик изначальной задачи"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.base import Runnable

from utils.function_calling.tool_functions.preparing_meeting.prompts import PLANER_PROMPT
from utils.function_calling.tool_functions.preparing_meeting.utils import Plan
from utils.function_calling.tool_functions.utils import get_model


def create_planner() -> Runnable:
    """
    Создает инстанс планировщика изначальных задач для выполнением агентом

    :return: Планировщик.
    """

    planner_prompt = ChatPromptTemplate.from_messages([("system", PLANER_PROMPT), ("placeholder", "{messages}")])
    planner = planner_prompt | get_model().with_structured_output(Plan)
    return planner
