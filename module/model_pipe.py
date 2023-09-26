import re
from re import search
import pickle

import pandas as pd
import pymorphy2
from sklearn.feature_extraction.text import TfidfVectorizer

from config import summarization_prompt
from module.gigachat import GigaChat

CLIENT_BINARY_CLASSIFICATION_MODEL_PATH = 'model/binary_classification_best.pkl'
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


def find_names(text: str, table: pd.DataFrame, clean: bool) -> str:
    """
    Takes string and returns string with all found names (with ; separator) from provided Pandas DF.
    :param text: str. Current string in which we search for names.
    :param table: Pandas DF. Pandas DF with columns with names neeeded to be found. In one row all names - alternatives.
    :param clean: bool. Flag shows whether search applies to original or cleaned text.
    :return: str. String with found names separated with ; symbol.
    """
    # search for names in normal case and upper case.
    if clean:
        text = clean_data(text)
    answer = []
    for i in range(len(table)):
        for j in range(len(table.loc[i])):
            if type(table.loc[i][j]) == str:
                if search(f'({str(table.loc[i][j])}|{str(table.loc[i][j]).upper()})', text):
                    answer += [table.loc[i][0].lower()]
                    break
    return ';'.join(answer)


def rate_client(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes Pandas DF with current news batch and makes predictions over them.
    :param df: Pandas DF. Pandas DF with current news batch.
    :return: Pandas DF. Current news batch DF with added column 'client_labels'
    """
    # read binary classification model (relevant or not)
    binary_model = pickle.load(open(CLIENT_BINARY_CLASSIFICATION_MODEL_PATH, 'rb'))
    # read multiclass classification model
    multiclass_model = pickle.load(open(CLIENT_MULTY_CLASSIFICATION_MODEL_PATH, 'rb'))
    # predict relevance and adding a column with relevance label (1 or 0)
    df['relevance'] = binary_model.predict(df['cleaned_data'])
    # predict label from multiclass classification
    df['client_labels'] = multiclass_model.predict(df['cleaned_data'])
    # using relevance label condition
    df['client_labels'] = df.apply(
        lambda x: [str(x['client_labels'])] if ((len(x['client']) > 0) & (x['relevance'] == 1)) else [], axis=1)
    # delete relevance column
    df = df.drop(columns=['relevance'])
    # add regular expression labels
    # read range system
    range_system_companies = pd.read_excel(CLIENT_RATING_FILE_PATH)
    range_system_companies['key words'] = range_system_companies['key words'].map(lambda x: re.split(',', x))
    # iterating throug news
    for i, article in enumerate(df['cleaned_data']):
        # iterating through lists of keywords:
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
    return df


def rate_commodity(df: pd.DataFrame, use_relevance_model: bool, threshold=0.4) -> pd.DataFrame:
    """
    Taking a current news batch to rate. Adding new columns with found labels from commodity rate system.
    :param df: Pandas DF. Pandas DF with current news batch.
    :param use_relevance_model : bool. Flag shows whether binary relevance model should be applied.
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
    if use_relevance_model:
        # load binary relevance model
        binary_model = pickle.load(open(COM_BINARY_CLASSIFICATION_MODEL_PATH, 'rb'))
        # make predictions
        probs = binary_model.predict_proba(df['cleaned_data'])
        res = []
        for pair in probs:
            if (pair[1]) > threshold:
                res.append(1)
            else:
                res.append(0)
        df['relevance'] = res
        # apply model results
        df['commodity_labels'] = df.apply(lambda x: x['commodity_labels'] if (x['relevance'] == 1) else '0', axis=1)
        # delete relevance column
        df = df.drop(columns=['relevance'])
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

    giga_json_answer = giga_chat.ask_giga_chat(token=token, text=text, prompt=summarization_prompt)
    try:
        giga_answer = giga_json_answer.json()['choices'][0]['message']['content']
        if giga_answer in BAD_GIGA_ANSWERS:
            giga_answer = ''
    except Exception as e:
        print(e)
        giga_answer = ''

    return giga_answer


def change_bad_summary(row: pd.Series) -> str:
    """ Change summary if it is not exist """
    if row['text_sum']:
        return row['text_sum']
    elif row['title']:
        return row['title']
    else:
        first_sentence = row['text'][:row['text'].find('.') + 1]
        return first_sentence


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
    clean_flag = False

    # read file with subject name
    subject_names = pd.read_excel(ALTERNATIVE_NAME_FILE.format(type_of_article))

    # make_summarization
    if type_of_article == 'commodity':
        print('-- make summary for commodity')
        giga_chat = GigaChat()
        token = giga_chat.get_user_token()
        df['text_sum'] = df['text'].apply(lambda text: summarization_by_giga(giga_chat, token, text))
        df['text_sum'] = df.apply(lambda row: change_bad_summary(row), axis=1)
        clean_flag = True

    # find subject name in text and union with polyanalyst names
    print(f'-- find {type_of_article} names in article')
    df[f'found_{type_of_article}'] = df['text_sum'].map(lambda x: find_names(x, subject_names, clean_flag))
    df[type_of_article] = df.apply(lambda row: union_name(row[type_of_article], row[f'found_{type_of_article}']),
                                   axis=1)

    # make rating for article
    print(f'-- rate {type_of_article} articles')
    df = rate_client(df) if type_of_article == 'client' else rate_commodity(df, True)

    # sum cluster labels
    df[f'{type_of_article}_score'] = df[f'{type_of_article}_labels'].map(
        lambda x: sum(list(map(int, list(x.split(';'))))))

    # delete unnecessary columns
    df.drop(columns=[f'{type_of_article}_labels', f'found_{type_of_article}'], inplace=True)

    return df


def deduplicate(df: pd.DataFrame, df_previous: pd.DataFrame, threshold: float = 0.45) -> pd.DataFrame:
    """
    Delete similar articles
    :param df: df with new article
    :param df_previous: df with article from database
    :param threshold: limit value for deduplicate
    :return: df without duplicates article
    """
    # TODO: учитывать кол-во найденных клиентов при удалении новости - удалять где меньше клиентов
    # make clean data for previous dataframe
    df_previous['cleaned_data'] = df_previous['text'].map(lambda x: clean_data(x))
    print(f'len of articles in database -- {len(df_previous)}')
    # concat two columns with news from both DFs.
    df_concat = pd.DataFrame(pd.concat([df_previous['cleaned_data'], df['cleaned_data']], keys=['df_previous', 'df']),
                             columns=['cleaned_data'])
    df_concat = df_concat.reset_index(drop=True)
    # vectorize news in new DF.
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
    return df
