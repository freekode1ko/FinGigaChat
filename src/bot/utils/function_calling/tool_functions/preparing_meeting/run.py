"""Тулза по получению отчета для подготовки ко встречи"""
from aiogram import types
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_gigachat.chat_models.gigachat import GigaChat
from langchain_openai import ChatOpenAI


from configs.config import giga_scope, giga_model, giga_credentials
from constants import constants
from main import bot
from utils.function_calling.tool_functions.preparing_meeting.config import EXECUTION_CONFIG
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
    result_history = []
    tg_message: types.Message = runnable_config['configurable']['message']
    message_text = '-Начало формирования отчета\n\n'

    # text = """
    # <b>bold</b>, <strong>bold</strong>
    # <i>italic</i>, <em>italic</em>
    # <u>underline</u>, <ins>underline</ins>
    # <s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
    # <span class="tg-spoiler">spoiler</span>, <tg-spoiler>spoiler</tg-spoiler>
    # <b>bold <i>italic bold <s>italic bold strikethrough <span class="tg-spoiler">italic bold strikethrough spoiler</span></s> <u>underline italic bold</u></i> bold</b>
    # <a href="http://www.example.com/">inline URL</a>
    # <a href="tg://user?id=123456789">inline mention of a user</a>
    # <tg-emoji emoji-id="5368324170671202286">👍</tg-emoji>
    # <code>inline fixed-width code</code>
    # <pre>pre-formatted fixed-width code block</pre>
    # <pre><code class="language-python">pre-formatted fixed-width code block written in the Python programming language</code></pre>
    # <blockquote>Block quotation started\nBlock quotation continued\nThe last line of the block quotation</blockquote>
    # <blockquote expandable>Expandable block quotation started\nExpandable block quotation continued\nExpandable block quotation continued\nHidden by default part of the block quotation started\nExpandable block quotation continued\nThe last line of the block quotation</blockquote>
    # """
    # final_message = await tg_message.answer(text, parse_mode='HTML')
    final_message = await tg_message.answer(message_text + f'\n...', parse_mode='HTML')

    config = EXECUTION_CONFIG['configurable'] = {
        "message": tg_message,
        'buttons': [],
        'message_text': [message_text,],
        'final_message': final_message,
    }

    try:
        inputs = {"input": INITIAL_QUERY.format(client_name=client_name)}
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
                         temperature=0)
        result = await get_answer_giga(llm,
                                       FINAL_ANSWER_SYSTEM_PROMPT,
                                       FINAL_ANSWER_USER_PROMPT,
                                       '\n'.join(result_history))
        await final_message.edit_text(text=result)
        # TODO: напечатать пользователю итоговый ответ
        return result
    except Exception as e:
        await final_message.edit_text('Произошла ошибка: ' + result)
        await tg_message.answer(str(e))
        print(e)
    return result
