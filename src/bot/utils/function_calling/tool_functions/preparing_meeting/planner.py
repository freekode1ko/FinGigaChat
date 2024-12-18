"""Планировщик изначальной задачи"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_gigachat.chat_models.gigachat import GigaChat
from langchain_openai import ChatOpenAI

from configs.config import giga_scope, giga_agent_model, giga_credentials, giga_model
from utils.function_calling.tool_functions.preparing_meeting.config import API_KEY, BASE_URL, BASE_MODEL, AGENT_MODEL
from utils.function_calling.tool_functions.preparing_meeting.prompts import PLANER_PROMPT
from utils.function_calling.tool_functions.preparing_meeting.utils import Plan


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
    if AGENT_MODEL == 'gpt':
        planner = planner_prompt | ChatOpenAI(model=BASE_MODEL,
                                              api_key=API_KEY,
                                              base_url=BASE_URL,
                                              max_tokens=5000,
                                              temperature=0).with_structured_output(Plan)
    elif AGENT_MODEL == 'giga':
        planner = planner_prompt | GigaChat(verbose=True,
                                            credentials=giga_credentials,
                                            scope=giga_scope,
                                            model=giga_model,  # TODO: вставить giga_agent_model, но пока падает 500 код
                                            verify_ssl_certs=False,
                                            profanity_check=False,
                                            temperature=0.00001).with_structured_output(Plan)
    else:
        raise Exception('Wrong agent model type')
    return planner
