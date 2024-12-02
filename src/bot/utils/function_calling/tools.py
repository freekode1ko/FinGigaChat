"""Функции для запуска function calling"""
from aiogram import types
from langchain_gigachat.chat_models import GigaChat
from langgraph.prebuilt import create_react_agent
import traceback

from constants.enums import FeatureType
from utils.decorators import has_access_to_feature
from utils.function_calling.tool_functions import tools_functions
from utils.function_calling.tool_functions.utils import LanggraphConfig


@has_access_to_feature(feature=FeatureType.admin, is_need_answer=False)
async def find_and_run_tool_function(message: types.Message, message_text: str) -> bool:
    """Функция вызывающая реализующая функционал function calling

    :param message_text: Текст по которому будет вызываться функция
    :param message:      Объект сообщения из aiogram, для взаимодействия с пользователем

    :return:             Вызвалась ли функция
    """
    giga = GigaChat(base_url='https://gigachat-preview.devices.sberbank.ru/api/v1/',
                    verbose=True,
                    credentials="YTQwNDJmMTUtYTY5NS00NTc3LTkxZmMtOTA4MTlkMTNjMGRiOmQxMWMyYzI1LTdlMzQtNGViNC1hYjMyLWQ0NDk5ODhiNmY1NA==",
                    scope='GIGACHAT_API_CORP',
                    model='GigaChat-Max-preview',
                    verify_ssl_certs=False,
                    profanity_check=False,
                    temperature=0.00001
                    )

    langgraph_agent_executor = create_react_agent(giga, tools_functions)
    conf = LanggraphConfig(message=message)

    try:
        res = await langgraph_agent_executor.ainvoke(
            {'messages': [('user', message_text)]},
            conf.config_to_langgraph_format(),
        )
        # Функция завершилась с ошибкой
        if res['messages'][2].status == 'error':
            print(res['messages'])
            return False
        # Проверка есть ли вызов функции в ответе от модели
        return 'function_call' in res['messages'][1].additional_kwargs

    except Exception as e:
        print(e)
        print(traceback.format_exc())
        # Случаи когда не смогли достучаться до модели или ошибки langgraph-gigachat
        return False
