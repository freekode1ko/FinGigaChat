import math
import re


class SentenceSplitter:

    sentence_end_characters = r'(\.\.\.)|(\. )|[!?]'

    @classmethod
    def split_text_by_sentences(cls, txt: str) -> list[str]:
        sentences = []
        sentence_start = 0
        for match_obj in re.finditer(cls.sentence_end_characters, txt):
            sentence_end = match_obj.end()
            sentences.append(txt[sentence_start: sentence_end])
            sentence_start = sentence_end
        return sentences

    @classmethod
    def split_text_by_chunks(cls, txt: str, chunk_size: int, delimiter: str = '\n\n') -> list[str]:
        if len(txt) < chunk_size:
            return [txt]

        chunks = []
        chunk = ''

        for paragraph in txt.split(delimiter):
            if len(paragraph) > chunk_size:
                sentences = cls.split_text_by_sentences(paragraph)

                for sentence in sentences:
                    if len(chunk) + len(sentence) > chunk_size:
                        chunks.append(chunk)
                        chunk = ''
                    chunk += sentence

                chunk += delimiter

            if len(chunk) + len(paragraph) > chunk_size:
                chunks.append(chunk)
                chunk = ''
            chunk += paragraph + delimiter

        if chunk:
            chunks.append(chunk)

        return chunks
