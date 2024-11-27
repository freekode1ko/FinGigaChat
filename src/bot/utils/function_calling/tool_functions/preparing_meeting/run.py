"""Тулза по получению отчета для подготовки ко встречи"""

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

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
    """Если пользователь просит составить отчет по подготовке ко встречи, создает отчет и возвращает ему его.
    Примеры того, как могут выглядеть сообщения пользователя, для которых нужно вызывать эту функцию:
    "Составь отчет для встречи с ..." / "Сделай отчет ко встречи с ..." / "Подготовка ко встрече с ...."

    Args:
        client_name (str): Название компании клиента в именительном падеже с маленькой буквы.
        runnable_config (RunnableConfig): Конфиг.
    return:
        (str): Сформированный отчет для встречи менеджера с клиентом.
    """
    print(f"Вызвана функция подготовки ко встречи с параметром {client_name}")
    cnt = 1
    result = ''
    try:
        inputs = {"input": INITIAL_QUERY.format(client_name=client_name)}
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
    except Exception as e:
        print(e)
    return result



