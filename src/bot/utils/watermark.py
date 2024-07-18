"""Функции для создания слайда с текстом вотермарки и наложения вотермарки на pdf файлы."""

import io
import subprocess
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

    packet = io.BytesIO()   # Файл будет буффере памяти (но можно сделать создание и проверку, что файл есть или нет)
    c = canvas.Canvas(packet, pagesize=pagesize)  # Создаем картинку размеров pagesize

    text_line = ' '.join(text for _ in range(word_in_line_cnt))  # Создаем строку, которая будет записываться на картинку
    text_object = c.beginText()  # Создает текстовый объект, который позволяет записывать множество строк на картинку
    text_object.setLeading(line_spacing)  # установка расстояния между строк
    text_object.setWordSpace(word_spacing)  # установка расстояния между слов в строке

    c.setFont(font_type, font_size)  # Установка шрифта
    c.setFillGray(0.5, font_color_alpha)  # Устанавливаем серый цвет и его прозрачность
    c.saveState()
    c.translate(-pagesize[0], pagesize[1])  # Установка стартовой точки, откуда текст начнет записываться на картинку
    c.rotate(rotation)  # Установка угла наклона текста (весь блок текста будет повернут относительно стартовой точки записи)

    # Запись строк текста на картинку
    for indent in range(lines_cnt):
        text_object.textLine(text_line)
    c.drawText(text_object)

    c.restoreState()
    c.save()

    # Возвращаемся в начало файла, чтоб pdfreader считал файл с самого начала
    packet.seek(0)
    return PdfReader(packet)


def add_watermark(
        input_pdf: Path | str,
        output_pdf: Path | str,
        watermark_text: str,
        font_type: str = texts_manager.FONT_TYPE,
        font_size: int = texts_manager.FONT_SIZE,
        watermark_text_rotation: int = texts_manager.ROTATION,
) -> None:
    """
    Добавить вотермарку к pdf файлу.

    :param input_pdf:               Путь к файлу, к которому надо добавить вотермарку
    :param output_pdf:              Путь сохранения файла с вотермаркой
    :param watermark_text:          Текст вотермарки
    :param font_type:               Шрифт текста
    :param font_size:               Размера шрифта
    :param watermark_text_rotation: Угол наклона текста
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


def add_watermark_cli(
        input_pdf: str | Path,
        output_pdf: str | Path,
        watermark: str,
        font_type: str = texts_manager.FONT_TYPE,
        font_size: int = texts_manager.FONT_SIZE,
        rotation: int = texts_manager.ROTATION,
        lines_count: int = texts_manager.VERTICAL_REPETITIONS,
        word_in_line_count: int = texts_manager.HORIZONTAL_REPETITIONS,
        opacity: float = texts_manager.FONT_COLOR_ALPHA,
) -> None:
    """
    Добавить вотермарку к pdf файлу.

    Работает быстрее, удобнее, но запускается из командной строки (надо проверить работу в рамках контейнера).

    :param input_pdf:               Путь к файлу, к которому надо добавить вотермарку
    :param output_pdf:              Путь сохранения файла с вотермаркой
    :param watermark:               Текст вотермарки
    :param font_type:               Шрифт текста
    :param font_size:               Размера шрифта
    :param rotation: Угол наклона текста
    :param lines_count:             Кол-во строк на странице с вотермаркой
    :param word_in_line_count:      Кол-во повторений слова в строке
    :param opacity:                 Прозрачность текста
    """
    cmd = [
        'watermark',
        'grid',
        '-s', str(output_pdf),
        '-tf', str(font_type),
        '-ts', str(font_size),
        '-a', str(rotation),
        '-h', str(lines_count),
        '-v', str(word_in_line_count),
        '-o', str(opacity),
        str(input_pdf),
        watermark,
    ]

    try:
        subprocess.call(cmd)
    except subprocess.SubprocessError as e:
        print(f'Error: {e}')
