"""Тулза по получению отчета для подготовки ко встречи"""
from aiogram import types
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import traceback

from zmq.backend import first

from utils.base import slit_message
from utils.function_calling.tool_functions.preparing_meeting.config import EXECUTION_CONFIG, MESSAGE_AGENT_START
from utils.function_calling.tool_functions.preparing_meeting.config import API_KEY, BASE_URL, BASE_MODEL
from utils.function_calling.tool_functions.preparing_meeting.graph_executable import create_graph_executable
from utils.function_calling.tool_functions.preparing_meeting.prompts import INITIAL_QUERY
from utils.function_calling.tool_functions.preparing_meeting.prompts import FINAL_ANSWER_SYSTEM_PROMPT, \
    FINAL_ANSWER_USER_PROMPT
from utils.function_calling.tool_functions.utils import get_answer_giga

agent_graph = create_graph_executable()


# TODO: разобраться, как прокидывать (и нужно ли?) треды
# TODO: поменять для принты для дебага на нормальное логирование
# TODO: сделать обработку исключений


@tool
async def get_preparing_for_meeting(client_name: str, special_info: str, runnable_config: RunnableConfig) -> str:
    """Если пользователь просит составить отчет по подготовке ко встречи, создает отчет и возвращает ему его.
    Примеры того, как могут выглядеть сообщения пользователя, для которых нужно вызывать эту функцию:
    "Составь отчет для встречи с ..." / "Сделай отчет ко встречи с ..." / "Подготовка ко встрече с ...."

    Args:
        client_name (str): Название компании клиента в именительном падеже с маленькой буквы.
        special_info (str): Специальная доп информация, извлеченная из сообщения менеджера, о том, как должен быть сделан отчет.
        runnable_config (RunnableConfig): Конфиг.
    return:
        (str): Сформированный отчет для встречи менеджера с клиентом.
    """
    print(f"Вызвана функция подготовки ко встречи с параметрами: {client_name}, {special_info}")
    cnt = 1
    result = ''
    result_history = []
    tg_message: types.Message = runnable_config['configurable']['message']

    message_text = MESSAGE_AGENT_START
    final_message = await tg_message.answer(message_text + f'...', parse_mode='HTML')
    buttons = []
    config = EXECUTION_CONFIG['configurable'] = {
        "message": tg_message,
        'buttons': buttons,
        'message_text': [message_text,],
        'final_message': final_message,
    }

    try:
        inputs = {"input": INITIAL_QUERY.format(client_name=client_name, special_info=special_info)}
        async for event in agent_graph.astream(inputs, config=config):
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
                        # print(v['plan'])
                        if len(v['plan']) > 0:
                            print(v['plan'][0])
                            print(f"plan: {v['plan'][0]}")
                            result_history.append(v['plan'][0])
                    if 'past_steps' in v:
                        if len(v['past_steps']) > 0:
                            print(f"past_steps: {v['past_steps'][0][1]}")
                            result_history.append(f"Выполненный шаг: {v['past_steps'][0][1]}")
                    if 'response' in v:
                        result = v['response']
                        print(f"Итоговый ответ: {v['response']}")
                    print()

        print(f"Логи действий для составления итогового ответа: {result_history}")
        # TODO: так что могут быть баги/странное поведение
        #llm = GigaChat(base_url='https://gigachat-preview.devices.sberbank.ru/api/v1/',
        #               verbose=True,
        #               credentials=giga_credentials,
        #               scope=giga_scope,
        #               model=giga_model,
        #               verify_ssl_certs=False,
        #               profanity_check=False,
        #               temperature=0.00001
        #               )
        llm = ChatOpenAI(model=BASE_MODEL,
                         api_key=API_KEY,
                         base_url=BASE_URL,
                         max_tokens=100000,
                         temperature=0)
        result = await get_answer_giga(llm,
                                       FINAL_ANSWER_SYSTEM_PROMPT,
                                       FINAL_ANSWER_USER_PROMPT,
                                       '\n'.join(result_history))



        try:
            first = True
            batches = slit_message(result)
            print(batches)
            for batch in batches:
                if first:
                    await final_message.edit_text(text=batch, parse_mode='HTML')
                    first = False
                    continue
                await tg_message.answer(text=batch, parse_mode='HTML')

        except Exception as e:
            print('Не смогло отправить финальное сообщение')
            print(e)


        try:
            for menu in buttons:
                await tg_message.answer(menu['message'], reply_markup=menu['keyboard'], parse_mode='HTML')
        except:
            pass
        # TODO: напечатать пользователю итоговый ответ
        return result
    except Exception as e:
        await final_message.edit_text('Произошла ошибка: ' + result)
        await tg_message.answer(str(e))
        print(e)
        print(traceback.format_exc())

    return result
