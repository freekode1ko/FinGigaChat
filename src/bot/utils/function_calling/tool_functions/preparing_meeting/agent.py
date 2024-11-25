"""Инициализация сущности самого агента"""

from langchain import hub
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from utils.function_calling.tool_functions.preparing_meeting.config import API_KEY, BASE_URL, BASE_MODEL
from utils.function_calling.tool_functions.preparing_meeting.prompts import BASE_PROMPT#from utils.function_calling.tool_functions.call_report.run import get_call_report
#from utils.function_calling.tool_functions.cib_info.run import get_cib_info
#from utils.function_calling.tool_functions.rag.run import get_rag_answer
#from utils.function_calling.tool_functions.recomendation.run import get_recomendation
#from utils.function_calling.tool_functions.summarization.run import get_summarization


def create_agent():
    prompt = hub.pull("ih/ih-react-agent-executor")
    prompt.messages[0].prompt.template = BASE_PROMPT

    tool_functions_prepare_for_meeting = []
    # tool_functions_prepare_for_meeting = [get_summarization,
    #                                      get_cib_info,
    #                                      get_rag_answer,
    #                                      get_recomendation,
    #                                      get_call_report]

    llm = ChatOpenAI(model=BASE_MODEL,
                     api_key=API_KEY,
                     base_url=BASE_URL,
                     temperature=0)

    llm_with_tools = llm.bind_tools(tool_functions_prepare_for_meeting, parallel_tool_calls=False)

    agent_executor = create_react_agent(llm_with_tools, tool_functions_prepare_for_meeting, state_modifier=prompt)
    return agent_executor
