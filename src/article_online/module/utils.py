"""Доп функции для обработки новостей"""
import pandas as pd

from db.database import engine


def get_alternative_names_pattern_commodity(alt_names: pd.DataFrame) -> dict[str, str]:
    """
    Создает регулярные выражения для коммодов.

    :param: alt_names: Таблица с комодами и их альтернативными названиями.
    :return:           Словарь с названиями для поиска регуляркой.
    """
    alter_names_dict = dict()
    table_subject_list = alt_names.values.tolist()
    for i, alt_names_list in enumerate(table_subject_list):
        clear_alt_names = [_ for _ in alt_names_list if not pd.isna(_)]
        names_pattern_base = '|'.join(clear_alt_names)
        names_patter_upper = '|'.join(el.upper() for el in clear_alt_names)
        key = clear_alt_names[0]
        alter_names_dict[key] = f'({names_pattern_base}|{names_patter_upper})'
    return alter_names_dict


def add_endings(clear_names_list: list[str]) -> list[str]:
    """
    Добавляет окончания к именам клиента в списке альтернативных имен.

    :param clear_names_list:   Список имен клиентов.
    :return:                   Измененный список имен клиентов.
    """
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


def get_alternative_names_pattern_client(alt_names: pd.DataFrame) -> dict[str, str]:
    """
    Создает регулярные выражения для клиентов.

    :param alt_names:   Таблица с клиентами и их альтернативными названиями.
    :return:            Словарь с названиями для поиска регуляркой.
    """
    alter_names_dict = dict()
    table_subject_list = alt_names.values.tolist()
    for alt_names_list in table_subject_list:
        clear_alt_names = [_ for _ in alt_names_list if not pd.isna(_)]
        key = clear_alt_names[0]

        clear_alt_names = add_endings(clear_alt_names)
        clear_alt_names_upper = add_endings([el.upper() for el in clear_alt_names])

        names_pattern_base = r'( |\. |, |\) )|'.join(clear_alt_names)
        names_pattern_base += r'( |\. |, |\) )'
        names_patter_upper = r'( |\. |, |\) )|'.join(clear_alt_names_upper)
        names_patter_upper += r'( |\. |, |\) )'
        alter_names_dict[key] = f'({names_pattern_base}|{names_patter_upper})'.replace('+', r'\+')

    return alter_names_dict


def create_alternative_names_dict(alt_names: pd.DataFrame) -> dict:
    """
    Создает словарь с альтернативными названиями клиентов.

    :param alt_names:   pd.DataFrame с альтернативными названиями клиентов.
    :return:            Словарь с названиями клиентов.
    """
    alter_names_dict = dict()
    table_subject_list = alt_names.values.tolist()
    for alt_names_list in table_subject_list:
        clear_alt_names = [_ for _ in alt_names_list if not pd.isna(_)]
        key = clear_alt_names[0].strip().lower()
        alter_names_dict[key] = ','.join(clear_alt_names)
    return alter_names_dict


def create_client_industry_dict() -> dict:
    """
    Создает словарь с названиями индустрий клиента.

    :return: Словарь индустрий клиентов.
    """
    query = (
        'select industry.name as industry_name, client.name as client_name from client '
        'join industry on client.industry_id = industry.id'
    )
    df = pd.read_sql(query, engine)
    df.index = df['client_name'].str.lower().str.strip()
    client_industry_dict = df['industry_name'].to_dict()
    return client_industry_dict


def modify_commodity_rating_system_dict(commodity_rating_system_dict: list[dict]) -> list[dict]:
    """
    Изменяет словарь с названиями коммодов в нужном формате.

    :param commodity_rating_system_dict: Словарь с названиями коммодов.
    :return:                             Измененный словарь с названиями коммодов.
    """
    for group in commodity_rating_system_dict:
        group['key words'] = ','.join(f' {word.strip().lower()}' for word in group['key words'].split(','))
    return commodity_rating_system_dict
