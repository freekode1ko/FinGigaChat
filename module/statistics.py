import config
import pandas as pd
from datetime import date
from pathlib import Path
from sqlalchemy import create_engine, NullPool


class UserStatistics:
    def __init__(self):
        """Объект для сбора статистики по пользователям"""
        self.engine = create_engine(config.psql_engine, poolclass=NullPool)  # FIXME унести в класс работы с БД

    def get_users(self) -> pd.DataFrame:
        """Возвращает справочник пользователей"""
        query = (
            'SELECT username AS telegram_user_name, user_id '
            # 'empl_fullname, department_name, empl_id '  # Просят передавать ФИО, отдел, табельный номер (нет в БД)
            'FROM whitelist '
            'ORDER BY username;'
        )

        users_df = pd.read_sql_query(query, con=self.engine)
        return users_df

    def get_stat(self, from_date: date = date.min, to_date: date = date.max) -> pd.DataFrame:
        """
        Возвращает статистику по использованию бота пользователями

        запрос на все действия(активные+пассивные) пользователя
        пассивные оцениваются, как 0
        :param from_date: - указывает начало периода, с которого будет собираться статистика (включительно)
        :param to_date: - указывает конец периода, до которого будет собираться статистика (включительно)
        """
        query = (
            f'SELECT whitelist.username AS telegram_user_name, user_log.user_id, '
            f"DATE(date) AS date, COUNT(CASE WHEN level='INFO' THEN 1 END) AS qty_of_prompts "
            f'FROM user_log '
            f'JOIN whitelist ON whitelist.user_id=user_log.user_id '
            f"WHERE (level='INFO' OR level='DEBUG') AND DATE(date) >= '{from_date}' AND DATE(date) <= '{to_date}' "
            f'GROUP BY whitelist.username, user_log.user_id, DATE(date) '
            f'ORDER BY date;'
        )

        stat_df = pd.read_sql_query(query, con=self.engine)
        return stat_df

    @staticmethod
    def save_stat_excel(save_df: pd.DataFrame, file_name: Path, *args, **kwargs) -> None:
        """
        Сохраняет передаваемый DataFrame в xlsx формате в папке config.STATISTICS_PATH

        :param save_df: DataFrame, данные которого будут сохранены в формате xlsx
        :param file_name: Имя файла, который будет создан в config.STATISTICS_PATH с сохраненными данными
        """
        stat_path = Path(config.STATISTICS_PATH)

        if not stat_path.exists():
            stat_path.mkdir()

        file_save_path = Path(stat_path, file_name)
        save_df.to_excel(file_save_path, *args, **kwargs)

    def collect_bot_usage_over_period(
            self, file_name: Path, from_date: date = date.min, to_date: date = date.max
    ) -> None:
        """
        Формирует статистику использования бота и сохраняет ее в config.STATISTICS_PATH
        в файле file_name в формате xlsx

        :param file_name: Имя файла, который будет создан в config.STATISTICS_PATH с данными собранной статистики
        :param from_date: - указывает начало периода, с которого будет собираться статистика (включительно)
        :param to_date: - указывает конец периода, до которого будет собираться статистика (включительно)
        """
        stat_df = self.get_stat(from_date=from_date, to_date=to_date)
        self.save_stat_excel(stat_df, file_name=file_name, sheet_name='Статистика использования')

    def collect_users_data(self, file_name: Path) -> None:
        """
        Формирует справочник пользователей и сохраняет его в config.STATISTICS_PATH
        в файле file_name в формате xlsx

        :param file_name: Имя файла, который будет создан в config.STATISTICS_PATH со списков пользователей системы
        """
        stat_df = self.get_users()
        self.save_stat_excel(stat_df, file_name=file_name, sheet_name='Справочник пользователей')
