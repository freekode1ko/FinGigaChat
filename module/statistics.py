import os

import pandas as pd
from sqlalchemy import Engine, text


class UserStatistics:
    def __init__(self, engine: Engine):
        """Объект для сбора статистики по пользователям"""
        self.engine = engine  # FIXME унести в класс работы с БД

    def get_users(self) -> pd.DataFrame:
        """Возвращает справочник пользователей"""
        query = (
            'SELECT username AS telegram_user_name, user_id '
            # 'empl_fullname, department_name, empl_id '  # Просят передавать ФИО, отдел, табельный номер (нет в БД)
            'FROM whitelist '
            'ORDER BY username;'
        )

        with self.engine.connect() as conn:  # FIXME унести в класс работы с БД
            data = conn.execute(text(query))
            data = data.all()

        users_df = pd.DataFrame(data, columns=['telegram_user_name', 'user_id'])  # 'empl_fullname', 'department_name'])
        return users_df

    def get_stat(self) -> pd.DataFrame:
        """
        Возвращает статистику по использованию бота пользователями

        запрос на все действия(активные+пассивные) пользователя
        пассивные оцениваются, как 0
        """
        query = (
            'SELECT whitelist.username AS telegram_user_name, user_log.user_id, '
            'DATE(date) AS date, COUNT(CASE WHEN level=\'INFO\' THEN 1 END) AS qty_of_prompts '
            'FROM user_log '
            'JOIN whitelist ON whitelist.user_id=user_log.user_id '
            'WHERE level=\'INFO\' OR level=\'DEBUG\' '
            'GROUP BY whitelist.username, user_log.user_id, DATE(date) '
            'ORDER BY date;'
        )

        with self.engine.connect() as conn:  # FIXME унести в класс работы с БД
            data = conn.execute(text(query))
            data = data.all()

        stat_df = pd.DataFrame(data, columns=['telegram_user_name', 'user_id', 'date', 'qty_of_prompts'])
        return stat_df

    @staticmethod
    def save_stat_excel(save_df: pd.DataFrame, file_save_path: str, sheet_name: str = 'Лист 1') -> None:
        """Сохраняет передаваемый DataFrame в xlsx формате"""
        if not isinstance(save_df, pd.DataFrame):
            raise TypeError(f'Передан {type(save_df)=:}, ожидалcя тип "pandas.DataFrame"')
        if not isinstance(sheet_name, str):
            raise TypeError(f'Передан {type(sheet_name)=:}, ожидалcя тип "str"')
        if not isinstance(file_save_path, str):
            raise TypeError(f'Передан {type(file_save_path)=:}, ожидалcя тип "str"')

        with pd.ExcelWriter(file_save_path) as writer:
            save_df.to_excel(writer, sheet_name=sheet_name)

    def collect_bot_usage(self, file_save_path: str = None) -> None:
        """
        Формирует статистику использования бота и сохраняет ее по пути file_save_path
        (по умолчанию sources/tables/users_statistics.xlsx).
        """
        stat_df = self.get_stat()
        file_save_path = file_save_path or os.path.join('sources', 'tables', 'users_statistics.xlsx')
        self.save_stat_excel(stat_df, file_save_path=file_save_path, sheet_name='Статистика использования')

    def collect_users(self, file_save_path: str = None) -> None:
        """
        Формирует справочник пользователей и сохраняет его по пути file_save_path
        (по умолчанию sources/tables/users.xlsx).
        """
        stat_df = self.get_users()
        file_save_path = file_save_path or os.path.join('sources', 'tables', 'users.xlsx')
        self.save_stat_excel(stat_df, file_save_path=file_save_path, sheet_name='Справочник пользователей')
