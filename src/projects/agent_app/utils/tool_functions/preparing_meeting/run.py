"""Тулза по получению отчета для подготовки ко встречи"""
import traceback

from aiogram import types
import asyncio
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from config import EXECUTION_CONFIG, MESSAGE_AGENT_START, \
    DEBUG_GRAPH, MAX_FAILURE_TOLERANCE
from utils.tool_functions.preparing_meeting.graph_executable import create_graph_executable
from utils.tool_functions.preparing_meeting.prompts import FINAL_ANSWER_SYSTEM_PROMPT, \
    FINAL_ANSWER_USER_PROMPT
from utils.tool_functions.preparing_meeting.prompts import INITIAL_QUERY
from utils.tool_functions.utils import get_answer_llm, get_model

agent_graph = create_graph_executable()


@tool
async def get_preparing_for_meeting(client_name: str, special_info: str, runnable_config: RunnableConfig) -> str:
    """Если пользователь просит составить отчет по подготовке ко встречи, создает отчет и возвращает ему его.
    Примеры того, как могут выглядеть сообщения пользователя, для которых нужно вызывать эту функцию:
    "Составь отчет для встречи с ..." / "Сделай отчет ко встречи с ..." / "Подготовка ко встрече с ...."

    Args:
        client_name (str): Название компании клиента в именительном падеже с маленькой буквы.
        special_info (str): Специальная доп информация, извлеченная из сообщения менеджера, о том, как должен быть сделан отчет. Если никакой спецификации в запросе нет, то вызови этот аргумент пустой строкой.
        runnable_config (RunnableConfig): Конфиг.
    return:
        (str): Сформированный отчет для встречи менеджера с клиентом.
    """
    if DEBUG_GRAPH:
        print(f"Вызвана функция подготовки ко встречи с параметрами: {client_name}, {special_info}")
    cnt = 1

    result = ''
    result_history = []
    states = []
    tg_message: types.Message = runnable_config['configurable']['message']

    message_text = MESSAGE_AGENT_START
    final_message = await tg_message.answer(message_text + f'...', parse_mode='HTML')
    buttons = []
    config = EXECUTION_CONFIG
    config['configurable'] = {
        "message": tg_message,
        'buttons': buttons,
        'message_text': [message_text],
        'final_message': final_message,
        "thread_id": f"{1}"  # TODO: добавить прокидывание нормального треда
    }

    try:
        inputs = {"input": INITIAL_QUERY.format(client_name=client_name, special_info=special_info)}
        failed_attempts = 0
        while failed_attempts < MAX_FAILURE_TOLERANCE:
            try:
                #print(config)
                if len(states) == 0:
                    astream = agent_graph.astream(inputs, config=config)
                else:
                    astream = agent_graph.astream(None, config=config)
                    print(states[-1].config)
                async for event in astream:
                    for node, graph_state in event.items():
                        states.append(agent_graph.get_state(config))
                        if node != "__end__":
                            if cnt == 1 and DEBUG_GRAPH:
                                print(f"Запрос пользователя: {inputs['input']}")
                                print("Составленный план:")
                                print(graph_state['plan'])
                                print()
                            if DEBUG_GRAPH:
                                print(f'Шаг {cnt}')
                            cnt += 1
                            if 'plan' in graph_state:
                                if len(graph_state['plan']) > 0:
                                    if DEBUG_GRAPH:
                                        print(graph_state['plan'][0])
                                        print(f"plan: {graph_state['plan'][0]}")
                                    result_history.append(graph_state['plan'][0])
                            if 'past_steps' in graph_state:
                                if len(graph_state['past_steps']) > 0:
                                    if DEBUG_GRAPH:
                                        print(f"past_steps: {graph_state['past_steps'][0][1]}")
                                    result_history.append(f"Выполненный шаг: {graph_state['past_steps'][0][1]}")
                            if 'response' in graph_state:
                                result = graph_state['response']
                                if DEBUG_GRAPH:
                                    print(f"Итоговый ответ: {graph_state['response']}")
            except Exception as e:
                print(traceback.format_exc())
                print(f'Ошибка: {e}')
                failed_attempts += 1
                await asyncio.sleep(1)
        if DEBUG_GRAPH:
            print(f"Логи действий для составления итогового ответа: {result_history}")
        llm = get_model()
        result = await get_answer_llm(llm,
                                      FINAL_ANSWER_SYSTEM_PROMPT.format(special_info=special_info),
                                      FINAL_ANSWER_USER_PROMPT,
                                      '\n'.join(result_history))
        try:
            first = True
            batches = slit_message(result)
            if DEBUG_GRAPH:
                print(batches)
            for batch in batches:
                if first:
                    await final_message.edit_text(text=batch, parse_mode='Markdown')
                    first = False
                    continue
                await tg_message.answer(text=batch, parse_mode='Markdown')

        except Exception as e:
            if DEBUG_GRAPH:
                print(f'Не смогло отправить финальное сообщение: {e}')
        try:
            for menu in buttons:
                await tg_message.answer(menu['message'], reply_markup=menu['keyboard'], parse_mode='HTML')
        except Exception as e:
            if DEBUG_GRAPH:
                print(f'Не смогло отправить финальное сообщение: {e}')
        return result
    except Exception as e:
        await final_message.edit_text('Произошла ошибка: ' + result)
        await tg_message.answer(str(e))
        if DEBUG_GRAPH:
            print(e)
            print(traceback.format_exc())

    return result
