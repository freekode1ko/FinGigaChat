import pandas as pd

from db import database


__table_name__ = 'parser_source'


def get_parser_data() -> pd.DataFrame:
    """
    Вынимает из базы информацию по парсерам из таблиц parser_source, source_group
    return: DataFrame[[param_value, last_update_datetime, previous_update_datetime, parser_type]]
    """
    query = (
        f'SELECT p.name as param_value, p.last_update_datetime, p.previous_update_datetime, sg.name as parser_type '
        f'FROM parser_source p '
        f'JOIN source_group sg ON p.source_group_id = sg.id '
    )
    df_parsers = pd.read_sql(query, con=database.engine)
    return df_parsers
