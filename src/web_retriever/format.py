"""Форматирование сырого ответа от GigaChat"""

import re
from urllib.parse import urlparse

from configs.config import N_LINKS_AFTER_TOPIC, N_LINKS_AFTER_ANSWER
from configs.text_constants import DEFAULT_ANSWER, USELESS_FRASES, SOURCES_PATTERN

pattern = re.compile(r'(</a>)(?!\n\n)(\s*[^,])')


def is_contain_link(answer: str) -> bool:
    """
    Проверяет, сформировал ли GigaChat ответ со ссылками.

    :param answer:        Отформатированный ответ GigaChat.
    :return:              Флаг наличия ссылки в ответе.
    """
    return '<a href=' in answer


def make_short_link(link: str) -> str:
    """
    Формирует короткую версию ссылки в формате html.

    :param link:     Ссылка.
    :return:         Ссылка в разметке html.
    """
    url = urlparse(link)
    base_url = url.netloc.split('www.')[-1]
    return f'<a href="{link}">{base_url}</a>' if base_url else link


def change_sources_format(answer: str, leave_amount: int = N_LINKS_AFTER_TOPIC) -> str:
    """
    Изменяет все ссылки на нужный формат и оставляеть leave_amount, если ссылок слишком много.

    :param answer:               Ответ от GigaChat.
    :param leave_amount:         Количество ссылок, которое нужно оставить
    :return:                     Строка из ссылок в разметке html.
    """
    sources = re.sub(pattern=SOURCES_PATTERN, repl=r'\1', string=answer)
    sources_list = sources.split(', ')
    return ', '.join(
        short_link for source in sources_list[0:leave_amount]
        if (short_link := make_short_link(source))
    )


def make_format_msg(answer: str) -> str:
    """
    Формирует ответ со ссылками для передачи его в Telegram.

    :param answer:               Ответ от RAG.
    :return:                     Ответ со ссылками в html разметке.
    """
    return re.sub(
        pattern=SOURCES_PATTERN, repl=lambda x: change_sources_format(x.group()), string=answer
    )


def make_format_msg_with_sources_in_end(answer: str,
                                        sources: list[str],
                                        leave_amount: int = N_LINKS_AFTER_ANSWER) -> str:
    """
    Формирует ответ для передачи его в Telegram, релевантные ссылки находятся в конце сообщения.

    :param answer:              Ответ, сгенерированный GigaChat (не содержит ссылок).
    :param sources:             Список ссылок на источники.
    :param leave_amount:        Количество ссылок, которые оставляем.
    :return:                    Ответ со ссылками в html разметке (в конце сообщения).
    """
    format_sources = ', '.join(
            short_link for source in sources[0:leave_amount]
            if (short_link := make_short_link(source))
    )
    return answer + format_sources


def clear_answer(answer: str) -> str:
    """
    Очистка текста от лишних фраз.

    :param answer: Ответ от RAG.
    :return:       Очищенный текст.
    """
    for frase in USELESS_FRASES:
        answer = answer.replace(frase, '')
    return answer


def add_paragraphs(answer: str) -> str:
    """
    Добавить в ответ абзацы после ссылок.

    :param answer: Отформатированный ответ от GigaChat.
    :return:       Отформатированный с абзацами ответ от GigaChat.
    """
    result = pattern.sub(r'\1\n\n\2', answer)
    return result.replace('\n\n ', '\n\n')


def clear_from_sources(answer: str) -> str:
    """
    Очистка ответа от ссылок.

    :param answer:  Ответ от LLM.
    :return:        Ответ без ссылок.
    """
    return clear_answer(re.sub(pattern=SOURCES_PATTERN, repl='', string=answer))


def format_answer(answer: str, sources: list[str]) -> str:
    """
    Очистка ответа от ссылок.

    :param answer:  Ответ от LLM.
    :param sources: Список ссылок на источники.
    :return:        Ответ без ссылок.
    """
    if answer == DEFAULT_ANSWER:
        return answer

    processed_answer = make_format_msg(answer)
    processed_answer = clear_answer(processed_answer)
    if is_contain_link(processed_answer):
        return re.sub(r'\n+', '\n\n', add_paragraphs(processed_answer).strip()).strip()
    answer = clear_answer(answer)
    return re.sub(r'\n+', '\n\n', make_format_msg_with_sources_in_end(answer, sources)).strip()
