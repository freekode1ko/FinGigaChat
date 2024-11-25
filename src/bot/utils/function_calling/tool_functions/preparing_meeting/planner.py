"""Планировщик изначальной задачи"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from utils.function_calling.tool_functions.preparing_meeting.config import API_KEY, BASE_URL, BASE_MODEL
from utils.function_calling.tool_functions.preparing_meeting.prompts import PLANER_PROMPT
from utils.function_calling.tool_functions.preparing_meeting.utils import Plan

# TODO: переписать промпты


def create_planner():
    planner_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                PLANER_PROMPT,
            ),
            ("placeholder", "{messages}"),
        ]
    )

    planner = planner_prompt | ChatOpenAI(model=BASE_MODEL,
                                          api_key=API_KEY,
                                          base_url=BASE_URL,
                                          temperature=0).with_structured_output(Plan)
    return planner
