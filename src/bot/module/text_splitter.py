import math
import re


class SentenceSplitter:

    sentence_end_characters = r'(\.\.\.)|[\.!?]'

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
            if len(chunk) + len(paragraph) + len(delimiter) < chunk_size:
                chunk += paragraph + delimiter
            else:
                chunks.append(chunk.strip())
                chunk = paragraph + delimiter

        if chunk:
            chunks.append(chunk.strip())

        return chunks
