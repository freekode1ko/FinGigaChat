import re
from re import search
import json
import pickle
from requests.exceptions import ConnectionError

import pandas as pd
import pymorphy2
from sklearn.feature_extraction.text import TfidfVectorizer
from openai.error import InvalidRequestError
from sqlalchemy import create_engine, text

from config import summarization_prompt, psql_engine
from module.gigachat import GigaChat
from module.chatgpt import ChatGPT

CLIENT_BINARY_CLASSIFICATION_MODEL_PATH = 'model/client_binary_best2.pkl'
CLIENT_MULTY_CLASSIFICATION_MODEL_PATH = 'model/multiclass_classification_best.pkl'
COM_BINARY_CLASSIFICATION_MODEL_PATH = 'model/commodity_binary_best.pkl'
STOP_WORDS_FILE_PATH = 'data/stop_words_list.txt'
COMMODITY_RATING_FILE_PATH = 'data/rating/commodity_rating_system.xlsx'
CLIENT_RATING_FILE_PATH = 'data/rating/client_rating_system.xlsx'
ALTERNATIVE_NAME_FILE = 'data/name/{}_with_alternative_names.xlsx'

BAD_GIGA_ANSWERS = ['Что-то в вашем вопросе меня смущает. Может, поговорим на другую тему?',
                    'Как у нейросетевой языковой модели у меня не может быть настроения, но почему-то я совсем не хочу '
                    'говорить на эту тему.',
                    'Не люблю менять тему разговора, но вот сейчас тот самый случай.',
                    'Спасибо за информацию! Я передам ее дальше.']
STOCK_WORDS = ['индекс мосбиржа', 'индекс мб', 'индекс ртс ', 's&p', 'фондовый рынок', 'курс доллар',
               'курс рубль', 'курс евро', 'дайджест', 'открытие рынок', 'закрытие рынок', 'комметарий по рынок',
               'утренний обзор', 'вечерний обзор', 'главный анонс', 'главный событие день', 'главный событие неделя',
               'главный событие месяц', 'вечерний комментарий', 'дневной обзор']

morph = pymorphy2.MorphAnalyzer()


def find_bad_gas(names: str, clean_text: str) -> str:
    if 'газ' in names:
        if search('парниковый|углекислый ', clean_text):
            names_list = names.split(';')
            names_list.remove('газ')
            names = ';'.join(names_list)
    return names


def check_gazprom(names: str, text: str) -> str:
    text = text.replace('"', '')
    names_list = names.split(';')
    if 'газпром' in names_list and 'газпром нефть' in names_list:
        if not search('газпром(?! нефт[ь,и])', text):
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
    if title and isinstance(title, str) and search(stock_pattern, clean_text):
        clean_title = clean_data(title)
        if search(stock_pattern, clean_title):
            return '0'
        else:
            return '1' if search(names_pattern, clean_title) else '0'
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


def find_names(article_text, alt_names_dict, commodity_flag: bool = False):
    """
    Takes string and returns string with all found names (with ; separator) from provided Pandas DF.
    :param article_text: str. Current string in which we search for names.
    :param alt_names_dict: Pandas DF. Pandas DF with columns with names neeeded to be found. In one row all names - alternatives.
    :param commodity_flag: bool. Flag shows that it commodity text or not.
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
    if commodity_flag:
        max_count = max(names_dict.values(), default=None)
        if max_count and max_count != 1:
            return ';'.join([key for key, val in names_dict.items() if val == max_count]), impact_json
        return '', impact_json
    return ';'.join(names_dict.keys()), impact_json


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
            query_count = ("SELECT COUNT(article_id) FROM relation_{type_of_article}_article r "
                           "JOIN {type_of_article} ON r.{type_of_article}_id={type_of_article}.id "
                           "where {type_of_article}.name = '{subject_name}'")
            count = conn.execute(text(query_count.format(type_of_article=type_of_article, subject_name=subject_name))).fetchone()
            counts_dict[subject_name] = count
    min_count = min(counts_dict.values())
    threshold = threshold - minus_threshold if min_count[0] <= min_count_article_val else threshold
    return threshold


def search_keywords(relevance, subject, clean_text, labels, rating_dict):
    if not relevance or not subject:
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
    df['client_labels'] = df.apply(lambda row: search_keywords(row['relevance'], row['client'], row['cleaned_data'],
                                                               row['client_labels'], rating_dict), axis=1)

    # delete relevance column
    df.drop(columns=['relevance'], inplace=True)

    # processing stck news
    df['client_labels'] = df.apply(lambda row: find_stock(row['title'], row['client'], row['cleaned_data'],
                                                          row['client_labels']), axis=1)

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
    engine = create_engine(psql_engine, pool_pre_ping=True)
    for index, pair in enumerate(probs):
        commodity_names = df['commodity'].iloc[index].split(';')
        local_threshold = down_threshold(engine, 'commodity', commodity_names, threshold)
        res.append(1 if (pair[1]) > local_threshold else 0)
    df['relevance'] = res

    df['commodity_labels'] = df.apply(lambda row: search_keywords(row['relevance'], row['commodity'],
                                                                  row['cleaned_data'], '0', rating_dict), axis=1)
    df.drop(columns=['relevance'], inplace=True)

    df['commodity_labels'] = df.apply(lambda row: find_stock(row['title'], row['commodity'], row['cleaned_data'],
                                                             row['commodity_labels'], 'commodity'), axis=1)
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


def summarization_by_giga(giga_chat: GigaChat, token: str, text: str) -> str:
    """
    Make summary of article text by GigaChat.
    :param giga_chat: instance of GigaChat.
    :param token: token of GigaChat chat.
    :param text: text of article for summarization.
    :return: summarization text.
    """

    try:
        giga_json_answer = giga_chat.ask_giga_chat(token=token, text=text, prompt=summarization_prompt)
        giga_answer = giga_json_answer.json()['choices'][0]['message']['content']
    except ConnectionError:
        print('ConnectionResetError while summarization by GigaChat')
        giga_chat = GigaChat()
        token = giga_chat.get_user_token()
        giga_json_answer = giga_chat.ask_giga_chat(token=token, text=text, prompt=summarization_prompt)
        giga_answer = giga_json_answer.json()['choices'][0]['message']['content']
    except Exception as e:
        print(e)
        giga_answer = ''

    if giga_answer in BAD_GIGA_ANSWERS:
        giga_answer = ''

    return giga_answer


def change_bad_summary(row: pd.Series) -> str:
    """ Change summary if it is not exist """
    if row['text_sum'] and len(row['text_sum']) > 50:
        return row['text_sum']
    # TODO: если заголовки не будут отображаться в боте, то раскомментировать
    # elif row['title']:
    #     return row['title']
    else:
        print(f'GigaChat did not make summary for {row["link"]}')
        first_sentence = row['text'][:row['text'].find('.') + 1]
        return first_sentence


def get_alternative_names_pattern(alt_names):
    alter_names_dict = dict()
    table_subject_list = alt_names.values.tolist()
    for i, alt_names_list in enumerate(table_subject_list):
        clear_alt_names = list(filter(lambda x: not pd.isna(x), alt_names_list))
        names_pattern_base = '|'.join(clear_alt_names)
        names_patter_upper = '|'.join([el.upper() for el in clear_alt_names])
        key = clear_alt_names[0]
        alter_names_dict[key] = f'({names_pattern_base}|{names_patter_upper})'
    return alter_names_dict


def model_func(df: pd.DataFrame, type_of_article: str) -> pd.DataFrame:
    """
    Find subject names which contain in article and make score for these articles
    :param df: dataframe with article
    :param type_of_article: type of article (client or commodity)
    :return: df with subject name and score
    """

    # add column with clean text
    print('-- cleaned data')
    df['cleaned_data'] = df['text'].map(lambda x: clean_data(x))

    # read file with subject name
    subject_names = pd.read_excel(ALTERNATIVE_NAME_FILE.format(type_of_article))
    alter_names_dict = get_alternative_names_pattern(subject_names)

    # make_summarization
    print(f'-- make summary for {type_of_article}')
    giga_chat = GigaChat()
    token = giga_chat.get_user_token()
    df['text_sum'] = df['text'].apply(lambda text: summarization_by_giga(giga_chat, token, text))
    df['text_sum'] = df.apply(lambda row: change_bad_summary(row), axis=1)

    # find subject name in text
    print(f'-- find {type_of_article} names in article')

    if type_of_article == 'commodity':

        df[[f'found_{type_of_article}', 'commodity_impact']] = df['cleaned_data'].apply(
            lambda x: pd.Series(find_names(x, alter_names_dict, True)))

        df[f'found_{type_of_article}'] = df.apply(lambda row: find_bad_gas(row[f'found_{type_of_article}'],
                                                                           row['cleaned_data']), axis=1)
        df[type_of_article] = df[f'found_{type_of_article}']

    else:

        df[[f'found_{type_of_article}', 'client_impact']] = df['text'].apply(
            lambda x: pd.Series(find_names(x, alter_names_dict)))

        df[type_of_article] = df.apply(lambda row: union_name(row[type_of_article], row[f'found_{type_of_article}']), axis=1)
        df[type_of_article] = df.apply(lambda row: check_gazprom(row[type_of_article], row['text']), axis=1)

    # make rating for article
    print(f'-- rate {type_of_article} articles')
    if type_of_article == 'client':
        rating_system_dict = pd.read_excel(CLIENT_RATING_FILE_PATH).to_dict('records')
    else:
        rating_system_dict = pd.read_excel(COMMODITY_RATING_FILE_PATH).to_dict('records')
        for group in rating_system_dict:
            group['key words'] = ','.join([f' {word.strip().lower()}' for word in group['key words'].split(',')])

    df = rate_client(df, rating_system_dict) if type_of_article == 'client' else rate_commodity(df, rating_system_dict)

    # sum cluster labels
    df[f'{type_of_article}_score'] = df[f'{type_of_article}_labels'].map(
        lambda x: sum(list(map(int, list(x.split(';'))))))

    # delete unnecessary columns
    df.drop(columns=[f'{type_of_article}_labels', f'found_{type_of_article}'], inplace=True)

    return df


def deduplicate(df: pd.DataFrame, df_previous: pd.DataFrame, threshold: float = 0.51) -> pd.DataFrame:
    """
    Delete similar articles
    :param df: df with new article
    :param df_previous: df with article from database
    :param threshold: limit value for deduplicate
    :return: df without duplicates article
    """
    # clear from 0 (not relevant articles)
    df = df.query('not client_score.isnull() and client_score != 0 or '
                  'not commodity_score.isnull() and commodity_score != 0')

    # sort new batch
    df['count_client'] = df['client'].map(lambda x: len(list(x.split(sep=';'))) if (isinstance(x, str) and x) else 0)
    df['count_commodity'] = df['commodity'].map(
        lambda x: len(list(x.split(sep=';'))) if (isinstance(x, str) and x) else 0)
    df = df.sort_values(by=['count_client', 'count_commodity', 'client_score', 'commodity_score'],
                        ascending=[False, False, False, False]).reset_index(drop=True)
    df.drop(columns=['count_client', 'count_commodity'], inplace=True)

    # clean data for dn article
    print(f'len of articles in database -- {len(df_previous)}')
    df_previous['cleaned_data'] = df_previous['text'].map(lambda x: clean_data(x))

    # concat two columns with news from both DFs.
    df_concat = pd.concat([df_previous['cleaned_data'], df['cleaned_data']], ignore_index=True)

    # vectorizing news in new DF
    vectorizer = TfidfVectorizer()
    X_tf_idf = vectorizer.fit_transform(df_concat)
    X_tf_idf = X_tf_idf.toarray()

    # adding a column with unique/not unique label for all news.
    df['unique'] = None

    # iterating over current news batch
    start = len(df_previous['cleaned_data'])
    end = len(df_concat)
    for actual_pos in range(start, end):

        flag_unique = True
        for previous_pos in range(actual_pos):

            # if found two close news - adding not unique label,
            # modify threshold for comparing news in one batch and from the different ones
            current_threshold = threshold + 0.2 if previous_pos < start else threshold

            if X_tf_idf[actual_pos, :].dot(X_tf_idf[previous_pos, :].T) > current_threshold:
                flag_unique = False
                break

        df['unique'][actual_pos - start] = flag_unique

    # delete duplicates from current batch
    df = df[df['unique']]
    df.drop(columns=['unique'], inplace=True)

    return df


def summarization_by_chatgpt(full_text: str):
    # TODO: do by langchain
    """ Make summary by chatgpt """
    batch_size = 4000
    text_batches = []
    new_text_sum = ''
    if len(full_text+summarization_prompt) > batch_size:
        while len(full_text+summarization_prompt) > batch_size:
            point_index = full_text[:batch_size].rfind('.')
            text_batches.append(full_text[:point_index+1])
            full_text = full_text[point_index+1:]
    else:
        text_batches = [full_text]
    for batch in text_batches:
        gpt = ChatGPT()
        query_to_gpt = gpt.ask_chat_gpt(text=batch, prompt=summarization_prompt)
        new_text_sum = new_text_sum + query_to_gpt.choices[0].message.content

    return new_text_sum



