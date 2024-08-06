"""Доп функции для меню комодов."""
import sqlalchemy as sa
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from configs.config import PATH_TO_COMMODITY_REPORTS
from constants.enums import SubjectType
from db.models import Commodity, CommodityResearch
from log.bot_logger import logger
from module.article_process import ArticleProcess


async def send_or_get_commodity_quotes_message(
        message: types.Message,
        commodity_id: int,
        send: bool = True

) -> str | None:
    """
    Отправить или получить сообщение с котировками

    :param message:      Объект, содержащий в себе информацию по отправителю, чату и сообщению.
    :param commodity_id: Айди комода.
    :param send:         Отправить или получить.

    :return:             Строка с текстом сообщения.
    """
    ap_obj = ArticleProcess(logger)
    com_price, _ = await ap_obj.process_user_alias(commodity_id, SubjectType.commodity)
    if com_price:
        if not send:
            return com_price
        await message.answer(com_price, parse_mode='HTML', disable_web_page_preview=True)


async def send_anal_report(
        message: types.Message,
        commodity_id: int,
        session: AsyncSession,
) -> None:
    """
    Отправить аналитический отчет по комодам

    :param message:      Объект, содержащий в себе информацию по отправителю, чату и сообщению.
    :param commodity_id: Айди комода.
    :param session:      Асинхронная сессия базы данных.
    """
    result = await session.execute(
        sa.select(Commodity, CommodityResearch)
        .join(CommodityResearch, Commodity.id == CommodityResearch.commodity_id)
        .filter(Commodity.id == commodity_id)
    )
    commodity, commodity_research = result.all()[0]
    com_name = commodity.name.capitalize()
    title = commodity_research.title
    text = commodity_research.text
    file_name = commodity_research.file_name

    if not title:
        title = f'<b>Аналитика по {com_name}<b>'

    message_text = title + '\n\n' + text

    if file_name and (file_path := PATH_TO_COMMODITY_REPORTS / file_name).exists():
        file = types.FSInputFile(file_path)
        await message.answer_document(
            document=file,
            caption=message_text,
            parse_mode='HTML',
        )
        return

    await message.answer(message_text, parse_mode='HTML')
