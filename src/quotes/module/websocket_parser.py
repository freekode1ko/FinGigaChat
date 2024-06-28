"""Парсера курсов валют на вебсокете"""

import json
import time

from websockets.sync.client import connect


def create_submessage(id_: int, info: int, quotes_list_json: str) -> dict:
    """
    Сформировать данные для рукопожатия по определенному шаблону.

    :param id_:                 Какое-то числовое значение.
    :param info:                Доп инфа для рукопожатия.
    :param quotes_list_json:    Полезная нагрузка с id запрашиваемого курса валюты.
    :return:                    Данные для рукопожатия.
    """
    return {
        '1': id_,
        '2': info,
        '3': quotes_list_json,
        '11': time.time(),
    }


def create_handshake_message_finam(data_key: str, submessages_data: list[dict[str, int | str]]) -> str:
    """
    Создать сообщения для рукопожатия.

    Сообщение имеет определенную структуру и хранит id получемого значения

    :param data_key:            Ключ, по которому лежат данные для рукопожатия
    :param submessages_data:    Формируемые данные для рукопожатия
    :return:                    json.dumps сообщение с данными для рукопожатия
    """
    data = [create_submessage(**data) for data in submessages_data]
    return json.dumps({data_key: data})


def parse_by_params(params: dict[str, str | int | list[dict], list[str | int]]) -> float | None:
    """
    Спарсить данные при подключении по вебсокету по параметрам.

    :param params:  Хранит uri сервера, параметры парсинга
    :return:        Полученное значение или None
    """
    with connect(params['url']) as websocket:
        accept_messages_handshake = params['accept_messages_handshake']
        for i in range(accept_messages_handshake):
            websocket.recv()
        for message in params['send_messages']:
            websocket.send(create_handshake_message_finam(message['data_key'], message['data']))
            websocket.recv()

        for _ in range(params['max_recv_messages']):
            message = websocket.recv()
            data = json.loads(message)
            if data[params['message_type_key']] == params['searched_message_type']:
                break

        try:
            data = json.loads(data[params['exchange_list_key']])
        except Exception as e:
            print('error, ', e)
            return

        for i in params['exchange_data_keys']:
            data = data[i]
        return data
