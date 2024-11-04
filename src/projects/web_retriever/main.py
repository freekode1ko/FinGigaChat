"""API сервиса web_retriever"""

import uvicorn
from fastapi import FastAPI

from configs.config import LOG_FILE, LOG_LEVEL, PORT
from configs.text_constants import DEFAULT_ANSWER
from log.logger_base import selector_logger
from retriever import WebRetriever, RagResponse, Question

app = FastAPI()

logger_app = selector_logger(LOG_FILE, LOG_LEVEL)
engine = WebRetriever(logger_app)


@app.post('/api/v1/question', response_model=RagResponse)
async def aanswer_tg(query: Question) -> RagResponse:
    """
    Формирование ответа на запрос с помощью интернет ретривера с форматированием ссылок для Telegram.

    """
    try:
        final_answer = await engine.aget_answer(query.body, output_format="tg")
        final_answer = final_answer[0]
        logger_app.info(f"На запрос {query.body} получен ответ: {final_answer}")
    except Exception as e:
        logger_app.error(f"Не получен ответ на запрос {query.body} по причине: {e}")
        final_answer = DEFAULT_ANSWER
    return RagResponse(body=final_answer)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
