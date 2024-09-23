import asyncio
import urllib.parse

from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse

from configs.config import LOG_FILE, LOG_LEVEL, N_NARROW_ANSWER, N_WIDE_ANSWER
from configs.prompts import DEFAULT_ANSWER
from log.logger_base import selector_logger
from retriever import Chain

app = FastAPI()

logger = selector_logger(LOG_FILE, LOG_LEVEL)
engine = Chain(logger)


@app.get('/aquery')
async def aanswer(query: str = Query(min_length=2)) -> PlainTextResponse:
    """
    Формирование ответа на запрос с помощью интернет ретривера

    """
    query = urllib.parse.unquote(query)
    tasks = [
        engine.aanswer_chain(query, N_WIDE_ANSWER),
        engine.aanswer_chain(query, N_NARROW_ANSWER)
    ]
    answers = await asyncio.gather(*tasks)
    final_answer = next(filter(lambda x: x not in [DEFAULT_ANSWER], answers), DEFAULT_ANSWER)
    engine.logger.info(f"Обработан запрос: {query}, с ответом: {final_answer}")
    return PlainTextResponse(content=''.join(map(str, final_answer)))
