"""Модуль с заглушкой по отраслям."""
from pathlib import Path

from aiogram import Bot, types
from langchain_core.messages import HumanMessage

from constants.constants import DEFAULT_RAG_ANSWER
from constants.texts import texts_manager
from db.api.industry import get_industry_analytic_files, industry_db
from keyboards.analytics.industry import callbacks
from log.bot_logger import logger
from module.llm_langchain import giga
from utils.base import send_pdf

INDUSTRY_PROMPT = """\
Ты работаешь аналитиком экономических отраслей. Тебе будет дан вопрос. 
Твоя задача - определить к какому классу относится вопрос. 
Есть следующие классы:
{categories}

Напиши, к какому классу можно отнести вопрос.
В ответе нужно предоставить только соответсвующее классу число!

Вопрос: {question}
"""  # noqa:W291

EXTRA_INDUSTRY_INFO = {
    'промышленность': 'промышленность (химическая, фармацевтика, лесная, удобрения)',
    'нефть и газ': 'нефть и газ (производство, поставки)',
    'сельское хозяйство': 'сельское хозяйство (агропромышленность, пищевая промышленность)'
}

OTHER_INDUSTRY = 'прочее'


async def prepare_categories_for_prompt() -> dict[int, str]:
    """Сформировать словарь из отраслей для внесения в промпт."""
    categories = await industry_db.get_all()
    categories = categories.to_dict(orient='records')
    categories = {category['id']: category['name'].lower().strip() for category in categories}
    for id_, industry in categories.items():
        if new_info := EXTRA_INDUSTRY_INFO.get(industry):
            categories[id_] = new_info
    categories[0] = OTHER_INDUSTRY
    categories = dict(sorted(categories.items()))
    logger.debug(f'Отформатированные категории: {categories}')
    return categories


async def get_industry_id_from_question(question: str) -> int | None:
    """Получить id отрасли из вопроса."""
    categories = await prepare_categories_for_prompt()
    content = INDUSTRY_PROMPT.format(categories=categories, question=question)
    giga_answer = await giga.ainvoke([HumanMessage(content), ])
    try:
        industry_id = int(giga_answer) or None  # чтобы вместо 0 (прочего) вернулось None
        logger.info(f'Ответ от GigaChat: {giga_answer}, определенный ID: {industry_id}')
        return industry_id
    except (TypeError, ValueError, SyntaxError) as e:
        logger.error(f'Ошибка при преобразовании id отрасли от GigaChat "{giga_answer}": {e}')


def get_industry_type(industry_id: int):
    """Получить тип отрасли по id."""
    return callbacks.IndustryTypes.default if industry_id else callbacks.IndustryTypes.general_comments


async def send_industry_report(question: str, bot: Bot, message: types.Message) -> str:
    """Отправить отчет(ы) по отрасли(ям), указанных в вопросе."""
    industry_id = await get_industry_id_from_question(question)
    industry_type = get_industry_type(industry_id)
    industry_info = await industry_db.get(industry_id) if industry_id else {'name': OTHER_INDUSTRY}
    logger.debug(f'Получена информация об отрасли: {industry_info}')

    files = await get_industry_analytic_files(industry_id, industry_type)
    files = [p for f in files if (p := Path(f.file_path)).exists()]

    if files:
        logger.info(f'Найдено {len(files)} отраслевых отчетов')
        text = f'{texts_manager.INDUSTRY_ANALYTICS} <b>{industry_info["name"].capitalize()}</b>'
        if await send_pdf(message, files, text, protect_content=texts_manager.PROTECT_CONTENT):
            return text

    logger.info('Файлы не найдены, отправка стандартного ответа')
    await bot.send_message(message.chat.id, text=DEFAULT_RAG_ANSWER)
    return DEFAULT_RAG_ANSWER
