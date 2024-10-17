import logging
import sys
import time

import pandas as pd

from config_evaluation import EVALUATION_DATASET_PATH, N_ATTEMPTS

sys.path.append('../')
from retriever import WebRetriever


async def get_answers(engine: WebRetriever, logger: logging.Logger, filepath: str = EVALUATION_DATASET_PATH) -> None:
    """
    Составляет ответы на вопросы из целевого датасета и сохраняет его в excel таблицу в файл "result_chain.xlsx"

    :param: logger. Логгер.
    :param: filepath. Путь к файлу с вопросами.
    """
    df = pd.read_excel(filepath)
    start_time = time.time()
    results = []
    formatted_results = []
    for question in df['query']:
        flag = False
        for i in range(N_ATTEMPTS):
            try:
                ans = await engine.aget_answer(question, debug=True)
                results.append(ans[0])
                formatted_results.append(ans[1])
                flag = True
                logger.info(f"Обработан запрос: {question}, с ответом: {results[-1]}")
                break
            except Exception as e:
                logger.error(str(e))
        if not flag:
            results.append("Не удалось получить ответ.")

    df['answers'] = results
    df['formatted_answers'] = formatted_results
    df.to_excel('result_chain.xlsx')
    logger.info("---Elapsed time %s seconds ---" % (time.time() - start_time))
