"""Функции для создания слайда с текстом вотермарки и наложения вотермарки на pdf файлы."""

import io
from pathlib import Path

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

from constants.texts import texts_manager


def create_watermark(
        text: str,
        font_type: str = texts_manager.FONT_TYPE,
        font_size: int = texts_manager.FONT_SIZE,
        rotation: int = texts_manager.ROTATION,
) -> PdfReader:
    """
    Создать слайд с вотермаркой из переданного текста.

    :param text:        Текст вотермарки
    :param font_type:   Шрифт
    :param font_size:   Размер шрифта
    :param rotation:    Угол наклона текста вотермарки
    :return:            Объект чтения pdf файла с вотермаркой
    """
    word_spacing = texts_manager.WORD_SPACING
    line_spacing = texts_manager.LINE_SPACING
    lines_cnt = texts_manager.LINES_COUNT
    pagesize = texts_manager.PAGE_SIZE
    word_in_line_cnt = texts_manager.WORD_IN_LINE_COUNT
    font_color_alpha = texts_manager.FONT_COLOR_ALPHA  # коэф прозрачности

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=pagesize)

    text_line = ' '.join(text for _ in range(word_in_line_cnt))
    text_object = c.beginText()
    text_object.setLeading(line_spacing)
    text_object.setWordSpace(word_spacing)

    c.setFont(font_type, font_size)
    c.setFillGray(0.5, font_color_alpha)  # Устанавливаем серый цвет
    c.saveState()
    c.translate(-pagesize[0], pagesize[1])
    c.rotate(rotation)

    for indent in range(lines_cnt):
        text_object.textLine(text_line)
    c.drawText(text_object)

    c.restoreState()
    c.save()

    packet.seek(0)
    return PdfReader(packet)


def add_watermark(
        input_pdf: Path | str,
        output_pdf: Path | str,
        watermark_text: str,
        font_type: str = texts_manager.FONT_TYPE,
        font_size: int = texts_manager.FONT_SIZE,
        watermark_text_rotation: int = texts_manager.ROTATION,
):
    """
    Добавить вотермарку к pdf файлу.

    :param input_pdf:                    Путь к файлу, к которому надо добавить вотермарку
    :param output_pdf:             Путь сохранения файла с вотермаркой
    :param watermark_text:              Текст вотермарки
    :param font_type:                   Шрифт текста
    :param font_size:                   Размера шрифта
    :param watermark_text_rotation:     Угол наклона текста
    """
    pdf_reader = PdfReader(input_pdf)
    pdf_writer = PdfWriter()
    watermark = create_watermark(watermark_text, font_type, font_size, watermark_text_rotation)

    for page_number in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_number]
        watermark_page = watermark.pages[0]
        page.merge_page(watermark_page)
        pdf_writer.add_page(page)

    with open(output_pdf, 'wb') as output_file:
        pdf_writer.write(output_file)
