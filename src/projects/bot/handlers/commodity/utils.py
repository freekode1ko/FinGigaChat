"""Доп функции для меню комодов."""
import sqlalchemy as sa
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from configs.config import PATH_TO_COMMODITY_REPORTS
from constants import enums
from constants.enums import SubjectType
from constants.texts.texts_manager import texts_manager
from db import models
from db.api.commodity import commodity_db
from db.models import Commodity, CommodityResearch, RelationCommodityCommodityResearch
from handlers.commodity.keyboards import get_menu_kb as get_commodity_menu_kb
from log.bot_logger import logger
from module.article_process import ArticleProcess
from module.fuzzy_search import FuzzyAlternativeNames
from utils.decorators import has_access_to_feature


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
        .join(RelationCommodityCommodityResearch, RelationCommodityCommodityResearch.commodity_id == Commodity.id)
        .join(CommodityResearch, CommodityResearch.id == RelationCommodityCommodityResearch.commodity_research_id)
        .filter(Commodity.id == commodity_id)
    )
    if not len(result := result.all()):
        name = (
            await session.execute(
                sa.select(Commodity.name)
                .where(Commodity.id == commodity_id)
            )
        ).scalar().capitalize()
        await message.answer(
            f'На данный момент отчеты по "<b>{name}</b>" отсутствуют', parse_mode='HTML')
        return None
    for report in result:
        commodity, commodity_research = report
        com_name = commodity.name.capitalize()
        title = commodity_research.title
        text = commodity_research.text or ''
        file_name = commodity_research.file_name

        if not title:
            title = f'<b>Аналитический обзор по "{com_name}"</b>'

        message_text = title + '\n\n' + text

        if file_name and (file_path := PATH_TO_COMMODITY_REPORTS / file_name).exists():
            file = types.FSInputFile(file_path)
            await message.answer_document(
                document=file,
                caption=message_text,
                parse_mode='HTML',
            )
            continue

        await message.answer(message_text, parse_mode='HTML')


@has_access_to_feature(feature=enums.FeatureType.news, is_need_answer=False)
async def is_commodity_in_message(
        message: types.Message,
        user_msg: str,
        send_message_if_commodity_in_message: bool = True,
        fuzzy_score: int = 95,
) -> bool:
    """
    Является ли введенное сообщение стейкхолдером, и если да, вывод меню стейкхолдера или новостей.

    :param message: Сообщение от пользователя.
    :param user_msg: Сообщение пользователя
    :param send_message_if_commodity_in_message: нужно ли отправлять в сообщении
    :param fuzzy_score: Величина в процентах совпадение с референтными именами стейкхолдеров.
    :return: Булевое значение о том что совпадает ли сообщение с именем стейкхолдера.
    """
    commodity_ids = await FuzzyAlternativeNames().find_subjects_id_by_name(
        user_msg.replace(texts_manager.COMMODITY_ADDITIONAL_INFO, ''),
        subject_types=[models.CommodityAlternative, ],
        score=fuzzy_score
    )
    commodities = await commodity_db.get_by_ids(commodity_ids[:1])

    if len(commodities) >= 1:
        if send_message_if_commodity_in_message:
            commodity_id = commodity_ids[0]
            commodity_name = commodities['name'].iloc[0]
            await send_or_get_commodity_quotes_message(message, commodity_id)
            keyboard = get_commodity_menu_kb(commodity_id)
            msg_text = texts_manager.COMMODITY_CHOOSE_SECTION.format(name=commodity_name.capitalize())
            await message.answer(msg_text, reply_markup=keyboard, parse_mode='HTML')
        return True
    return False
