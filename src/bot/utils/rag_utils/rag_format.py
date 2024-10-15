"""Функции для форматирования и обработки ответов от РАГов"""

from copy import copy
import re

from sklearn.feature_extraction.text import TfidfVectorizer

BAD_PATTERN = '(ответ сгенерирован)|(нет ответа)'
LINKS_PATTERN = '(https)|(html)'
GIGA_MARK = 'Ответ сгенерирован Gigachat с помощью Базы Знаний. Информация требует дополнительной верификации'


def get_text_and_links(text: str) -> tuple[str, list[str]]:
    """
    Достает из параграфа смысловую часть и ссылки

    :param text: текст параграфа.
    :return: Строка смыслового параграфа и массив ссылок.
    """
    splitted = text.split('<')
    plain_text = text.split('<')[0]
    links = '<' + '<'.join(splitted[i] for i in range(1, len(splitted))) if len(splitted) > 1 else ''
    links_list = links.split(',') if len(links) > 1 else list()
    return plain_text, links_list


def contains_only_text(text: str) -> bool:
    """Проверяет, что текст не содержит ссылки"""
    return len(get_text_and_links(text)[1]) == 0


def contains_only_links(text: str) -> bool:
    """Проверяет, что текст содержит только ссылки"""
    return len(get_text_and_links(text)[0]) == 0


def contains_bad_pattern(text: str) -> bool:
    """
    Проверяет, что текст на самом деле не является нормальным ответом GigaChat.

    :param text: текст параграфа.
    :return: Булевое выражение отвечающее тому, содержит ли ответ фразы их ответов заглушек.
    """
    return bool(re.findall(BAD_PATTERN, text))


def contains_bad_links(text: str) -> bool:
    """
    Проверяет, что текст содержит какие-то осколки html ссылок.

    :param text: текст параграфа.
    :return: Булевое выражение отвечающее тому, содержит ли ответ ссылки в неправильном формате.
    """
    return bool(re.findall(LINKS_PATTERN, text))


def filter_broken_links_paragraphs(text: str) -> str:
    """
    Фильтрует параграфы, которые содержат ссылки в неправильном формате.

    :param text: текст ответа.
    :return: очищенный текст ответа.
    """
    paragrahs = text.split('\n\n')
    return '\n\n'.join(filter(lambda x: not contains_only_text(x) or not contains_bad_links(x), paragrahs))


def union_paragraphs(text: str) -> str:
    """
    Если текст и ссылки разбиты на два разных параграфа - объединяет их в один.

    :param text: текст параграфа.
    :return: текст с объединенными параграфами.
    """
    paragrahs = text.split('\n\n')
    if len(paragrahs) == 0:
        return text
    new_ans = [paragrahs[0]]
    for i in range(1, len(paragrahs)):
        par = paragrahs[i]
        if contains_only_links(par):
            if contains_only_text(new_ans[-1]):
                new_ans[-1] += f" {par}"
            else:
                union_links = set(get_text_and_links(new_ans[-1])[1]).union(get_text_and_links(par)[1])
                new_ans[-1] = get_text_and_links(new_ans[-1])[0] + ','.join(union_links)
        else:
            new_ans.append(par)
    return "\n\n".join(new_ans)


def union_paragraphs_with_same_links(text: str) -> str:
    """
    Исправляет ошибки форматирования от гигачата. Если последовательные параграфы содержат одинаковые ссылки, то объединяем их.

    :param text: текст параграфа.
    :return: текст с объединенными параграфами.
    """
    paragrahs = text.split('\n\n')
    if len(paragrahs) == 0:
        return text
    # формируем списки с текстами и сетами ссылок каждого параграфа
    texts = [get_text_and_links(text)[0] for text in text.split('\n\n')]
    links_sets = [set(map(lambda x: x.lstrip(), get_text_and_links(text)[1])) for text in text.split('\n\n')]
    new_texts = [texts[0]]
    new_links = [links_sets[0]]
    for i in range(1, len(texts)):
        # если есть пересечение по ссылкам с прошлым параграфом - объединяем их
        if len(links_sets[i].intersection(new_links[-1])) > 0:
            new_texts[-1] += f" {texts[i]}"
            new_links[-1] = links_sets[i].union(new_links[-1])
        # иначе добавляем как новый параграф
        else:
            new_texts.append(texts[i])
            new_links.append(links_sets[i])
    # собираем все это дело в один ответ
    return '\n\n'.join(new_texts[i] + ', '.join(new_links[i]) for i in range(len(new_texts)))


def fix_format_answer(text: str) -> str:
    """
    Преформатирует ответ, полученный от рага.

    :param text: текст ответа.
    :return: ответ с обработанными ошибками форматирования.
    """
    # удаляем параграфы с кривыми ссылками.
    text = filter_broken_links_paragraphs(text)
    # склеиваем абзацы, которые состоят чисто из ссылок с предыдущими
    text = union_paragraphs(text)
    # чиним параграфы с одинаковыми ссылками
    text = union_paragraphs_with_same_links(text)
    return text


def extract_summarization(news_answer: str, duckduck_answer: str, threshold=0.2) -> str:
    """
    Составляет аггрегированный ответ из двух источников.

    :param news_answer: ответ из новостного ретривера.
    :param duckduck_answer: ответ из интернет ретривера.
    :param threshold: порог схожести документов.
    :return: аггрегированный ответ.
    """
    # чиним ошибки форматирования в каждом из ответов
    news_answer = fix_format_answer(news_answer)
    duckduck_answer = fix_format_answer(duckduck_answer)
    # оставляем только смысловые параграфы
    chunks1 = list(filter(lambda x: not contains_bad_pattern(x.lower()), news_answer.split('\n\n')))
    chunks2 = list(filter(lambda x: not contains_bad_pattern(x.lower()), duckduck_answer.split('\n\n')))
    # в chunks1 оставляем тот, где больше число параграфов
    if len(chunks1) < len(chunks2):
        chunks1, chunks2 = chunks2, chunks1
    ans = copy(chunks1)
    # если второй оказался пустым - то отвечаем первым
    if len(chunks2) == 0:
        #ans.append(GIGA_MARK)
        return '\n\n'.join(ans)
    # Добираем параграфы из второго ответа, которые непохожи на параграфы из первого ответа
    all_batch = chunks1 + chunks2
    texts = [get_text_and_links(text)[0] for text in all_batch]
    links_sets = [set(map(lambda x: x.lstrip(), get_text_and_links(text)[1])) for text in all_batch]
    # считаем скоры схожести
    vectorizer = TfidfVectorizer()
    texts_vectorized = vectorizer.fit_transform(texts)
    scores_tf_idf = texts_vectorized @ texts_vectorized.T
    for i, candidate in enumerate(chunks2):
        flag_unique = True
        index = i + len(chunks1)
        # если параграф состоит только из ссылок, то пропускаем его
        if len(texts[index]) == 0:
            continue
        for j, previous in enumerate(chunks1):
            is_contains_links_intersection = len(links_sets[index].intersection(links_sets[j])) > 0
            is_similar_to_previous = float(scores_tf_idf[index, j]) > threshold
            # Если не близкие, но есть одинаковые ссылки - добавляем текст и разницу ссылок в предыдущий параграф
            if is_contains_links_intersection and not is_similar_to_previous:
                flag_unique = False
                texts[j] += f" {texts[index]}"
                links_sets[j] = links_sets[j].union(links_sets[index])
                ans[j] = texts[j] + ', '.join(links_sets[j])
            # Если близкие, но есть или нет одинаковые ссылки - пропускаем просто
            elif is_similar_to_previous:
                flag_unique = False
        if flag_unique:
            ans.append(candidate)
    #ans.append(GIGA_MARK)
    return '\n\n'.join(ans)
