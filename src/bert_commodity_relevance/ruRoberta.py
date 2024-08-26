import torch
from config import LOG_FILE, LOG_LEVEL, MODEL_PATH
from log.logger_base import selector_logger
from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer

logger = selector_logger(LOG_FILE, LOG_LEVEL)

MAX_INPUT_LENGTH = 512

N_ATTEMPTS = 5


def load_model() -> tuple[ORTModelForSequenceClassification, AutoTokenizer]:
    """
    Обработчик ошибки загрузки модели.
    :return: Загруженная модель и токенайзер.
    """

    logger.info('Старт загрузки модели с HuggingFace')
    for _ in range(N_ATTEMPTS):
        try:
            model = ORTModelForSequenceClassification.from_pretrained(MODEL_PATH)
            tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
            logger.info('Модель загружена')
            return model, tokenizer
        except Exception as e:
            logger.info(f'Ошибка загрузки модели с Huggingface: {e}')


async def predict(text: str, model: ORTModelForSequenceClassification, tokenizer: AutoTokenizer) -> list[float]:
    """
    Получаем вероятности от модели принадлежности текста новости релевантости или нерелевантности.
    :param text: текст новости
    :param model: модель
    :param tokenizer: токенизатор
    :return: вероятности от модели
    """

    try:
        # Обрезаем текст до максимальной длины символов и токенизируем его
        inputs = tokenizer(text, padding=True, truncation=True, max_length=512, return_tensors='pt')
        # Получаем предсказания модели
        with torch.inference_mode():
            outputs = model(**inputs)
        # Достаем вероятности из логитов
        probs = outputs[0].softmax(1)
        # Возвращаем вероятности
        results = list(probs.detach().numpy()[0])
        logger.info(f'Получены вероятности: {results}. Новость: {text}')
    except Exception as e:
        logger.error(f'Ошибка при получении вероятностей: {e}')
        results = [-1, -1]
    return results
