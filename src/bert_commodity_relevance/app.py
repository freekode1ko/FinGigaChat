import urllib.parse

from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse
from ruRoberta import load_model, predict

roberta, tokenizer = load_model()

app = FastAPI()


@app.get('/query')
async def answer(query: str = Query(min_length=2)) -> PlainTextResponse:
    """Формирование предсказания по запросу."""

    query = urllib.parse.unquote(query)
    probs = await predict(query, roberta, tokenizer)
    return PlainTextResponse(content=':'.join(map(str, probs)))
