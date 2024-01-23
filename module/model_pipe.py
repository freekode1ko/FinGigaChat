import json
import pickle
import re
from re import search
from typing import Dict

import pandas as pd
import pymorphy2
from requests.exceptions import ConnectionError
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

from config import psql_engine, summarization_prompt
from module.chatgpt import ChatGPT
from module.gigachat import GigaChat
from module.logger_base import Logger

CLIENT_BINARY_CLASSIFICATION_MODEL_PATH = 'model/client_binary_best2.pkl'
CLIENT_MULTY_CLASSIFICATION_MODEL_PATH = 'model/multiclass_classification_best.pkl'
COM_BINARY_CLASSIFICATION_MODEL_PATH = 'model/commodity_binary_best.pkl'
STOP_WORDS_FILE_PATH = 'data/stop_words_list.txt'
COMMODITY_RATING_FILE_PATH = 'data/rating/commodity_rating_system.xlsx'
CLIENT_RATING_FILE_PATH = 'data/rating/client_rating_system.xlsx'
ALTERNATIVE_NAME_FILE = 'data/name/{}_with_alternative_names.xlsx'

BAD_GIGA_ANSWERS = [
    'Что-то в вашем вопросе меня смущает. Может, поговорим на другую тему?',
    'Как у нейросетевой языковой модели у меня не может быть настроения, но почему-то я совсем не хочу ' 'говорить на эту тему.',
    'Не люблю менять тему разговора, но вот сейчас тот самый случай.',
    'Спасибо за информацию! Я передам ее дальше.',
]
STOCK_WORDS = [
    'индекс мосбиржа',
    'индекс мб',
    'индекс ртс ',
    's&p',
    'фондовый рынок',
    'курс доллар',
    'курс рубль',
    'курс евро',
    'дайджест',
    'открытие рынок',
    'закрытие рынок',
    'комметарий по рынок',
    'утренний обзор',
    'вечерний обзор',
    'главный анонс',
    'главный событие день',
    'главный событие неделя',
    'главный событие месяц',
    'вечерний комментарий',
    'дневной обзор',
]


def get_alternative_names_pattern_commodity(alt_names):
    """Создает регулярные выражения для коммодов"""
    alter_names_dict = dict()
    table_subject_list = alt_names.values.tolist()
    for i, alt_names_list in enumerate(table_subject_list):
        clear_alt_names = list(filter(lambda x: not pd.isna(x), alt_names_list))
        names_pattern_base = '|'.join(clear_alt_names)
        names_patter_upper = '|'.join([el.upper() for el in clear_alt_names])
        key = clear_alt_names[0]
        alter_names_dict[key] = f'({names_pattern_base}|{names_patter_upper})'
    return alter_names_dict


def add_endings(clear_names_list):
    """Добавляет окончания к именам клиента в списке альтернативных имен"""
    vowels = 'ауоыэяюиеь'
    english_vowels = 'aeiouy'
    ending_v = '|а|я|ы|и|е|у|ю|ой|ей'
    ending_c = '|о|е|а|я|у|ю|и|ом|ем'

    for i, name in enumerate(clear_names_list):
        name_strip = name.strip()
        if ' ' not in name_strip:

            last_mark = name_strip[-1]
            last_mark_lower = last_mark.lower()

            if last_mark_lower in vowels and len(name_strip) > 3:
                clear_names_list[i] = f'{name[:-1]}({last_mark}{ending_v})'
            elif last_mark.isalpha() and last_mark_lower not in english_vowels and last_mark != 'ъ':
                clear_names_list[i] = f'{name}({ending_c})'

    return clear_names_list


def get_alternative_names_pattern_client(alt_names):
    """Создает регулярные выражения для клиентов"""
    alter_names_dict = dict()
    table_subject_list = alt_names.values.tolist()
    for alt_names_list in table_subject_list:
        clear_alt_names = list(filter(lambda x: not pd.isna(x), alt_names_list))
        key = clear_alt_names[0]

        clear_alt_names = add_endings(clear_alt_names)
        clear_alt_names_upper = add_endings([el.upper() for el in clear_alt_names])

        names_pattern_base = '( |\. |, |\) )|'.join(clear_alt_names)
        names_pattern_base += '( |\. |, |\) )'
        names_patter_upper = '( |\. |, |\) )|'.join(clear_alt_names_upper)
        names_patter_upper += '( |\. |, |\) )'
        alter_names_dict[key] = f'({names_pattern_base}|{names_patter_upper})'.replace('+', '\+')

    return alter_names_dict


morph = pymorphy2.MorphAnalyzer()

client_names = pd.read_excel(ALTERNATIVE_NAME_FILE.format('client'))
commodity_names = pd.read_excel(ALTERNATIVE_NAME_FILE.format('commodity'))
alter_client_names_dict = get_alternative_names_pattern_client(client_names)
alter_commodity_names_dict = get_alternative_names_pattern_commodity(commodity_names)

client_rating_system_dict = pd.read_excel(CLIENT_RATING_FILE_PATH).to_dict('records')
commodity_rating_system_dict = pd.read_excel(COMMODITY_RATING_FILE_PATH).to_dict('records')
for group in commodity_rating_system_dict:
    group['key words'] = ','.join([f' {word.strip().lower()}' for word in group['key words'].split(',')])


def find_bad_gas(names: str, clean_text: str) -> str:
    if 'газ' in names:
        if search('магазин|газета|парниковый|углекислый| сектор газ ', clean_text):
            names_list = names.split(';')
            names_list.remove('газ')
            names = ';'.join(names_list)
    return names


def check_gazprom(names: str, names_impact: Dict, text: str) -> str:
    text = text.replace('"', '')
    names_list = names.split(';')
    names_impact_list = list(eval(names_impact).keys())
    if 'газпром' in names and 'газпром нефть' in names_impact_list:
        if not search('газпром(?! нефт[ьи])', text):
            try:
                names_list.remove('газпром')
                names = ';'.join(names_list)
            except ValueError:
                print('check gazprom error in ', names)
    return names


def get_names_pattern(names: str, type_of_article: str):
    """
    Make pattern with alternative names
    :param names: names which were founded in article
    :param type_of_article: client or commodity
    :return: pattern which included alternative names
    """
    # Load alternative names data
    df_alternative_names = pd.read_excel(ALTERNATIVE_NAME_FILE.format(type_of_article), index_col=False)
    df_alternative_names = df_alternative_names.applymap(lambda x: x.lower().strip() if isinstance(x, str) else None)
    first_column = df_alternative_names.columns[0]

    # Filter alternative names based on input names
    names_list = names.split(';')
    names_alternative_list = df_alternative_names[df_alternative_names[first_column].isin(names_list)].values.tolist()

    # Create a list of names
    list_of_all_names = [name for client_list in names_alternative_list for name in client_list if pd.notnull(name)]

    # Generate names pattern
    if type_of_article == 'commodity':
        # TODO: костыль: нужна основа или альтернативные названия более полные
        names_pattern = '|'.join([name[:-1] for name in list_of_all_names if len(name) > 3])
    else:
        names_pattern = '|'.join(list_of_all_names)

    return names_pattern


def find_stock(title: str, names: str, clean_text: str, labels: str, type_of_article: str = 'client') -> str:
    """
    Processing news about stock
    :param title: title of article
    :param names: names that which found in article
    :param clean_text: text in normal view
    :param labels: labels with score
    :param type_of_article: client or commodity
    :return: score by rules or unchanged
    """
    # Make patterns
    stock_pattern = '|'.join(STOCK_WORDS)
    names_pattern = get_names_pattern(names, type_of_article)

    # Get new labels score based on rules
    if labels == '-1':
        return labels
    elif title and isinstance(title, str) and search(stock_pattern, clean_text):
        clean_title = clean_data(title)
        if search(stock_pattern, clean_title):
            return '0'
        else:
            return '1' if search(names_pattern, clean_title) and names else '0'
    else:
        return labels


def clean_data(text: str) -> str:
    """
    Takes string, - erase symbols excluding letters from it, lemmatize, stop-words cleaning and lower case casting.
    :param text: str. String to clean.
    :return: str. Current cleaned string.
    """
    #  cleaning from symbols excluding letters and casting to lower case
    text = re.sub('[^\w\s]', '', text)
    text = re.sub('[-+?\d+]', '', text)
    text = text.lower()
    text_list = re.split('\s', text)
    text_list = list(filter(None, text_list))
    #  lemmatization
    lemma = []
    for w in text_list:
        word = morph.parse(w)[0]
        lemma.append(word.normal_form)
    # stop words cleaning
    with open(STOP_WORDS_FILE_PATH, 'r', encoding='utf-8') as file:
        stop_words_list = [line.strip() for line in file.readlines()]
    clean_text_list = [token for token in lemma if token not in stop_words_list]
    clean_text = ' '.join(clean_text_list)
    return clean_text


def find_names(article_text, alt_names_dict, rule_flag: bool = False):
    """
    Takes string and returns string with all found names (with ; separator) from provided Pandas DF.
    :param article_text: str. Current string in which we search for names.
    :param alt_names_dict: Pandas DF. Pandas DF with columns with names neeeded to be found. In one row all names - alternatives.
    :param rule_flag: bool. Flag shows that it commodity text or not.
    :return: str. String with found names separated with ; symbol.
    """
    # TODO: убрать удаление кавычек, когда перейдем на свой парсинг
    article_text = article_text.replace('"', '')
    names_dict = {}
    for key, alt_names in alt_names_dict.items():
        alt_names = alt_names.replace('"', '')
        re_findall = re.findall(alt_names, article_text)
        if re_findall:
            key_name = key.lower().strip()
            names_dict[key_name] = len(re_findall)
    impact_json = json.dumps(names_dict, ensure_ascii=False)
    if rule_flag:
        max_count = max(names_dict.values(), default=None)
        if max_count and max_count != 1:
            return ';'.join([key for key, val in names_dict.items() if val == max_count]), impact_json
        return '', impact_json
    return ';'.join(names_dict.keys()), impact_json


def find_names_online(article_title, article_text, alt_names_dict):
    """
    Takes string and returns string with all found names (with ; separator) from provided Pandas DF.
    :param article_title: str. Current string in which we search for names.
    :param article_text: str. Current string in which we search for names.
    :param alt_names_dict: Pandas DF. Pandas DF with columns with names needed to be found. In one row all names - alternatives.
    :return: str. String with found names separated with ; symbol.
    """
    article_text = ' {} '.format(article_text.replace('"', ''))
    article_title = ' {} '.format(article_title.replace('"', '')) if isinstance(article_title, str) else ''
    names_dict = {}
    title_name_list = []
    names_text = ''
    for key, alt_names in alt_names_dict.items():
        alt_names = alt_names.replace('"', '')
        re_findall = re.findall(alt_names, article_text)

        # find in text
        if re_findall:
            key_name = key.lower().strip()
            names_dict[key_name] = len(re_findall)

        # find in title
        re_findall_t = re.findall(alt_names, article_title)
        if re_findall_t:
            title_name_list.append(key.lower().strip())

    names_title = ';'.join(title_name_list)
    impact_json = json.dumps(names_dict, ensure_ascii=False)
    max_count = max(names_dict.values(), default=None)
    if max_count and max_count != 1:
        names_text = ';'.join([key for key, val in names_dict.items() if val == max_count])

    names = union_name(names_title, names_text)
    return names, impact_json


def down_threshold(engine, type_of_article, names, threshold) -> float:
    """
    Down threshold if new contains rare subject
    :param engine: engine to database
    :param type_of_article: client or commodity
    :param names: list with names of different subjects
    :param threshold: float value, limit of relevance
    :return: new little threshold
    """
    # TODO: искать кол-во новостей за квартал
    minus_threshold = 0.2
    min_count_article_val = 7
    counts_dict = {}
    with engine.connect() as conn:
        for subject_name in names:
            query_count = (
                'SELECT COUNT(article_id) FROM relation_{type_of_article}_article r '
                'JOIN {type_of_article} ON r.{type_of_article}_id={type_of_article}.id '
                "where {type_of_article}.name = '{subject_name}'"
            )
            count = conn.execute(text(query_count.format(type_of_article=type_of_article, subject_name=subject_name))).fetchone()
            counts_dict[subject_name] = count
    min_count = min(counts_dict.values())
    threshold = threshold - minus_threshold if min_count[0] <= min_count_article_val else threshold
    return threshold


def search_keywords(relevance, subject, clean_text, labels, rating_dict):
    if not subject:
        labels = '-1'
    elif not relevance:
        labels = '0'
    else:
        labels = str(labels)
        for group in rating_dict:
            keywords_pattern = group['key words'].replace(',', '|')
            if search(keywords_pattern, clean_text):
                label = str(group['label'])
                if label not in labels:
                    labels += f';{label}'

    return labels


def rate_client(df, rating_dict, threshold: float = 0.65) -> pd.DataFrame:
    """
    Takes Pandas DF with current news batch and makes predictions over them.
    :param rating_dict: dict with rating
    :param df: Pandas DF. Pandas DF with current news batch.
    :param threshold: limit relevant for binary model
    :return: Pandas DF. Current news batch DF with added column 'client_labels'
    """
    # read binary classification model (relevant or not)
    with open(CLIENT_BINARY_CLASSIFICATION_MODEL_PATH, 'rb') as f:
        binary_model = pickle.load(f)

    # read multiclass classification model
    with open(CLIENT_MULTY_CLASSIFICATION_MODEL_PATH, 'rb') as f:
        multiclass_model = pickle.load(f)

    # predict relevance and adding a column with relevance label (1 or 0)
    probs = binary_model.predict_proba(df['cleaned_data'])
    df['relevance'] = [1 if (pair[1]) > threshold else 0 for pair in probs]

    # predict label from multiclass classification
    df['client_labels'] = multiclass_model.predict(df['cleaned_data'])

    # using relevance label condition
    df['client_labels'] = df.apply(
        lambda row: search_keywords(row['relevance'], row['client'], row['cleaned_data'], row['client_labels'], rating_dict), axis=1
    )

    # delete relevance column
    df.drop(columns=['relevance'], inplace=True)

    # processing stck news
    df['client_labels'] = df.apply(
        lambda row: find_stock(row['title'], row['client'], row['cleaned_data'], row['client_labels']), axis=1
    )

    return df


def rate_commodity(df, rating_dict, threshold=0.5) -> pd.DataFrame:
    """
    Taking a current news batch to rate. Adding new columns with found labels from commodity rate system.
    :param df: Pandas DF. Pandas DF with current news batch.
    :param rating_dict: dict with rating
    :param threshold : float. Threshold on binary commodity relevance model.
    :return: Pandas DF. Current news batch DF with added column 'commodity_labels'
    """

    with open(COM_BINARY_CLASSIFICATION_MODEL_PATH, 'rb') as f:
        binary_model = pickle.load(f)

    probs = binary_model.predict_proba(df['cleaned_data'])

    res = []
    engine = create_engine(psql_engine, poolclass=NullPool)
    for index, pair in enumerate(probs):
        commodity_names = df['commodity'].iloc[index].split(';')
        local_threshold = down_threshold(engine, 'commodity', commodity_names, threshold)
        res.append(1 if (pair[1]) > local_threshold else 0)
    df['relevance'] = res

    df['commodity_labels'] = df.apply(
        lambda row: search_keywords(row['relevance'], row['commodity'], row['cleaned_data'], '0', rating_dict), axis=1
    )
    df.drop(columns=['relevance'], inplace=True)

    df['commodity_labels'] = df.apply(
        lambda row: find_stock(row['title'], row['commodity'], row['cleaned_data'], row['commodity_labels'], 'commodity'), axis=1
    )
    return df


def union_name(p_row: str, r_row: str) -> str:
    """
    Union names
    :param p_row: row with names from polyanalyst
    :param r_row: row with names from models (regular exception)
    return: str with union names from the all rows
    """
    p_set = set(el.strip() for el in p_row.split(';')) if p_row else set()
    r_set = set(el.strip() for el in r_row.split(';')) if r_row else set()
    common_set = p_set.union(r_set)

    return ';'.join(common_set)


def summarization_by_giga(logger: Logger.logger, giga_chat: GigaChat, token: str, text: str) -> str:
    """
    Создание краткой версии новостного текста с помощью GigaChat
    :param logger: экземпляр класса логер для логирования процесса
    :param giga_chat: экземпляр класса GigaChat
    :param token: токен авторизации в GigaChat
    :param text: текст новости
    :return: суммаризированный текст
    """

    try:
        giga_json_answer = giga_chat.ask_giga_chat(token=token, text=text, prompt=summarization_prompt)
        giga_answer = giga_json_answer.json()['choices'][0]['message']['content']
    except ConnectionError:
        giga_chat = GigaChat()
        token = giga_chat.get_user_token()
        giga_json_answer = giga_chat.ask_giga_chat(token=token, text=text, prompt=summarization_prompt)
        giga_answer = giga_json_answer.json()['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f'Ошибка при создании саммари: {e}')
        print(f'Ошибка при создании саммари: {e}')
        giga_answer = ''

    paragraphs = giga_answer.split('\n\n')
    giga_answer = '\n'.join([p for p in paragraphs if p.strip()])

    if giga_answer in BAD_GIGA_ANSWERS:
        logger.error('GigaChat отказался генерировать саммари из-за цензуры')
        giga_answer = ''

    return giga_answer


def change_bad_summary(logger: Logger.logger, row: pd.Series) -> str:
    """Изменение краткой версии текста, если ее нет"""
    if row['text_sum']:
        return row['text_sum']
    # elif row['title']:
    #     return row['title']
    else:
        print(f'GigaChat не сгенерировал саммари для новости  {row["link"]}')
        logger.error(f'GigaChat не сгенерировал саммари для новости {row["link"]}')
        first_sentence = row['text'][: row['text'].find('.') + 1]
        return first_sentence


def model_func(logger: Logger.logger, df: pd.DataFrame, type_of_article: str) -> pd.DataFrame:
    """
    Нахождение имен объектов в тексте новости и назначение баллов значимости новости
    :param logger: экземпляр класса логер для логирования процесса
    :param df: датафрейм с новостями
    :param type_of_article: тип новости (client или commodity)
    :return: датафрейм с найденными в новостях объектами и баллами значимости
    """

    logger.debug('Приведение текста новостей в нормальную форму')
    df['cleaned_data'] = df['text'].map(lambda x: clean_data(x))

    logger.debug(f'Нахождение {type_of_article} в тексте новости')

    if type_of_article == 'client':
        df[['found_client', 'client_impact']] = df['text'].apply(lambda x: pd.Series(find_names(x, alter_client_names_dict)))

        df[type_of_article] = df.apply(lambda row: union_name(row['client'], row['found_client']), axis=1)
        df[type_of_article] = df.apply(lambda row: check_gazprom(row['client'], row['client_impact'], row['text']), axis=1)

        logger.debug('Сортировка новостей о клиентах')
        df = rate_client(df, client_rating_system_dict)

    else:
        df[['found_commodity', 'commodity_impact']] = df['cleaned_data'].apply(
            lambda x: pd.Series(find_names(x, alter_commodity_names_dict, True))
        )

        df['found_commodity'] = df.apply(lambda row: find_bad_gas(row['found_commodity'], row['cleaned_data']), axis=1)
        df[type_of_article] = df['found_commodity']

        logger.debug('Сортировка новостей о товарах')
        df = rate_commodity(df, commodity_rating_system_dict)

    # суммирование баллов значимости
    df[f'{type_of_article}_score'] = df[f'{type_of_article}_labels'].map(lambda x: sum(list(map(int, list(x.split(';'))))))

    # удаление ненужных колонок
    df.drop(columns=[f'{type_of_article}_labels', f'found_{type_of_article}'], inplace=True)

    return df


def model_func_online(logger: Logger.logger, df: pd.DataFrame) -> pd.DataFrame:
    """
    Нахождение имен объектов в тексте новости и назначение баллов значимости новости
    :param logger: экземпляр класса логер для логирования процесса
    :param df: датафрейм с новостями
    :return: датафрейм с найденными в новостях объектами и баллами значимости
    """

    logger.debug('Приведение текста новостей в нормальную форму')
    df['cleaned_data'] = df['text'].map(lambda x: clean_data(x))

    # find subject name in text
    logger.debug('Нахождение клиентов в тексте новости')
    df[['client', 'client_impact']] = df.apply(
        lambda row: pd.Series(find_names_online(row['title'], row['text'], alter_client_names_dict)), axis=1
    )
    df['client'] = df.apply(lambda row: check_gazprom(row['client'], row['client_impact'], row['text']), axis=1)

    logger.debug('Нахождение товаров в тексте новости')
    df[['commodity', 'commodity_impact']] = df.apply(
        lambda row: pd.Series(find_names_online(row['title'], row['cleaned_data'], alter_commodity_names_dict)), axis=1
    )
    df['commodity'] = df.apply(lambda row: find_bad_gas(row['commodity'], row['cleaned_data']), axis=1)

    # make rating for article
    logger.debug('Сортировка новостей о клиентах')
    df = rate_client(df, client_rating_system_dict)
    logger.debug('Сортировка новостей о товарах')
    df = rate_commodity(df, commodity_rating_system_dict)

    # суммирование баллов значимости
    df['client_score'] = df['client_labels'].map(lambda x: sum(list(map(int, list(x.split(';'))))))
    df['commodity_score'] = df['commodity_labels'].map(lambda x: sum(list(map(int, list(x.split(';'))))))

    # удаление ненужных колонок
    df.drop(columns=['client_labels', 'commodity_labels'], inplace=True)

    return df


def add_text_sum_column(logger: Logger.logger, df: pd.DataFrame) -> pd.DataFrame:
    """Make summary for dataframe with articles"""
    logger.debug('Создание саммари')
    giga_chat = GigaChat()
    token = giga_chat.get_user_token()
    df['text_sum'] = df['text'].apply(lambda text: summarization_by_giga(logger, giga_chat, token, text))
    df['text_sum'] = df.apply(lambda row: change_bad_summary(logger, row), axis=1)
    return df


def deduplicate(logger: Logger.logger, df: pd.DataFrame, df_previous: pd.DataFrame, threshold: float = 0.35) -> pd.DataFrame:
    """
    Удаление похожих новостей. Чем выше граница, тем сложнее посчитать новость уникальной
    :param logger: экземпляр класса логер для логирования процесса
    :param df: датафрейм с только что полученными новостями
    :param df_previous: датафрейс с новостями из БД
    :param threshold: граница отсечения новости
    :return: датафрейм без дублей
    """
    # отчищаем датафрейма от нерелевантных новостей
    old_len = len(df)
    df = df.query('not client_score.isnull() and client_score != -1 or ' 'not commodity_score.isnull() and commodity_score != -1')
    now_len = len(df)
    logger.info(f'Количество нерелевантных новостей - {old_len - now_len}')
    logger.info(f'Количество новостей перед удалением дублей - {now_len}')

    # сортируем батч новостей по кол-ву клиентов и товаров, а также по баллам значимости
    df['count_client'] = df['client'].map(lambda x: len(list(x.split(sep=';'))) if (isinstance(x, str) and x) else 0)
    df['count_commodity'] = df['commodity'].map(lambda x: len(list(x.split(sep=';'))) if (isinstance(x, str) and x) else 0)
    df = df.sort_values(
        by=['count_client', 'count_commodity', 'client_score', 'commodity_score'], ascending=[False, False, False, False]
    ).reset_index(drop=True)
    df.drop(columns=['count_client', 'count_commodity'], inplace=True)

    # объединяем столбцы старого и нового датафрейма
    df_concat = pd.concat([df_previous['cleaned_data'], df['cleaned_data']], ignore_index=True)
    df_concat_client = pd.concat([df_previous['client'], df['client']], ignore_index=True).fillna(';')
    df_concat_commodity = pd.concat([df_previous['commodity'], df['commodity']], ignore_index=True).fillna(';')

    # векторизируем новости в датафрейме
    vectorizer = TfidfVectorizer()
    X_tf_idf = vectorizer.fit_transform(df_concat)
    X_tf_idf = X_tf_idf.toarray()

    # добавляем колонку с флагом уникальности новости
    df['unique'] = None

    start = len(df_previous['cleaned_data'])
    end = len(df_concat)
    # для каждой новой новости
    for actual_pos in range(start, end):

        flag_unique = True  # флаг уникальности новости
        flag_found_same = False  # флаг нахождения в новостях одинаковых клиентов

        # от начала старых новостей до конца новых новостей
        for previous_pos in range(actual_pos):

            # если новость из старого батча + 0.2 к границе (чем выше граница, тем сложнее посчитать новость уникальной)
            current_threshold = threshold + 0.2 if previous_pos < start else threshold

            actual_client = df_concat_client[actual_pos].split(';')
            actual_commodity = df_concat_commodity[actual_pos].split(';')
            previous_client = df_concat_client[previous_pos].split(';')
            previous_commodity = df_concat_commodity[previous_pos].split(';')

            # для каждого клиента в списке найденных клиентов
            for client in actual_client:
                # если клиент есть в старой новости, то говорим, что новости имеют одинаковых клиентов
                if client in previous_client and len(actual_client) > 1 and len(previous_client) > 1:
                    flag_found_same = True

            # для каждого товара в списке найденных товаров
            for commodity in actual_commodity:
                # если товар есть в старой новости, то говорим, что новости имеют одинаковые товары
                if commodity in previous_commodity and len(actual_commodity) > 1 and len(previous_commodity) > 1:
                    flag_found_same = True

            # меняем границу, если новости имеют одинаковых клиентов
            current_threshold = current_threshold if flag_found_same else current_threshold + 0.1

            # если разница между векторами рассматриваемых новостей больше границы, то новость неуникальна
            if X_tf_idf[actual_pos, :].dot(X_tf_idf[previous_pos, :].T) > current_threshold:
                flag_unique = False
                break

        # присваем флаг уникальности новости
        df['unique'][actual_pos - start] = flag_unique

    # удаляем дубли из нового батча
    if not df.empty:
        df = df[df['unique']]
        df.drop(columns=['unique'], inplace=True)

    logger.info(f'Количество новостей из базы данных за последние 14 дней - {len(df_previous)}')
    logger.info(f'Количество новостей после удаления дублей - {len(df)}')

    return df


def summarization_by_chatgpt(full_text: str):
    # TODO: do by langchain
    """Make summary by chatgpt"""
    batch_size = 4000
    text_batches = []
    new_text_sum = ''
    if len(full_text + summarization_prompt) > batch_size:
        while len(full_text + summarization_prompt) > batch_size:
            point_index = full_text[:batch_size].rfind('.')
            text_batches.append(full_text[: point_index + 1])
            full_text = full_text[point_index + 1 :]
    else:
        text_batches = [full_text]
    for batch in text_batches:
        gpt = ChatGPT()
        query_to_gpt = gpt.ask_chat_gpt(text=batch, prompt=summarization_prompt)
        new_text_sum = new_text_sum + query_to_gpt.choices[0].message.content

    return new_text_sum
