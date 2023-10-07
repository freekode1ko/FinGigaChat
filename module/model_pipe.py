import re
from re import search
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


def find_bad_gas(names: str, clean_text: str) -> str:
    if 'газ' in names:
        if search('парниковый|углекислый ', clean_text):
            names_list = names.split(';')
            names_list.remove('газ')
            names = ';'.join(names_list)
    return names


def check_gazprom(names: str, clean_text: str) -> str:
    if 'газпром нефть' in names:
        if not search('газпром(?! нефть)', clean_text):
            names_list = names.split(';')
            names_list.remove('газпром')
            names = ';'.join(names_list)
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
    if title and search(stock_pattern, clean_text):
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
    text = text.strip()
    text = text.lower()
    #  lemmatization
    morph = pymorphy2.MorphAnalyzer()
    lemma = []
    text = re.split('\n | ', text)
    text = list(filter(None, text))
    for w in text:
        word = morph.parse(w)[0]
        lemma.append(word.normal_form)
    temp = '\n'.join(map(str, lemma))
    text = temp.split('\n')
    # stop words cleaning
    with open(STOP_WORDS_FILE_PATH, 'r', encoding='utf-8') as file:
        stop_words = list(map(str.rstrip, file.readlines()))
    text = [token for token in text if token not in stop_words and token != " "]
    text = ' '.join(text)
    return text


def find_names(text: str, table: pd.DataFrame, commodity_flag: bool = False) -> str:
    """
    Takes string and returns string with all found names (with ; separator) from provided Pandas DF.
    :param text: str. Current string in which we search for names.
    :param table: Pandas DF. Pandas DF with columns with names neeeded to be found. In one row all names - alternatives.
    :param commodity_flag: bool. Flag shows that it commodity text or not.
    :return: str. String with found names separated with ; symbol.
    """
    names_dict = {}
    # search for names in normal case and upper case.
    for i in range(len(table)):
        for j in range(len(table.loc[i])):
            if type(table.loc[i][j]) == str:
                re_findall = re.findall(f'({str(table.loc[i][j])}|{str(table.loc[i][j]).upper()})', text)
                if re_findall:
                    key_name = table.loc[i][0].lower()
                    names_dict[key_name] = len(re_findall)
                    break
    if commodity_flag:
        max_count = max(names_dict.values(), default=None)
        return ';'.join([key for key, val in names_dict.items() if (val > 1 or val == max_count)]) if max_count else ''
    else:
        return ';'.join(names_dict.keys())


def down_threshold(engine, type_of_article, names, threshold) -> float:
    """
    Down threshold if new contains rare subject
    :param engine: engine to database
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


def rate_client(df: pd.DataFrame, threshold: float = 0.65) -> pd.DataFrame:
    """
    Takes Pandas DF with current news batch and makes predictions over them.
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
    res = []
    for pair in probs:
        if (pair[1]) > threshold:
            res.append(1)
        else:
            res.append(0)
    df['relevance'] = res
    # predict label from multiclass classification
    df['client_labels'] = multiclass_model.predict(df['cleaned_data'])
    # using relevance label condition
    df['client_labels'] = df.apply(lambda x: [str(x['client_labels'])] if (len(x['client']) > 0) else [], axis=1)
    # add regular expression labels
    # read range system
    range_system_companies = pd.read_excel(CLIENT_RATING_FILE_PATH)
    range_system_companies['key words'] = range_system_companies['key words'].map(lambda x: re.split(',', x))
    # iterating throug news
    for i, article in enumerate(df['cleaned_data']):
        # iterating through lists of keywords:
        if df["relevance"][i] == 1:
            for j, list_of_key_words in enumerate(range_system_companies['key words']):
                # iterating through keywords in a list
                for key_word in list_of_key_words:
                    if re.search(key_word, article):
                        label = str(range_system_companies['label'][j])
                        if label not in df['client_labels'][i]:
                            df['client_labels'][i] += [label]
            if len(df['client_labels'][i]) == 0:
                df['client_labels'][i] = ['0']
            df['client_labels'][i] = ';'.join(sorted(df['client_labels'][i]))
        else:
            df['client_labels'][i] = '0'
    # delete relevance column
    df = df.drop(columns=['relevance'])
    # processing stck news
    df['client_labels'] = df.apply(lambda row: find_stock(row['title'], row['client'], row['cleaned_data'],
                                                          row['client_labels']), axis=1)
    return df


def rate_commodity(df: pd.DataFrame, threshold=0.5) -> pd.DataFrame:
    """
    Taking a current news batch to rate. Adding new columns with found labels from commodity rate system.
    :param df: Pandas DF. Pandas DF with current news batch.
    :param threshold : float. Threshold on binary commodity relevance model.
    :return: Pandas DF. Current news batch DF with added column 'commodity_labels'
    """
    # read commodity rating system
    rating_data = pd.read_excel(COMMODITY_RATING_FILE_PATH)
    rating_data['keys'] = rating_data['keys'].str.lower()
    rating_data['keys'] = rating_data['keys'].map(lambda x: re.split(',', x))
    # adding new column
    df['commodity_labels'] = ''
    # iterating through news
    for j, article in enumerate(df['cleaned_data']):
        # temp list for answer
        temp_ans = []
        # condition that current row contains any commodity found
        if len(df['commodity'][j]) != 0:
            # iterating through rows in rating system
            for i, keys in enumerate(rating_data['keys']):
                # iterating throw keywords
                for key in keys:
                    # adding label
                    if search(key, str(article)):
                        if (str(key)) != '':
                            temp_ans += [rating_data['label'][i]]
                            break
        if len(temp_ans) == 0:
            temp_ans = [str(0)]
        df['commodity_labels'][j] = ';'.join(str(x) for x in temp_ans)

    # load binary relevance model
    with open(COM_BINARY_CLASSIFICATION_MODEL_PATH, 'rb') as f:
        binary_model = pickle.load(f)
    # make predictions
    probs = binary_model.predict_proba(df['cleaned_data'])
    res = []
    engine = create_engine(psql_engine, pool_pre_ping=True)
    for index, pair in enumerate(probs):
        commodity_names = df['commodity'].iloc[index].split(';')
        local_threshold = down_threshold(engine, 'commodity', commodity_names, threshold)
        if (pair[1]) > local_threshold:
            res.append(1)
        else:
            res.append(0)
    df['relevance'] = res
    # apply model results
    df['commodity_labels'] = df.apply(lambda x: x['commodity_labels'] if (x['relevance'] == 1) else '0', axis=1)
    # delete relevance column
    df = df.drop(columns=['relevance'])
    # processing stock news
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
    if row['text_sum']:
        return row['text_sum']
    # TODO: если заголовки не будут отображаться в боте, то раскомментировать
    # elif row['title']:
    #     return row['title']
    else:
        print(f'GigaChat did not make summary for {row["link"]}')
        first_sentence = row['text'][:row['text'].find('.') + 1]
        return first_sentence


def model_func(df: pd.DataFrame, type_of_article: str) -> pd.DataFrame:
    """
    Find subject names which contain in article and make score for these articles
    :param df: dataframe with article
    :param type_of_article: type of article (client or commodity)
    :return: df with subject name and score
    """
    # TODO: рефакторинг !!!!
    # add column with clean text
    print('-- cleaned data')
    df['cleaned_data'] = df['text'].map(lambda x: clean_data(x))

    # read file with subject name
    subject_names = pd.read_excel(ALTERNATIVE_NAME_FILE.format(type_of_article))

    # make_summarization
    print(f'-- make summary for {type_of_article}')
    giga_chat = GigaChat()
    token = giga_chat.get_user_token()
    df['text_sum'] = df['text'].apply(lambda text: summarization_by_giga(giga_chat, token, text))
    df['text_sum'] = df.apply(lambda row: change_bad_summary(row), axis=1)

    # find subject name in text
    print(f'-- find {type_of_article} names in article')

    if type_of_article == 'commodity':

        df[f'found_{type_of_article}'] = df['cleaned_data'].map(lambda x: find_names(x, subject_names, True))
        df[f'found_{type_of_article}'] = df.apply(lambda row: find_bad_gas(row[f'found_{type_of_article}'],
                                                                           row['cleaned_data']), axis=1)
        df[type_of_article] = df[f'found_{type_of_article}']

    else:

        df[f'found_{type_of_article}'] = df['text'].map(lambda x: find_names(x, subject_names))
        df[type_of_article] = df.apply(lambda row: union_name(row[type_of_article], row[f'found_{type_of_article}']), axis=1)
        df[type_of_article] = df.apply(lambda row: check_gazprom(row[type_of_article], row['cleaned_data']), axis=1)

    # make rating for article
    print(f'-- rate {type_of_article} articles')
    df = rate_client(df) if type_of_article == 'client' else rate_commodity(df)

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
    # sort new batch
    df['count_client'] = df['client'].map(lambda x: len(list(x.split(sep=';'))) if (isinstance(x, str) and len(x) > 0) else 0)
    df['count_commodity'] = df['commodity'].map(lambda x: len(list(x.split(sep=';'))) if (isinstance(x, str) and len(x) > 0) else 0)
    df = df.sort_values(by=['count_client', 'count_commodity', 'client_score', 'commodity_score'],
                        ascending=[False, False, False, False])
    df = df.reset_index(drop=True)
    df.drop(columns=['count_client', 'count_commodity'], inplace=True)
    # concat two columns with news from both DFs.
    df_previous['cleaned_data'] = df_previous['text'].map(lambda x: clean_data(x))
    print(f'len of articles in database -- {len(df_previous)}')
    # concat two columns with news from both DFs.
    df_concat = pd.DataFrame(pd.concat([df_previous['cleaned_data'], df['cleaned_data']], keys=['df_previous', 'df']),
                             columns=['cleaned_data'])
    df_concat = df_concat.reset_index(drop=True)
    # vectorizing news in new DF
    vectorizer = TfidfVectorizer()
    X_tf_idf = vectorizer.fit_transform(df_concat['cleaned_data'])
    X_tf_idf = X_tf_idf.toarray()
    # adding a column with unique/not unique label for all news.
    df['unique'] = ''
    # iterating over current news batch
    for actual_pos in range(len(df_previous['cleaned_data']), len(df_concat['cleaned_data'])):
        flag_unique = True
        for previous_pos in range(actual_pos):
            # if found two close news - adding not unique label
            # modify threshold for comparing news in one batch and from the different ones
            current_threshold = threshold
            if previous_pos < len(df_previous['cleaned_data']):
                current_threshold += 0.2
            if X_tf_idf[actual_pos, :].dot(X_tf_idf[previous_pos, :].T) > current_threshold:
                flag_unique = False
                break
        df['unique'][actual_pos - len(df_previous['cleaned_data'])] = flag_unique
    # delete duplicates from current batch
    df = df.drop(df[df.unique == False].index)
    df = df.reset_index(drop=True)
    df = df.drop(columns=['unique', 'cleaned_data'])
    df.to_excel('Комоды квартал через все модели (без саммари).xlsx', index=False)
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



