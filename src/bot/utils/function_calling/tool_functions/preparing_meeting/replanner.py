"""Перепланировщик"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from utils.function_calling.tool_functions.preparing_meeting.config import API_KEY, BASE_URL, BASE_MODEL
from utils.function_calling.tool_functions.preparing_meeting.utils import Act
from utils.function_calling.tool_functions.preparing_meeting.prompts import REPLANER_PROMPT


def create_replanner():
    replanner_prompt = ChatPromptTemplate.from_template(REPLANER_PROMPT)

    replanner = replanner_prompt | ChatOpenAI(model=BASE_MODEL,
                                              api_key=API_KEY,
                                              base_url=BASE_URL,
                                              max_tokens=100000,
                                              temperature=0).with_structured_output(Act)
    return replanner
