import re
import urllib.parse

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

from ruRoberta import get_prediction_cpu, get_prediction_batch_cpu

app = FastAPI()


@app.get('/query')
async def answer(query: str = Query(min_length=2)) -> HTMLResponse:
    """Формирование предсказания модели на запрос с новостью."""

    query = urllib.parse.unquote(query)
    probs = await get_prediction_cpu(query)
    return HTMLResponse(content=':'.join(map(str, probs)))


@app.get('/queries')
async def answer_batch(query: str = Query(min_length=2)) -> HTMLResponse:
    """Формирование предсказания модели на запрос с батчем новостей"""

    queries = re.split(r';;', urllib.parse.unquote(query))
    probs = await get_prediction_batch_cpu(queries)
    return HTMLResponse(content=';'.join(':'.join(map(str, prob)) for prob in probs))
