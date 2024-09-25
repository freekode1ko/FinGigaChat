"""Модуль для определения ближайшего похожего отчета."""
import math
import numpy as np
from collections import Counter
from typing import ClassVar


class BM25:
    """Класс для определения ближайшего похожего отчета."""
    # регулирует, насколько частота термина в документе влияет на его релевантность
    # 0 - частота термина не будет влиять на результат, увеличение k1 - влияние частоты термина возрастает
    K1: ClassVar[float] = 1.5
    # регулирует влияние длины документа
    # 0 - длина документа не учитывается, 1 - длинные документы будут иметь меньшую релевантность
    B: ClassVar[float] = 0.75

    def __init__(self, documents: list[str]):
        self.documents = documents
        self.doc_lengths = [len(doc.split()) for doc in documents]
        self.avg_doc_length = np.mean(self.doc_lengths)
        self.N = len(documents)
        self.doc_freqs = []

        # Вычисление частот терминов по каждому документу
        for doc in documents:
            freq = Counter(doc.split())
            self.doc_freqs.append(freq)

        # Вычисление общей частоты терминов во всех документах
        self.term_doc_freq = {}
        for freq in self.doc_freqs:
            for term in freq:
                if term not in self.term_doc_freq:
                    self.term_doc_freq[term] = 0
                self.term_doc_freq[term] += 1

    def bm25_score(self, report_text: str, index: int) -> float:
        """
        Расчет балла схожести для отчета.

        :param report_text: Текст отчета.
        :param index:       Его индекс в списке.
        :return:            Балл схожести
        """
        score = 0
        doc_freq = self.doc_freqs[index]
        doc_len = self.doc_lengths[index]

        for term in report_text.split():
            if term in doc_freq:
                # Частота термина в документе
                term_freq_in_doc = doc_freq[term]
                # Общее число документов, содержащих этот термин
                doc_freq_with_term = self.term_doc_freq.get(term, 0)
                idf = math.log((self.N - doc_freq_with_term + 0.5) / (doc_freq_with_term + 0.5) + 1)
                score += idf * ((term_freq_in_doc * (self.K1 + 1)) /
                                (term_freq_in_doc + self.K1 * (1 - self.B + self.B * (doc_len / self.avg_doc_length))))
        return score

    def search(self, report_text: str) -> tuple[int, float]:
        """
        Поиск ближайшего похожего отчета.

        :param report_text: Текст отчета.
        :return: Tuple[индекс балла схожести (самого подходящего отчета), балл схожести]
        """
        scores = [self.bm25_score(report_text, i) for i in range(self.N)]
        return np.argmax(scores), max(scores)
