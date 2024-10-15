import urllib.parse

import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse, HTMLResponse

from configs.config import LOG_FILE, LOG_LEVEL, PORT
from configs.text_constants import DEFAULT_ANSWER
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
    try:
        query = urllib.parse.unquote(query)
        final_answer = await engine.aget_answer(query)
    except:
        final_answer = DEFAULT_ANSWER
    return PlainTextResponse(content=''.join(map(str, final_answer[0])))


@app.get('/aquery_tg')
async def aanswer_tg(query: str = Query(min_length=2)) -> PlainTextResponse:
    """
    Формирование ответа на запрос с помощью интернет ретривера с форматированием ссылок для Telegram.

    """
    query = urllib.parse.unquote(query)
    final_answer = await engine.aget_answer(query, output_format="tg")
    logger_app.info(final_answer[0])
    final_answer = final_answer[0]
    return PlainTextResponse(content=final_answer)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
