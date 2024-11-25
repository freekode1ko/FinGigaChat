"""Тулза по получению отчета для подготовки ко встречи"""

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from config import EXECUTION_CONFIG
from graph_executable import app
from utils.function_calling.tool_functions.cib_info.run import get_cib_reports_by_name
from utils.function_calling.tool_functions.product.run import get_product_recomendation
from utils.function_calling.tool_functions.rag.run import rag_news, rag_web, rag_cib
from utils.function_calling.tool_functions.summarization.run import get_news_by_name


# TODO: разобраться, как прокидывать (и нужно ли?) треды
# TODO: поменять для принты для дебага на нормальное логирование
# TODO: сделать нормальное прокидывание название компании и оборачивать его в отдельный промпт
# TODO: сделать обработку исключений
# TODO: Вообще на тестах он как-то не всегда формирвал в последнем сообщении итоговый отчет, возможно есть смысл отдельно еще раз его формировать уже по истории сообщений от модели в процессе исполнения

# Pipeline
# News get_news_by_name
# CIB article get_reports_by_name
# Новостной раг
# Веб ретривер
# Раг ресерч
# Рекомендация продукта
#


@tool
async def get_preparing_for_meeting(runnable_config: RunnableConfig) -> str:
    """Если пользователь просит помощи и не понимает что делать, то эта функция отправляет ему сообщение с руководством.

    return:
        (str): сообщение с руководством.
    """
    name = 'Газпром'

    # Pipeline
    # News get_news_by_name
    await get_news_by_name(name, runnable_config)
    # CIB article get_reports_by_name
    await get_cib_reports_by_name(name, runnable_config)
    # Новостной раг
    await rag_news(name, runnable_config)
    # Веб ретривер
    await rag_web(name, runnable_config)
    # Раг ресерч
    await rag_cib(name, runnable_config)
    # Рекомендация продукта
    await get_product_recomendation(name, runnable_config)
    # CumReports

    cnt = 1
    result = ''
    inputs = {
        "input": "У менеджера встреча к компаниями-клиентами. Помоги ему подготовиться ко встрече и собери по ним информационную сводку, твой итоговый ответ быть именно этой информационной сводкой. Включи туда последние события по компаниям и предложи на основании этого банковские продукты применительно к этим ситациям (кредиты, лизинг и тд)"}
    async for event in app.astream(inputs, config=EXECUTION_CONFIG):
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



