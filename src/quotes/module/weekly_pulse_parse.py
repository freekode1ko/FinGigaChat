# importing required modules
import os
import re
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Iterable, List, Optional, Union

import fitz
import pandas

__all__ = ['ParsePresentationPDF', 'ReportTypes']


HEADER_MAX_LEN = 256
PERCENT_HEIGHT_OF_USEFUL_INFO = 94


def default_slide_item() -> dict:
    return {
        'page_number': -1,
        'text': '',
        'table': None,
    }


def crop_slide_text(text: str) -> str:
    if not isinstance(text, str):
        return ''

    splited_text = text.split('\n')
    return '\n'.join(splited_text[2:-5]) if len(splited_text) > 7 else text


def __crop_text_upto_header(text: str) -> str:
    return text[:HEADER_MAX_LEN]


def __is_needed_slide_inner(criteria: str, slide_text: str) -> bool:
    if not re.search(criteria.lower(), slide_text.lower()):
        return False
    return True


def is_needed_slide(criteria: str, slide_text: str) -> bool:
    try:
        return __is_needed_slide_inner(criteria, __crop_text_upto_header(slide_text))
    except Exception:
        pass
    return False


def get_page_table(
    pdf_file: str, page_number: Union[str, int], area: Optional[Union[list, tuple]] = None, relative_area: bool = False
) -> Optional[pandas.DataFrame]:
    return None
    # try:
    #     import tabula  # pip install tabula-py
    # except ImportError:
    #     return None
    #
    # try:
    #     tables = tabula.read_pdf(pdf_file, pages=page_number, area=area, relative_area=relative_area)
    # except FileNotFoundError:  # IF NOT JAVA INSTALLED OR JAVA_HOME IS NOT SET
    #     return None
    #
    # return tables[0] if tables else None


def get_special_slides(filename: str, slides_meta: Union[List[dict], Iterable[dict]]) -> defaultdict:
    slides_titles2data = defaultdict(default_slide_item)

    if not filename or not isinstance(filename, (str, Path)) or not os.path.isfile(filename) or not slides_meta:
        return slides_titles2data

    slides_meta = [i.copy() for i in slides_meta if isinstance(i, dict)]  # make a list, that copy slide_meta

    with fitz.open(filename) as pdf_file:
        for page_num, page in enumerate(pdf_file):
            # extracting text from page in natural reading order
            text = page.get_text(sort=True)

            for i, slide_meta in enumerate(slides_meta):
                title = slide_meta['title']

                if not is_needed_slide(title, text):
                    continue

                slides_titles2data[title]['page_number'] = page_num
                slides_titles2data[title]['text'] = crop_slide_text(text)  # crop some first and some last lines

                if slide_meta.get('table', False):
                    slides_titles2data[title]['table'] = get_page_table(
                        filename, page_num + 1, slide_meta.get('area', None), slide_meta.get('relative_area', False)
                    )

                slides_meta.pop(i)
                break
    return slides_titles2data


class ReportTypes(Enum):
    """Типы отчетов для пользователя по weekly pulse"""

    weekly_results = 0
    weekly_event = 1


class ParsePresentationPDF:
    """Обрабатывает файл презентации weekly pulse в pdf формате"""

    @staticmethod
    def get_slides_meta() -> List[dict]:
        """
        Возвращает мета-информацию о слайдах, которые вынимаются из презентации weekly_pulse
        Мета-информация содержит следующий набор данных:

        title: Заголовок слайда, используется в качестве критерия для определения номера слайда
        eng_name: название слайда на английском, используется для сохранения слайда в виде png
        crop: флаг необходимости обрезки сохраненного изображения
        report_type: тип отчетной информации, используется для группировки слайдов при выдаче пользователю (data_transfer)
        table: флаг указания наличия таблицы на слайде
        Optional[area]: область слайда, которая содержит таблицу (top, left, bottom, right)
        Optional[relative_area]: флаг указания, что area указывает область в процентах (True) или в абсолютных единицах (False)
        return: list[dict] список словарей с мета-информацией по каждому слайду
        """
        special_slides_meta = [
            {
                'title': 'Основные события недели',
                'eng_name': 'week_results',
                'crop': False,
                'crop_params': {},
                'sub_images': [],
                'report_type': ReportTypes.weekly_results,
                'table': False,
            },
            {
                'title': 'Пульс рынка',
                'eng_name': 'rialto_pulse',
                'crop': True,
                'crop_params': {'left': 70, 'top': 40, 'right': 1350, 'bottom': 1290},
                'sub_images': [],
                'report_type': ReportTypes.weekly_results,
                'table': False,  # True
                'area': (15, 0, 90, 50),  # top, left, bottom, right in %
                'relative_area': True,
            },
            {
                'title': 'Следите за важным',
                'eng_name': 'important_events',
                'crop': False,
                'crop_params': {},
                'sub_images': [],
                'report_type': ReportTypes.weekly_event,
                'table': False,
            },
            {
                'title': 'Прогноз валютных курсов',
                'eng_name': 'exc_rate_prediction',
                'crop': False,
                'crop_params': {},
                'sub_images': [
                    {
                        'name': 'exc_rate_prediction_table',
                        'relative': True,
                        'crop_params': {'left': 0, 'top': 0.15, 'right': 0.5, 'bottom': 0.9},
                    },
                    {
                        'name': 'key_rate_dynamics_table',
                        'relative': True,
                        'crop_params': {'left': 0.5, 'top': 0.15, 'right': 1, 'bottom': 0.8},
                    },
                ],
                'report_type': ReportTypes.weekly_event,
                'table': False,  # True
                'area': (15, 0, 90, 100),
                'relative_area': True,
            },
        ]
        return special_slides_meta

    @classmethod
    def get_fnames_by_type(cls, report_type=None) -> List[str]:
        """
        Возвращает список названий слайдов, сохраненных в виде png, для определенного типа report_type

        :param report_type: тип из Types
        return: List[str]
        """
        s_meta = cls.get_slides_meta()
        return [f"{i['eng_name']}.png" for i in s_meta if i['report_type'] == report_type]

    @staticmethod
    def parse_table(
        pdf_file: str, page_number: Union[str, int], area: Optional[Union[list, tuple]] = None, relative_area: bool = False
    ) -> Optional[pandas.DataFrame]:
        """
        Возвращает найденную на слайде первую таблицу

        :param pdf_file: Имя презентации с расширением pdf
        :param page_number: Номер слайда (int, str)
        :param area: Область нахождения таблицы (по умолчанию весь слайд)
        :param relative_area: Флаг указания, что область area в процентах
        return: None или DataFrame с табличными данными со слайда
        """
        try:
            return get_page_table(pdf_file, page_number, area, relative_area)
        except Exception:
            pass

        return None

    def parse(self, filename: str, slides_meta: Optional[Union[List[dict], Iterable[dict]]] = None) -> defaultdict:
        """
        Возвращает словарь, где ключом является заголовок слайда, а по заголовку содержится информация:

        page_number: номер слайда с заданным заголовком int, -1 если не найден
        text: текст слайда str
        table: таблица со слайда DataFrame или None
        :param filename: Путь к файлу, который необходимо распарсить
        :param slides_meta: Мета информация вынимаемых слайдов
        return: defaultdict[str: dict]
        """
        if not slides_meta:
            slides_meta = self.get_slides_meta()

        try:
            return get_special_slides(filename, slides_meta)
        except Exception:
            pass

        return defaultdict(default_slide_item)
