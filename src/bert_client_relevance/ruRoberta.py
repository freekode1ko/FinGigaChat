from transformers import RobertaForSequenceClassification, AutoTokenizer
from config import MODEL_PATH, LOG_LEVEL, LOG_FILE
from log.logger_base import selector_logger
import torch

logger = selector_logger(LOG_FILE, LOG_LEVEL)

logger.info('Загрузка модели с Huggingface')

Roberta = RobertaForSequenceClassification.from_pretrained(MODEL_PATH)
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

logger.info('Модель загружена')

MAX_INPUT_LENGTH = 512


async def get_prediction_cpu(text: str) -> list[float]:
    """
    Получаем вероятности от модели принадлежности текста новости релевантости или нерелевантности.
    :param text: текст новости
    :return: вероятности от модели
    """
    try:
        # токенизируем и обрезаем текст новости до максимального входа
        inputs = tokenizer(text, padding=True, truncation=True, max_length=MAX_INPUT_LENGTH, return_tensors="pt")
        # получаем предсказания модели
        with torch.no_grad():
            outputs = Roberta(**inputs)
        # достаем вероятности из логитов
        probs = outputs[0].softmax(1)
        # возвращаем вероятности
        results = list(probs.detach().numpy()[0])
        logger.info("Получены вероятности: " + str(results) + ". Новость: " + text)
    except Exception as e:
        logger.error("Ошибка при получении вероятностей: " + str(e))
        results = [-1, -1]
    return results


async def get_prediction_batch_cpu(texts: list[str], batch_size: int = 4) -> list[list[float]]:
    """
    TODO: Переписать обработку текстов по батчам, с учетом нормального паддинга. Пока работает не совсем корректно
    Получаем вероятности от модели принадлежности текстов новостей релевантости или нерелевантности.
    :param texts: список текстов новостей.
    :param batch_size: размер батча
    :return: вероятности от модели для каждой новости в формате строки вида: 'prob1_0:prob1_1;prob2_0:prob2_1'
    """
    try:
        # токенизируем и обрезаем текст новости до максимального входа
        inputs = torch.tensor([tokenizer.encode(text, padding='max_length', truncation=True,
                                         max_length=MAX_INPUT_LENGTH, add_special_tokens=True) for text in texts])
    except Exception as e:
        logger.error("Ошибка при токенизации: " + str(e))
        return [[-1, -1] for _ in range(len(texts))]
    try:
        # получаем предсказания модели
        probs = []
        with torch.no_grad():
            # разбиваем тексты на батчи и получаем предсказания для каждого батча
            for i in range(0, len(texts), batch_size):
                batch = inputs[i: min(i + batch_size, len(texts)), :]
                outputs = Roberta(batch)
                probs += [outputs.logits[j, :].softmax(0) for j in range(len(batch))]
        # возвращаем вероятности
        results = [list(prob.detach().numpy()) for prob in probs]
        logger.info("Обработан батч размера " + str(len(results)) + ". Результаты: " + str(results))
    except Exception as e:
        logger.error("Ошибка при получении вероятностей: " + str(e))
        results = [[-1, -1] for _ in range(len(texts))]
    return results
