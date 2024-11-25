"""Тулза по получению отчета для подготовки ко встречи"""

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from utils.function_calling.tool_functions.preparing_meeting.config import EXECUTION_CONFIG
from utils.function_calling.tool_functions.preparing_meeting.graph_executable import create_graph_executable

agent_graph = create_graph_executable()


# TODO: разобраться, как прокидывать (и нужно ли?) треды
# TODO: поменять для принты для дебага на нормальное логирование
# TODO: сделать нормальное прокидывание название компании и оборачивать его в отдельный промпт
# TODO: сделать обработку исключений
# TODO: Вообще на тестах он как-то не всегда формировал в последнем сообщении итоговый отчет, возможно есть смысл отдельно еще раз его формировать уже по истории сообщений от модели в процессе исполнения


@tool
async def get_preparing_for_meeting(client_name: str, runnable_config: RunnableConfig) -> str:
    """Функция по подготовке отчета по компании. Используй тогда, когда поступает сообщение от пользователя в виде:
    'Помоги подготовиться ко встрече с клиентом ...'/'Подготовка ко встрече с компанией ...'/
    'Сформируй отчет ко встрече с ...'

    Args:
        client_name (str): Название компании клиента в именительном падеже с маленькой буквы.
    return:
        (str): сообщение с руководством.
    """
    print('Вызвана функция подготовки ко встречи')
    cnt = 1
    result = ''
    inputs = {
        "input": f"У менеджера встреча к компанией-клиентом {client_name}. Помоги ему подготовиться ко встрече и собери по ней информационную сводку, твой итоговый ответ быть именно этой информационной сводкой. Включи туда последние события по компании и предложи на основании этого банковские продукты применительно к этим ситациям (кредиты, лизинг и тд)"}
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



