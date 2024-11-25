"""Тулза по получению отчета для подготовки ко встречи"""

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool


# from utils.function_calling.tool_functions.cib_info.run import get_cib_reports_by_name
# from utils.function_calling.tool_functions.product.run import get_product_recomendation
# from utils.function_calling.tool_functions.rag.run import rag_news, rag_web, rag_cib
# from utils.function_calling.tool_functions.summarization.run import get_news_by_name

from utils.function_calling.tool_functions.preparing_meeting.config import EXECUTION_CONFIG
from utils.function_calling.tool_functions.preparing_meeting.graph_executable import create_graph_executable
from utils.function_calling.tool_functions.preparing_meeting.prompts import INITIAL_QUERY

agent_graph = create_graph_executable()


# TODO: разобраться, как прокидывать (и нужно ли?) треды
# TODO: поменять для принты для дебага на нормальное логирование
# TODO: сделать обработку исключений
# TODO: Вообще на тестах он как-то не всегда формирвал в последнем сообщении итоговый отчет, возможно есть смысл отдельно еще раз его формировать уже по истории сообщений от модели в процессе исполнения


@tool
async def get_preparing_for_meeting(client_name: str, runnable_config: RunnableConfig) -> str:
    """Если пользователь просит помощи и не понимает что делать, то эта функция отправляет ему сообщение с руководством.

    Args:
        client_name (str): Название компании клиента в именительном падеже с маленькой буквы.
        runnable_config (RunnableConfig): Конфиг.
    return:
        (str): Сформированный отчет для встречи менеджера с клиентом.
    """

    cnt = 1
    result = ''
    inputs = {"input": INITIAL_QUERY.format(company_name=client_name)}
    async for event in agent_graph.astream(inputs, config=EXECUTION_CONFIG):
        for k, v in event.items():
            if k != "__end__":
                if cnt == 1:
                    print(f"Запрос пользователя: {inputs['input']}")
                    print("Составленный план:")
                    print(v['plan'])
                    print()
                print(f'Шаг {cnt}')
                cnt += 1
                if 'plan' in v:
                    print(v['plan'])
                    if len(v['plan']) > 0:
                        print(v['plan'][0])
                if 'past_steps' in v:
                    if len(v['past_steps']) > 0:
                        print(v['past_steps'][0][1])
                if 'response' in v:
                    result = v['response']
                    print(f"Итоговый ответ: {v['response']}")
                print()
    return result



