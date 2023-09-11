import re
from re import search
import numpy as np
import pickle

import pandas as pd
import pymorphy2
from sklearn.feature_extraction.text import TfidfVectorizer


def clean_data(text: str) -> str:
    '''Принимает на вход строку - отдает строку, очищенную от символов, кроме букв, стоп слов, и лемматизированную'''
    #  очистка от лишних символов + нижний регистр
    text = re.sub('[^\w\s]', '', text)
    text = re.sub('[-+?\d+]', '', text)
    text = text.strip()
    text = text.lower()
    #  лемматизация
    morph = pymorphy2.MorphAnalyzer()
    lemma = []
    text = re.split('\n | ', text)
    text = list(filter(None, text))
    for w in text:
        word = morph.parse(w)[0]
        lemma.append(word.normal_form)
    temp = '\n'.join(map(str, lemma))
    text = temp.split('\n')
    # очистка от стоп слов
    stop_words = []
    with open('data/stop_words_list.txt', 'r', encoding='utf-8') as file:
        stop_words = list(map(str.rstrip, file.readlines()))
    text = [token for token in text if token not in stop_words and token != " "]
    text = ' '.join(text)
    return text


def find_clients(text: str, clients: pd.DataFrame) -> str:
    '''Принимает на вход новость, отдает лист с названиями компаний - клиентов. Названия компа``ний клиентов
    (по крайней мере на данном этапе) читаются из Excel таблицы, в которой одной строке соответствуют несколько
    разных названий одной и той же компании. Итоговая метка названия добавляется из колонки "Клиент"'''
    # ищем исходные названия и названия в верхнем регистре в необработнанных данных
    answer = []
    for i in range(len(clients)):
        for j in range(len(clients.loc[i])):
            if clients.loc[i][j] != np.nan:
                if search(f'({str(clients.loc[i][j])}|{str(clients.loc[i][j]).upper()})', text):
                    answer += [clients.loc[i][0]]
                    break
    return ';'.join(answer).lower()


def find_commodity(text: str, s) -> str:
    '''Принимает на вход новость, отдает лист с названиями commodity'''
    commodity_items = []
    with open('data/commodity_list.txt', 'r', encoding='utf-8') as file:
        commodity_items = list(map(str.rstrip, file.readlines()))
    found = []
    for item in commodity_items:
        if search(item.lower(), text):
            found += [item]
    return ';'.join(found).lower()


def rate_clients(df: pd.DataFrame) -> pd.DataFrame:
    '''Принимает на вход Pandas Dataframe (df). Добавляет столбец 'clients_labels' с найденными метками классов
    по системе ранжирования новостей по компаниям - клиентам'''
    # читаем бинарную модель разделения на релевантные/нерелевантные новости
    binary_model = pickle.load(open('model/binary_classification_best.pkl', 'rb'))
    # читаем модель мультиклассовой классификации
    multiclass_model = pickle.load(open('model/multiclass_classification_best.pkl', 'rb'))
    # предсказываем релевантность и нерелевантность новостей, создаем столбец с меткой релевантности (1), нерелевантности (0)
    df['relevance'] = binary_model.predict(df['cleaned_data'])
    # предсказываем метку класса классификаци для новостей
    df['client_labels'] = multiclass_model.predict(df['cleaned_data'])
    # оставляем метки только для тех новостей, где были найдены названия клиентов и предсказана релевантность 1
    df['client_labels'] = df.apply(
        lambda x: [x['client_labels']] if ((len(x['client']) > 0) & (x['relevance'] == 1)) else [], axis=1)
    # удаляем столбец relevance
    df = df.drop(columns=['relevance'])
    return df


def rate_commodity(df: pd.DataFrame) -> pd.DataFrame:
    '''Принимает на вход Pandas Dataframe (df). Добавляет столбец 'commodity_labels' с найденными метками классов по системе ранжирования commodity'''
    # читаем систему оценивания commodity
    rating_data = pd.read_excel('data/commodity_rating_system.xlsx')
    rating_data['keys'] = rating_data['keys'].str.lower()
    rating_data['keys'] = rating_data['keys'].map(lambda x: re.split(',', x))
    # создаем новый столбец для меток
    df['commodity_labels'] = ''
    # перебираем индексы строк новостей и сами новости
    for j, article in enumerate(df['cleaned_data']):
        # заведем массив для ответа
        temp_ans = []
        # проверяем, что новость содержит commodity
        if len(df['commodity'][j]) != 0:
            # перебираем номер списка ключевых слов и сам список ключевых слов
            for i, keys in enumerate(rating_data['keys']):
                # перебираем ключевые слова
                for key in keys:
                    # добавляем метку при нахождении ключевого слова
                    if search(key, str(article)):
                        temp_ans += [rating_data['label'][i]]
                        break
        df['commodity_labels'][j] = temp_ans
    return df


def union_name(p_row: str, r_row: str) -> str:
    """
    Union names
    :param p_row: row with names from polyanalyst
    :param r_row: row with names from models (regular exception)
    return: str with union names from the all rows
    """

    p_set = set(p_row.split(';')) if p_row else set()
    r_set = set(r_row.split(';')) if r_row else set()
    common_set = p_set.union(r_set)

    return ';'.join(common_set)


def model_func(df: pd.DataFrame, type_of_article: str) -> pd.DataFrame:
    """
    Find subject names which contain in article and make score for these articles
    :param df: dataframe with article
    :param type_of_article: type of article (client or commodity)
    :return: df with subject name and score
    """
    # add column with clean text
    df['cleaned_data'] = df['text'].map(lambda x: clean_data(x))

    # read file with subject name
    subject_names = pd.read_excel(f'data/{type_of_article}_with_alternative_names.xlsx')

    # TODO: мб как то сделать менее различными?
    # find subject name in text and make rating
    if type_of_article == 'client':
        df['found_client'] = df['text'].map(lambda x: find_clients(x, subject_names))
        df['client'] = df.apply(lambda row: union_name(row['client'], row['found_client']), axis=1)
        df = rate_clients(df)
    else:
        df['found_commodity'] = df['cleaned_data'].map(lambda x: find_commodity(x, subject_names))
        df['commodity'] = df.apply(lambda row: union_name(row['commodity'], row['found_commodity']), axis=1)
        df = rate_commodity(df)

    # sum cluster labels
    df[f'{type_of_article}_score'] = df[f'{type_of_article}_labels'].map(lambda x: sum(x))

    # delete unnecessary columns
    df.drop(columns=['cleaned_data', f'{type_of_article}_labels'], inplace=True)

    return df


def deduplicate(new_articles: pd.DataFrame, old_articles: pd.DataFrame, threshold: float = 0.3) -> pd.DataFrame:
    """
    Delete similar articles
    :param new_articles: df with new article
    :param old_articles: df with article from database
    :param threshold: limit value for deduplicate
    :return: df without duplicates article
    """

    df_concat = pd.DataFrame(pd.concat([old_articles['text'], new_articles['text']], keys=['df_previous', 'df']),
                             columns=['text']).reset_index(drop=True)

    vectorizer = TfidfVectorizer()
    X_tf_idf = vectorizer.fit_transform(df_concat['text'])
    X_tf_idf = X_tf_idf.toarray()

    new_articles['unique'] = None

    for actual_pos in range(len(old_articles['text']), len(df_concat['text'])):
        flag_unique = True
        for previous_pos in range(actual_pos):
            if X_tf_idf[actual_pos, :].dot(X_tf_idf[previous_pos, :].T) > threshold:
                flag_unique = False
                break
        new_articles['unique'][actual_pos - len(old_articles['text'])] = flag_unique

    result = new_articles.drop(new_articles[new_articles.unique == False].index).reset_index(drop=True)
    result = result.drop(columns=['unique'])
    return result
