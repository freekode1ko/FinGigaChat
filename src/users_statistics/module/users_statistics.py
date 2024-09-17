"""Модуль сбора статистики по пользователям"""
from datetime import date
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, NullPool

from configs import config


class UserStatistics:
    """Класс сборщика статистики использования бота пользователями"""

    def __init__(self) -> None:
        """Объект для сбора статистики по пользователям"""
        self.engine = create_engine(config.psql_engine, poolclass=NullPool)  # FIXME унести в класс работы с БД

    def get_users(self) -> pd.DataFrame:
        """Возвращает справочник пользователей"""
        query = (
            'SELECT username AS telegram_user_name, user_id '
            # 'empl_fullname, department_name, empl_id '  # Просят передавать ФИО, отдел, табельный номер (нет в БД)
            'FROM registered_user '
            'ORDER BY username;'
        )

        users_df = pd.read_sql_query(query, con=self.engine)
        return users_df

    def get_stat(self, from_date: date = date.min, to_date: date = date.max) -> pd.DataFrame:
        """
        Возвращает статистику по использованию бота пользователями

        запрос на все действия(активные+пассивные) пользователя
        пассивные оцениваются, как 0
        :param from_date:   указывает начало периода, с которого будет собираться статистика (включительно)
        :param to_date:     указывает конец периода, до которого будет собираться статистика (включительно)
        :returns:           DataFrame[telegram_user_name, user_log.user_id, date, qty_of_prompts]
        """
        user_tbl = 'registered_user'
        query = (
            f'SELECT {user_tbl}.username AS telegram_user_name, user_log.user_id, '
            f"DATE(date) AS date, COUNT(CASE WHEN level='INFO' THEN 1 END) AS qty_of_prompts "
            f'FROM user_log '
            f'JOIN {user_tbl} ON {user_tbl}.user_id=user_log.user_id '
            f"WHERE (level='INFO' OR level='DEBUG') AND DATE(date) >= '{from_date}' AND DATE(date) <= '{to_date}' "
            f'GROUP BY {user_tbl}.username, user_log.user_id, DATE(date) '
            f'ORDER BY date;'
        )

        stat_df = pd.read_sql_query(query, con=self.engine)
        return stat_df

    def collect_bot_usage_over_period(self, file_path: Path, from_date: date = date.min, to_date: date = date.max) -> None:
        """
        Формирует статистику использования бота

        Сохраняет его в file_path в формате xlsx

        :param file_path: Путь до файла для сохранения статистики
        :param from_date: - указывает начало периода, с которого будет собираться статистика (включительно)
        :param to_date: - указывает конец периода, до которого будет собираться статистика (включительно)
        """
        stat_df = self.get_stat(from_date=from_date, to_date=to_date)
        stat_df.to_excel(file_path, sheet_name='Статистика использования')

    def collect_users_data(self, file_path: Path) -> None:
        """
        Формирует справочник пользователей

        Сохраняет его в file_path в формате xlsx

        :param file_path: Путь до файла для сохранения статистики
        """
        stat_df = self.get_users()
        stat_df.to_excel(file_path, sheet_name='Справочник пользователей')

    def _collect_activity(self) -> pd.DataFrame:
        """
        Собирает статистику активности пользователей

        :return: pd.DataFrame со статистикой
        """
        func_names = "','".join(config.STATISTICS_PROMPT_FUNCTIONS)
        query = (
            f"""
            SELECT registered_user.username AS telegram_user_name,
               user_log.user_id,
               registered_user.user_email,
               DATE(date) AS date,
               COUNT(CASE WHEN level='INFO' THEN 1 END) AS qty_of_prompts
            FROM user_log
            JOIN registered_user ON registered_user.user_id = user_log.user_id
            WHERE (level = 'INFO' OR level = 'DEBUG')
               AND func_name in ('{func_names}')
               AND DATE(date) >= '{config.STATISTICS_FROM_DATE}' -- замените на вашу начальную дату
               AND DATE(date) <= current_date -- замените на вашу конечную дату
               AND  user_log.user_id not in({','.join(config.STATISTICS_IGNORE_TG_IDS)})
            GROUP BY registered_user.username, user_log.user_id, DATE(date), user_email
            ORDER BY date DESC;
            """
        )
        return pd.read_sql_query(query, con=self.engine)

    def collect_activity(self, file_name: Path) -> None:
        """
        Собирает статистику активности пользователей.

        Сохраняет его в file_path в формате xlsx

        :param file_path: Путь до файла для сохранения статистики
        """
        stat_df = self._collect_activity()
        stat_df.to_excel(file_name, sheet_name='Промты', index=False)

    def _collect_users_subscriptions(self) -> pd.DataFrame:
        """
        Собирает статистику подписок пользователей.

        :return: pd.DataFrame со статистикой
        """
        query = (
            f"""
            SELECT
                wh.username,
                wh.user_email,
                u.user_id,
                c.qty_client_subs,
                r.qty_research_subs,
                i.qty_industry_subs,
                com.qty_commodity_subs,
                t.qty_tg_subs,
                current_date
            FROM
                (SELECT DISTINCT user_id FROM user_client_subscription
                 UNION
                 SELECT DISTINCT user_id FROM user_research_subscription
                 UNION
                 SELECT DISTINCT user_id FROM user_industry_subscription
                 UNION
                 SELECT DISTINCT user_id FROM user_commodity_subscription
                 UNION
                 SELECT DISTINCT user_id FROM user_telegram_subscription) AS u
            LEFT JOIN
                (SELECT user_id, COUNT(*) AS qty_client_subs
                 FROM user_client_subscription
                 GROUP BY user_id) AS c ON u.user_id = c.user_id
            LEFT JOIN
                (SELECT user_id, COUNT(*) AS qty_research_subs
                 FROM user_research_subscription
                 GROUP BY user_id) AS r ON u.user_id = r.user_id
            LEFT JOIN
                (SELECT user_id, COUNT(*) AS qty_industry_subs
                 FROM user_industry_subscription
                 GROUP BY user_id) AS i ON u.user_id = i.user_id
            LEFT JOIN
                (SELECT user_id, COUNT(*) AS qty_commodity_subs
                 FROM user_commodity_subscription
                 GROUP BY user_id) AS com ON u.user_id = com.user_id
            LEFT JOIN
                (SELECT user_id, COUNT(*) AS qty_tg_subs
                 FROM user_telegram_subscription
                 GROUP BY user_id) AS t ON u.user_id = t.user_id
            LEFT JOIN registered_user wh on u.user_id = wh.user_id
            WHERE COALESCE(
               c.qty_client_subs,
               r.qty_research_subs,
               i.qty_industry_subs,
               com.qty_commodity_subs,
               t.qty_tg_subs) IS NOT NULL
            AND u.user_id not in({','.join(config.STATISTICS_IGNORE_TG_IDS)})
            """
        )
        return pd.read_sql_query(query, con=self.engine)

    def collect_users_subscriptions(self, file_name: Path) -> None:
        """
        Собирает статистику подписок пользователей.

        Сохраняет его в file_path в формате xlsx

        :param file_path: Путь до файла для сохранения статистики
        """
        stat_df = self._collect_users_subscriptions()
        stat_df.to_excel(file_name, sheet_name='Подписки', index=False)

    def _collect_handler_calls(self) -> pd.DataFrame:
        """
        Собирает статистику вызовов обработчиков пользователей.

        :return: pd.DataFrame со статистикой
        """
        func_names = "','".join(config.STATISTICS_PROMPT_FUNCTIONS)
        query = (
            f"""SELECT * FROM (
                    SELECT registered_user.username AS telegram_user_name,
                        user_log.user_id,
                        registered_user.user_email,
                        DATE(date) AS date,
                        COUNT(CASE WHEN level = 'INFO' THEN 1 END) AS Qty_func_call
                    FROM user_log
                        JOIN registered_user ON registered_user.user_id = user_log.user_id
                    WHERE (level = 'INFO' OR level = 'DEBUG')
                        AND func_name not in ('{func_names}')
                        AND DATE(date) >= '{config.STATISTICS_FROM_DATE}' -- замените на вашу начальную дату
                        AND DATE(date) <= current_date -- замените на вашу конечную дату
                        AND user_log.user_id not in ({','.join(config.STATISTICS_IGNORE_TG_IDS)})
                    GROUP BY registered_user.username, user_log.user_id, DATE(date), user_email
                    ORDER BY date DESC
                ) as q
                WHERE Qty_func_call > 0"""
        )
        return pd.read_sql_query(query, con=self.engine)

    def collect_handler_calls(self, file_path: Path) -> None:
        """
        Собирает статистику вызовов обработчиков пользователями.

        Сохраняет его в file_path в формате xlsx

        :param file_path: Путь до файла для сохранения статистики
        """
        stat_df = self._collect_handler_calls()
        stat_df.to_excel(file_path, sheet_name='Функции', index=False)
