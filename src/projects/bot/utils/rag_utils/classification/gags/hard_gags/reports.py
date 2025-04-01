"""Модуль с заглушками-отчетами"""
import os
import subprocess
import tempfile
from pathlib import Path

from aiogram import Bot, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import over

from configs import config
from constants.constants import DEFAULT_RAG_ANSWER
from constants.quotes.const import ReportParameter
from constants.texts import texts_manager
from db.api.research import research_db
from db.models import Research, ResearchResearchType, ResearchType
from db.user import get_user
from keyboards.analytics.constructors import get_few_full_research_kb
from log.bot_logger import logger
from module import formatter
from utils.watermark import add_watermark_cli


async def get_file_with_watermark(session: AsyncSession, chat_id: int, filepath: str | Path):
    """Сформировать файл с вотермаркой."""
    user = await get_user(session, chat_id)
    user_anal_filepath = Path(tempfile.gettempdir()) / f'{os.path.basename(filepath)}_{chat_id}_watermarked.pdf'
    try:
        add_watermark_cli(
            filepath,
            user_anal_filepath,
            user.user_email,
        )
    except subprocess.SubprocessError as e:
        logger.error(f'*{user.user_id}* При рассылке отчета {filepath} произошла ошибка: {e}.')
    else:
        return types.FSInputFile(user_anal_filepath)


async def send_currency_market_anal_reports(bot: Bot, chat_id: int, session: AsyncSession, ):
    """Отправка отчетов по валютному рынку."""
    row_number_column = over(
        func.row_number(),
        partition_by=ResearchType.name,
        order_by=desc(Research.publication_date)
    ).label('rn')
    ranked_research = (
        select(Research.id, Research.header, row_number_column)
        .join(ResearchResearchType, ResearchResearchType.research_type_id == ResearchType.id)
        .join(Research, Research.id == ResearchResearchType.research_id)
        .where(ResearchType.name.in_([
            'Прогноз валютного рынка на месяц',
            'Ежемесячный обзор по мягким валютам',
            'Ежемесячный обзор по юаню'
        ]))
    ).subquery()
    results = await session.execute(
        select(ranked_research.c.id, ranked_research.c.header)
        .where(ranked_research.c.rn <= 1)
    )

    reports_data = [
        {'header': report_header, 'research_id': report_id}
        for report_id, report_header in results.fetchall()
    ]
    await bot.send_message(
        chat_id,
        text=texts_manager.CURRENCY_MARKET_ANALYTICS,
        reply_markup=get_few_full_research_kb(InlineKeyboardBuilder(), reports_data),
        protect_content=texts_manager.PROTECT_CONTENT
    )
    return texts_manager.CURRENCY_MARKET_ANALYTICS + f' Кнопки:{[r["header"] for r in reports_data]}'


async def send_weekly_pulse(bot: Bot, chat_id: int, session: AsyncSession):
    """Отправить отчет викли пульс (pdf)"""
    path_to_dir = config.PATH_TO_SOURCES / 'weeklies'
    pdf_files = list(path_to_dir.glob('*.pdf'))
    weekly_path = None
    if len(pdf_files) == 1:
        weekly_path = pdf_files[0]
    elif len(pdf_files) > 1:
        weekly_path = max(pdf_files, key=lambda f: f.stat().st_mtime)

    if weekly_path and (file := await get_file_with_watermark(session, chat_id, weekly_path)):
        await bot.send_document(
            chat_id=chat_id,
            document=file,
            caption=texts_manager.INVESTMENT,
            parse_mode='HTML',
            protect_content=texts_manager.PROTECT_CONTENT,
        )
        return texts_manager.INVESTMENT
    return DEFAULT_RAG_ANSWER


async def send_eco_research_reports(bot: Bot, chat_id: int, session: AsyncSession):
    """Отправить экономические отчеты по России."""
    reports_parameters = [
        ReportParameter(
            section_name='Экономика РФ',
            type_name='Экономика РФ',
            condition=Research.header.ilike('%экономика россии. ежемесячный обзор%'),
        ),
        ReportParameter(
            section_name='Экономика РФ',
            type_name='Экономика РФ',
            condition=Research.header.notilike('%ежемесячный%'),
            count=3
        ),
    ]

    return_text = ''
    for data in reports_parameters:
        data = data.dict()
        reports = await research_db.get_report_by_parameters(session, data)

        if reports and not return_text:
            return_text += texts_manager.MACRO_ANALYTICS
            await bot.send_message(chat_id, return_text)

        for report in reports:
            format_text = formatter.ResearchFormatter.format(report)
            return_text += f'\n{format_text}'
            await bot.send_message(
                chat_id, text=format_text,
                protect_content=texts_manager.PROTECT_CONTENT, parse_mode='HTML'
            )

            if report.filepath and os.path.exists(report.filepath):
                if file := await get_file_with_watermark(session, chat_id, report.filepath):
                    await bot.send_document(
                        chat_id=chat_id,
                        document=file,
                        caption=report.header,
                        parse_mode='HTML',
                        protect_content=texts_manager.PROTECT_CONTENT,
                    )
    return return_text
