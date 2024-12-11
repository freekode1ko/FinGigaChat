"""Инициализация сущности самого агента"""

from langchain import hub
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from utils.function_calling.tool_functions.preparing_meeting.config import API_KEY, BASE_URL, BASE_MODEL
from utils.function_calling.tool_functions.preparing_meeting.prompts import BASE_PROMPT

from utils.function_calling.tool_functions.call_report.run import get_call_reports_by_name
from utils.function_calling.tool_functions.cib_info.run import get_analytical_reports_by_name
from utils.function_calling.tool_functions.product.run import get_product_recommendation
from utils.function_calling.tool_functions.rag.run import rag_news, rag_cib, rag_web
from utils.function_calling.tool_functions.summarization.run import get_news_by_name
from utils.function_calling.tool_functions.summarization.client_industry_mapping.run import get_industry_by_client_name

tool_functions_prepare_for_meeting = [
    get_call_reports_by_name,
    get_analytical_reports_by_name,
    rag_news,
    rag_cib,
    #rag_web,
    get_product_recommendation,
    get_news_by_name,
    get_industry_by_client_name
]


def create_agent():
    prompt = hub.pull("ih/ih-react-agent-executor")
    prompt.messages[0].prompt.template = BASE_PROMPT

    llm = ChatOpenAI(model=BASE_MODEL,
                     api_key=API_KEY,
                     base_url=BASE_URL,
                     max_tokens=100000,
                     temperature=0)

    llm_with_tools = llm.bind_tools(tool_functions_prepare_for_meeting, parallel_tool_calls=False)

    agent_executor = create_react_agent(llm_with_tools, tool_functions_prepare_for_meeting, state_modifier=prompt)
    return agent_executor
