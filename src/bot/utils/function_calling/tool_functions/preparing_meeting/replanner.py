"""Перепланировщик"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_gigachat.chat_models.gigachat import GigaChat
from langchain_openai import ChatOpenAI

from configs.config import giga_scope, giga_agent_model, giga_credentials
from utils.function_calling.tool_functions.preparing_meeting.config import API_KEY, BASE_URL, BASE_MODEL, AGENT_MODEL
from utils.function_calling.tool_functions.preparing_meeting.utils import Replan
from utils.function_calling.tool_functions.preparing_meeting.prompts import REPLANER_PROMPT


def create_replanner():
    replanner_prompt = ChatPromptTemplate.from_template(REPLANER_PROMPT)

    if AGENT_MODEL == 'gpt':
        replanner = replanner_prompt | ChatOpenAI(model=BASE_MODEL,
                                                  api_key=API_KEY,
                                                  base_url=BASE_URL,
                                                  max_tokens=5000,
                                                  temperature=0).with_structured_output(Replan)
    elif AGENT_MODEL == 'giga':
        replanner = replanner_prompt | GigaChat(verbose=True,
                                                credentials=giga_credentials,
                                                scope=giga_scope,
                                                model=giga_agent_model,
                                                verify_ssl_certs=False,
                                                profanity_check=False,
                                                temperature=0.00001).with_structured_output(Replan)
    else:
        raise Exception('Wrong agent model type ')
    return replanner
