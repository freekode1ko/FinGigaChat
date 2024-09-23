import asyncio
import logging
import sys
import time

import pandas as pd

from config_evaluation import EVALUATION_DATASET_PATH, N_ATTEMPTS

sys.path.append('../')
from retriever import Chain
from configs.config import N_WIDE_ANSWER, N_NARROW_ANSWER
from configs.prompts import DEFAULT_ANSWER


async def get_answers(engine: Chain, logger: logging.Logger, filepath: str = EVALUATION_DATASET_PATH) -> None:
    """
    Составляет ответы на вопросы из целевого датасета и сохраняет его в excel таблицу в файл "result_chain.xlsx"
    :param: logger. Логгер.
    :param: filepath. Путь к файлу с вопросами.

    """
    df = pd.read_excel(filepath)
    start_time = time.time()
    results = []
    for question in df['query']:
        flag = False
        for i in range(N_ATTEMPTS):
            try:
                tasks = [
                    engine.aanswer_chain(question, 8),
                    engine.aanswer_chain(question, 5),
                    engine.aanswer_chain(question, 2)
                ]
                answers = await asyncio.gather(*tasks)
                results.append(next(filter(lambda x: x not in [DEFAULT_ANSWER], answers), DEFAULT_ANSWER))
                flag = True
                break
            except Exception as e:
                logger.error(e)
        logger.info(f"Обработан запрос: {question}, с ответом: {results[-1]}")
        if not flag:
            results.append("Не удалось получить ответ.")

    df['answers'] = results
    df.to_excel('result_chain.xlsx')
    logger.info("---Elapsed time %s seconds ---" % (time.time() - start_time))
