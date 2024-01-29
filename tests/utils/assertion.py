import typing as t


def assert_words_in_text(words: t.List[str], text: str) -> None:
    """
    Assert того, что все строки из списка есть в строке
    Args:
        words: список слов (строк)
        text: текст, в который проверяем вхождение
    """
    for word in words:
        assert word in text
