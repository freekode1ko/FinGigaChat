# importing required modules
import os
import re

from collections import defaultdict
from pathlib import Path
from typing import List, Union, Iterable, Optional

import fitz
import pandas

from module.logger_base import Logger

__all__ = ['ParsePDF']


HEADER_MAX_LEN = 256


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


def get_page_table(pdf_file: str, page_number: Union[str, int], area: Optional[Union[list, tuple]] = None,
                   relative_area: bool = False) -> Optional[pandas.DataFrame]:
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


def get_special_slides(filename: str, slides_titles: Union[List[dict], Iterable[dict]]) -> defaultdict:
    slides_titles_data = defaultdict(default_slide_item)

    if not filename or not isinstance(filename, (str, Path)) or not os.path.isfile(filename) or not slides_titles:
        return slides_titles_data

    slides_titles = [i.copy() for i in slides_titles if isinstance(i, dict)]  # make a list, that copy titles

    with fitz.open(filename) as pdf_file:
        for page_num, page in enumerate(pdf_file):
            # extracting text from page in natural reading order
            text = page.get_text(sort=True)

            for i, slide_meta in enumerate(slides_titles):
                title = slide_meta['title']

                if not is_needed_slide(title, text):
                    continue

                slides_titles_data[title]['page_number'] = page_num
                slides_titles_data[title]['eng_name'] = slide_meta['eng_name']
                slides_titles_data[title]['text'] = crop_slide_text(text)  # crop some first and some last lines

                if slide_meta.get('table', False):
                    slides_titles_data[title]['table'] = get_page_table(filename, page_num + 1,
                                                                        slide_meta.get('area', None),
                                                                        slide_meta.get('relative_area', False))

                slides_titles.pop(i)
                break
    return slides_titles_data


class ParsePDF:

    @staticmethod
    def get_weekly_pulse_special_slides_meta() -> List[dict]:
        special_slides_meta = [
            {
                'title': 'Основные события недели',
                'eng_name': 'week_results',
                'crop': False,
                'table': False,
            },
            {
                'title': 'Пульс рынка',
                'eng_name': 'rialto_pulse',
                'crop': True,
                'table': False,  # True
                'area': (15, 0, 90, 50),  # top, left, bottom, right in %
                'relative_area': True,
            },
            {
                'title': 'Следите за важным',
                'eng_name': 'important_events',
                'crop': False,
                'table': False,
            },
            {
                'title': 'Прогноз валютных курсов',
                'eng_name': 'exc_rate_prediction',
                'crop': False,
                'table': False,  # True
                'area': (15, 0, 90, 100),
                'relative_area': True,
            },
        ]
        return special_slides_meta

    @staticmethod
    def get_page_table(pdf_file: str, page_number: Union[str, int], area: Optional[Union[list, tuple]] = None,
                       relative_area: bool = False) -> Optional[pandas.DataFrame]:
        try:
            return get_page_table(pdf_file, page_number, area, relative_area)
        except Exception:
            pass

        return None

    def get_special_slides(self, filename: str, slides_titles: Optional[Union[List[dict], Iterable[dict]]]) -> defaultdict:
        if not slides_titles:
            slides_titles = self.get_weekly_pulse_special_slides_meta()

        try:
            return get_special_slides(filename, slides_titles)
        except Exception:
            pass

        return defaultdict(default_slide_item)



