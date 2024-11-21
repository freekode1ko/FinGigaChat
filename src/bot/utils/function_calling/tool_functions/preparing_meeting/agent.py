"""Инициализация сущности самого агента"""

from langchain import hub
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from config import API_KEY, BASE_URL, BASE_MODEL
from prompts import BASE_PROMPT
from utils.function_calling.tool_functions import tool_functions_prepare_for_meeting

prompt = hub.pull("ih/ih-react-agent-executor")
prompt.messages[0].prompt.template = BASE_PROMPT

llm = ChatOpenAI(model=BASE_MODEL,
                 api_key=API_KEY,
                 base_url=BASE_URL,
                 temperature=0)

llm_with_tools = llm.bind_tools(tool_functions_prepare_for_meeting, parallel_tool_calls=False)

agent_executor = create_react_agent(llm_with_tools, tool_functions_prepare_for_meeting, state_modifier=prompt)
