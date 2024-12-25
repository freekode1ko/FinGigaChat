"""Тулза по получению отчета для подготовки ко встречи"""
import traceback

import asyncio

from agent_app import logger
from config import EXECUTION_CONFIG, MESSAGE_AGENT_START, MAX_FAILURE_TOLERANCE
from utils.tool_functions.preparing_meeting.graph_executable import create_graph_executable
from utils.tool_functions.preparing_meeting.prompts import FINAL_ANSWER_SYSTEM_PROMPT, \
    FINAL_ANSWER_USER_PROMPT
from utils.tool_functions.preparing_meeting.prompts import INITIAL_QUERY
from utils.tool_functions.utils import get_answer_llm, get_model

agent_graph = create_graph_executable()


async def get_preparing_for_meeting(client_name: str, special_info: str, user_id: str, thread_id: str) -> str:
    """Если пользователь просит составить отчет по подготовке ко встречи, создает отчет и возвращает ему его.
    Примеры того, как могут выглядеть сообщения пользователя, для которых нужно вызывать эту функцию:
    "Составь отчет для встречи с ..." / "Сделай отчет ко встречи с ..." / "Подготовка ко встрече с ...."

    Args:
        client_name (str): Название компании клиента в именительном падеже с маленькой буквы.
        special_info (str): Специальная доп информация, извлеченная из сообщения менеджера, о том, как должен быть сделан отчет. Если никакой спецификации в запросе нет, то вызови этот аргумент пустой строкой.
        user_id (str): ID пользователя.
        thread_id (str): ID нити исполнения.
    return:
        (str): Сформированный отчет для встречи менеджера с клиентом.
    """
    logger.info(f"Вызвана функция подготовки ко встречи с параметрами: {client_name}, {special_info}")
    cnt = 1
    result = ''
    result_history = []
    states = []
    config = EXECUTION_CONFIG
    config['configurable'] = {
        'name': client_name,
        'special_info': special_info,
        'user_id': user_id,
        'thread_id': thread_id
    }
    try:
        inputs = {"input": INITIAL_QUERY.format(client_name=client_name, special_info=special_info)}
        failed_attempts = 0
        while failed_attempts < MAX_FAILURE_TOLERANCE:
            try:
                if len(states) == 0:
                    astream = agent_graph.astream(inputs, config=config)
                else:
                    astream = agent_graph.astream(None, config=config)
                async for event in astream:
                    for node, graph_state in event.items():
                        states.append(agent_graph.get_state(config))
                        if node != "__end__":
                            if cnt == 1:
                                logger.info(f"Запрос пользователя: {inputs['input']}")
                                logger.info("Составленный план:")
                                logger.info(graph_state['plan'])
                            logger.info(f'Шаг {cnt}')
                            cnt += 1
                            if 'plan' in graph_state:
                                if len(graph_state['plan']) > 0:
                                    logger.info(graph_state['plan'][0])
                                    logger.info(f"plan: {graph_state['plan'][0]}")
                                    result_history.append(graph_state['plan'][0])
                            if 'past_steps' in graph_state:
                                if len(graph_state['past_steps']) > 0:
                                    logger.info(f"past_steps: {graph_state['past_steps'][0][1]}")
                                    result_history.append(f"Выполненный шаг: {graph_state['past_steps'][0][1]}")
                            if 'response' in graph_state:
                                result = graph_state['response']
                                logger.debug(f"Итоговый ответ: {graph_state['response']}")
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error(e)
                failed_attempts += 1
        logger.debug(f"Логи действий для составления итогового ответа: {result_history}")
        llm = get_model()
        result = await get_answer_llm(llm,
                                      FINAL_ANSWER_SYSTEM_PROMPT.format(special_info=special_info),
                                      FINAL_ANSWER_USER_PROMPT,
                                      '\n'.join(result_history))
        logger.info(f'Итоговый ответ: {result}')
        # TODO: возвращаем итоговый ответ
        return result
    except Exception as e:
        logger.error(traceback.format_exc())

    return result
