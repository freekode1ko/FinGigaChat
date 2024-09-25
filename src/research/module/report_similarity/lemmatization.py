"""Модуль приведения текста в нормальную форму."""
from pymorphy3 import MorphAnalyzer

from configs.config import STATIC_DATA_PATH
from utils.utils import read_file_lines


class Lemmatization:
    """Лемматизация текста (перевод в нормальную форму)."""

    def __init__(self):
        self.morph = MorphAnalyzer()
        self.stop_words_list = read_file_lines(STATIC_DATA_PATH / 'base_stop_words_list.txt')

    def lemma_text(self, original_text: str) -> str:
        """
        Лемматизация текста и удаление не нужных слов.

        :param original_text:   Оригинальный текст новости.
        :return:                Лемматизированный текст.
        """
        normal_words = []
        for word in original_text.lower().split():
            if word:
                normal_word = self.morph.parse(word)[0].normal_form
                if normal_word not in self.stop_words_list:
                    normal_words.append(normal_word)
        return ' '.join(normal_words)
