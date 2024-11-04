"""Функция для суммаризации от chat gpt"""
from configs.prompts import SUMMARIZATION_PROMPT
from module.chatgpt import ChatGPT


def summarization_by_chatgpt(full_text: str):
    # TODO: do by langchain
    """Make summary by chatgpt"""
    batch_size = 4000
    text_batches = []
    new_text_sum = ''
    if len(full_text + SUMMARIZATION_PROMPT) > batch_size:
        while len(full_text + SUMMARIZATION_PROMPT) > batch_size:
            point_index = full_text[:batch_size].rfind('.')
            text_batches.append(full_text[: point_index + 1])
            full_text = full_text[point_index + 1:]
    else:
        text_batches = [full_text]
    for batch in text_batches:
        gpt = ChatGPT()
        query_to_gpt = gpt.ask_chat_gpt(text=batch, prompt=SUMMARIZATION_PROMPT)
        new_text_sum = new_text_sum + query_to_gpt.choices[0].message.content

    return new_text_sum
