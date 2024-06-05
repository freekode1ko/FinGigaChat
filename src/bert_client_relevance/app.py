import re
import urllib.parse

from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse

from ruRoberta import get_prediction_cpu, get_prediction_batch_cpu, load_model

roberta, tokenizer = load_model()

app = FastAPI()


@app.get('/query')
async def answer(query: str = Query(min_length=2)) -> PlainTextResponse:
    """Формирование предсказания модели на запрос с новостью."""

    query = urllib.parse.unquote(query)
    probs = await get_prediction_cpu(query, roberta, tokenizer)
    return PlainTextResponse(content=':'.join(map(str, probs)))


@app.get('/queries')
async def answer_batch(query: str = Query(min_length=2)) -> PlainTextResponse:
    """Формирование предсказания модели на запрос с батчем новостей"""

    queries = re.split(r';;', urllib.parse.unquote(query))
    probs = await get_prediction_batch_cpu(queries, roberta, tokenizer)
    return PlainTextResponse(content=';'.join(':'.join(map(str, prob)) for prob in probs))
