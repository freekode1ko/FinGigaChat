import pandas as pd
from datetime import date
from pathlib import Path
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

    def get_stat(self, from_date: date = None, to_date: date = None) -> pd.DataFrame:
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
            'WHERE (level=\'INFO\' OR level=\'DEBUG\') {period_condition} '
            'GROUP BY whitelist.username, user_log.user_id, DATE(date) '
            'ORDER BY date;'
        )

        period_condition = ''

        if from_date:
            period_condition += f'AND DATE(date) >= \'{from_date.strftime("%Y-%m-%d")}\' '
        if to_date:
            period_condition += f'AND DATE(date) <= \'{to_date.strftime("%Y-%m-%d")}\' '

        query = query.format(period_condition=period_condition)

        with self.engine.connect() as conn:  # FIXME унести в класс работы с БД
            data = conn.execute(text(query))
            data = data.all()

        stat_df = pd.DataFrame(data, columns=['telegram_user_name', 'user_id', 'date', 'qty_of_prompts'])
        return stat_df

    @staticmethod
    def save_stat_excel(save_df: pd.DataFrame, file_save_path: Path, sheet_name: str = 'Лист 1') -> None:
        """Сохраняет передаваемый DataFrame в xlsx формате"""
        save_df.to_excel(file_save_path, sheet_name=sheet_name)

    def collect_bot_usage(self, file_save_path: Path) -> None:
        """Формирует статистику использования бота и сохраняет ее по пути file_save_path"""
        stat_df = self.get_stat()
        self.save_stat_excel(stat_df, file_save_path=file_save_path, sheet_name='Статистика использования')

    def collect_bot_usage_over_period(self, file_save_path: Path, from_date: date, to_date: date) -> None:
        """Формирует статистику использования бота и сохраняет ее по пути file_save_path"""
        stat_df = self.get_stat(from_date=from_date, to_date=to_date)
        self.save_stat_excel(stat_df, file_save_path=file_save_path, sheet_name='Статистика использования')

    def collect_users_data(self, file_save_path: Path) -> None:
        """Формирует справочник пользователей и сохраняет его по пути file_save_path"""
        stat_df = self.get_users()
        self.save_stat_excel(stat_df, file_save_path=file_save_path, sheet_name='Справочник пользователей')
