import urllib.parse

from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse

from configs.config import LOG_FILE, LOG_LEVEL
from log.logger_base import selector_logger
from retriever import WebRetriever

app = FastAPI()

logger_app = selector_logger(LOG_FILE, LOG_LEVEL)
engine = WebRetriever(logger_app)


@app.get('/aquery')
async def aanswer(query: str = Query(min_length=2)) -> PlainTextResponse:
    """
    Формирование ответа на запрос с помощью интернет ретривера в обычном формате.

    """
    query = urllib.parse.unquote(query)
    final_answer = await engine.aget_answer(query)
    engine.logger.info(f"Обработан запрос: {query}, с ответом: {final_answer}")
    return PlainTextResponse(content=''.join(map(str, final_answer)))


@app.get('/aquery_tg')
async def aanswer_tg(query: str = Query(min_length=2)) -> PlainTextResponse:
    """
    Формирование ответа на запрос с помощью интернет ретривера с форматированием ссылок для Telegram.

    """
    query = urllib.parse.unquote(query)
    final_answer = await engine.aget_answer(query, output_format="tg")
    engine.logger.info(f"Обработан запрос: {query}, с ответом: {final_answer}")
    return PlainTextResponse(content=''.join(map(str, final_answer)))
