import asyncio
import datetime
import json
import re
import time
import warnings
from typing import Dict, List, Optional, Tuple

import asyncpg
import numpy as np
import pandas as pd
import requests as req
import schedule
from selenium.webdriver.remote.webdriver import WebDriver
from sqlalchemy.orm import sessionmaker

import module.crawler as crawler
import module.data_transformer as dt
from configs import config
from db.database import engine
from log import sentry
from log.logger_base import Logger, selector_logger
from parsers.cib import ResearchAPIParser, ResearchParser
from parsers.user_emulator import InvestingAPIParser, MetalsWireParser
from sql_model.commodity import Commodity
from sql_model.commodity_pricing import CommodityPricing
from utils.selenium_utils import get_driver


class ResearchesGetter:
    def __init__(self, logger):
        self.logger = logger
        parser_obj = crawler.Parser(self.logger)
        transformer_obj = dt.Transformer()
        psql_engine = config.psql_engine
        list_of_companies = config.list_of_companies
        data_market_base_url = config.data_market_base_url

        self.psql_engine = psql_engine
        self.parser_obj = parser_obj
        self.transformer_obj = transformer_obj
        self.list_of_companies = list_of_companies
        self.data_market_base_url = data_market_base_url
        self.commodities = self.transformer_obj.url_updater()
        self.metals_wire_table = None
        self.__driver = None

    def set_driver(self, driver: WebDriver):
        self.__driver = driver

    def graph_collector(self, url, session: req.sessions.Session, name=''):
        self.logger.info(f'Сборка графиков. Источник: {url}')
        if 'api.investing' in url:
            try:
                InvAPI_obj = ue.InvestingAPIParser(self.__driver, self.logger)
                data = InvAPI_obj.get_graph_investing(url)
            except Exception as e:
                self.logger.error('При загрузке данных для графика с investing.com произошла ошибка: %s', e)
                self.__driver = get_driver(self.logger)
                raise Exception('get graph investing error: %s' % e)  # FIXME криво, подумать еще

            if data is not None:
                self.transformer_obj.five_year_graph(data, name)

        elif 'metals-wire' in url:
            euro_standard, page_html = self.parser_obj.get_html(url, session)
            page_html = json.loads(page_html)
            data = pd.DataFrame()
            for day in page_html:
                day['x'] = day['time']
                day['date'] = dt.Transformer.unix_to_default(day['time'])
                row = {'date': day['date'], 'x': day['x'], 'y': day['close']}
                data = pd.concat([data, pd.DataFrame(row, index=[0])], ignore_index=True)

            self.transformer_obj.five_year_graph(data, name)

        elif 'profinance' in url:
            response = session.get(url)
            name = name.replace('/', '_')
            name = name.replace(' ', '_')
            name = name.split(',')
            name = f'{name[0]}_graph.png'
            with open(f'./sources/img/{name}', 'wb') as f:
                f.write(response.content)
        else:
            name = url.split('/')[-1]
            euro_standard, page_html = self.parser_obj.get_html(url, session)
            auth = re.findall(r"TESecurify = ('.+');", page_html)
            graph_url = (
                '{}chart?s=lmahds03:com&'
                'span=5y&'
                'securify=new&'
                'url=/commodity/{}&'
                'AUTH={}&'
                'ohlc=0'.format(self.data_market_base_url, name, auth[-1][1:-1])
            )
            data = req.get(graph_url, verify=False)

            self.transformer_obj.five_year_graph(data, name)

    def get_metals_wire_table_data(self):
        try:
            metals_wire_parser_obj = MetalsWireParser(self.__driver, self.logger)
            self.metals_wire_table = metals_wire_parser_obj.get_table_data()
        except Exception as e:
            self.__driver = get_driver(self.logger)
            self.logger.critical('При сборке табличных данных для MetalsWire произошла ошибка: %s', e)

    def commodities_plot_collect(self, session: req.sessions.Session):
        # FIXME что делать, если тут произошла ошибка? Пока пропускаю elif
        self.get_metals_wire_table_data()
        commodity_pricing = pd.DataFrame()
        self.logger.info(f'Сборка по сырью {len(self.commodities)}')
        for commodity in self.commodities:
            link = self.commodities[commodity]['links'][0]
            name = self.commodities[commodity]['naming']
            self.logger.info(commodity)
            self.logger.info(self.commodities[commodity]['links'][0])

            # FIXME что делать, если мы не смогли сохранить картинку, потому что возникла ошибка получения данных?
            try:
                self.graph_collector(link, session, commodity)
            except Exception as e:
                self.logger.warning(f'Не удалось получить графики для {commodity}: %s', e)
                continue

            if len(self.commodities[commodity]['links']) > 1:
                url = self.commodities[commodity]['links'][1]

                try:
                    InvAPI_obj = InvestingAPIParser(self.__driver, self.logger)
                    streaming_price = InvAPI_obj.get_streaming_chart_investing(url)
                except Exception as e:
                    self.logger.error(
                        f'При обработке данных для стримингового графика с investing.com ({url}) произошла ошибка: %s',
                        e,
                    )
                    self.__driver = get_driver(self.logger)
                    continue

                ''' What's the difference?
                dict_row = {'Resource': commodity.split(',')[0], 'SPOT': round(float(streaming_price), 1),
                            'alias': self.commodities[commodity]['alias'].lower().strip(),
                            'unit': self.commodities[commodity]['measurables']}
                '''
                dict_row = {
                    'Resource': commodity.split(',')[0],
                    'SPOT': round(float(streaming_price), 1),
                    'alias': self.commodities[commodity]['alias'].lower().strip(),
                    'unit': self.commodities[commodity]['measurables'],
                }

                commodity_pricing = pd.concat([commodity_pricing, pd.DataFrame(dict_row, index=[0])], ignore_index=True)

            elif self.commodities[commodity]['naming'] != 'Gas' and self.metals_wire_table is not None:
                to_take = self.commodities[commodity]['to_take'] + 1

                table = self.metals_wire_table
                row_index = table.index[table['Resource'] == name][0]
                dict_row = {}
                for key in table.iloc[row_index][:to_take].keys():
                    dict_row[key] = table.iloc[row_index][:to_take][key]

                for key in dict_row:
                    if key not in ['Resource']:
                        if dict_row[key].strip() != '':
                            num = round(float(dict_row[key].strip().split('%')[0]), 1)
                            dict_row[key] = num
                        else:
                            dict_row[key] = np.nan

                dict_row['alias'] = self.commodities[commodity]['alias'].lower().strip()
                dict_row['unit'] = self.commodities[commodity]['measurables']
                dict_row['Resource'] = commodity.split(',')[0]
                commodity_pricing = pd.concat([commodity_pricing, pd.DataFrame(dict_row, index=[0])], ignore_index=True)

        commodity = pd.read_sql_query('SELECT * FROM commodity', con=engine)
        commodity_ids = pd.DataFrame()

        for i, row in commodity_pricing.iterrows():
            commodity_id = commodity[commodity['name'] == row['alias']]['id']

            dict_row = {'commodity_id': commodity_id.values[0]}
            commodity_ids = pd.concat([commodity_ids, pd.DataFrame(dict_row, index=[0])], ignore_index=True)

        df_combined = pd.concat([commodity_pricing, commodity_ids], axis=1)
        df_combined = df_combined.rename(
            columns={'Resource': 'subname', 'SPOT': 'price', '1M diff.': 'm_delta', 'YTD diff.': 'y_delta', "Cons-s'23": 'cons'}
        )
        df_combined = df_combined.loc[:, ~df_combined.columns.str.contains('^Unnamed')]
        df_combined = df_combined.drop(columns=['alias'])

        Session = sessionmaker(bind=engine)
        with Session() as session:
            q = session.query(CommodityPricing)

            if q.count() == 28:
                for i, row in df_combined.iterrows():
                    session.query(CommodityPricing).filter(CommodityPricing.subname == row['subname']).update(
                        {
                            'price': row['price'],
                            'm_delta': np.nan,
                            'y_delta': row['y_delta'],
                            'cons': row['cons'],
                        }
                    )
                    # update({"price": row['price'], "m_delta": row['m_delta'],
                    # "y_delta": row['y_delta'], "cons": row['cons']})

                    session.commit()
            else:
                for i, row in df_combined.iterrows():
                    commodity_price_obj = CommodityPricing(
                        commodity_id=int(row['commodity_id']),
                        subname=row['subname'],
                        unit=row['unit'],
                        price=row['price'],
                        m_delta=np.nan,
                        # m_delta=row['m_delta'],
                        y_delta=row['y_delta'],
                        cons=row['cons'],
                    )
                    session.merge(commodity_price_obj, load=True)
                    session.commit()

                q_gas = session.query(Commodity).filter(Commodity.name == 'газ')
                commodity_price_obj = CommodityPricing(
                    commodity_id=q_gas[0].id, subname='Газ', unit=np.nan, price=np.nan, m_delta=np.nan, y_delta=np.nan, cons=np.nan
                )
                session.merge(commodity_price_obj, load=True)
                session.commit()

    def collect_research(self) -> Tuple[Optional[dict], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        Collect all type of reviews from CIB Research
        And get page html with fin data about companies from CIB Research
        :return: dict with data reviews, dict with html page
        """

        self.logger.info('Начало сборки с research')
        economy, money, comm = 'econ', 'money', 'comm'

        try:
            authed_user = ResearchParser(self.__driver, self.logger)
        except Exception as e:
            error_msg = 'Не удалось авторизоваться на Sberbank CIB Research: %s'
            self.logger.error(error_msg, e)
            raise Exception(error_msg % e)

        # economy
        try:
            key_eco_table = authed_user.get_key_econ_ind_table()
        except Exception as e:
            self.__driver = get_driver(logger=self.logger)
            authed_user = ResearchParser(self.__driver, self.logger)
            self.logger.error('При сборе ключевых показателей компании произошла ошибка: %s', e)
            key_eco_table = None

        try:
            eco_day = authed_user.get_reviews(url_part=economy, tab='Ежедневные', title='Экономика - Sberbank CIB')
        except Exception as e:
            self.__driver = get_driver(logger=self.logger)
            authed_user = ResearchParser(self.__driver, self.logger)
            self.logger.error('При сборе отчетов по "Экономика - Sberbank CIB" во вкладке "Ежедневные" произошла ошибка: %s', e)
            eco_day = None

        try:
            eco_month = authed_user.get_reviews(
                url_part=economy,
                tab='Все',
                title='Экономика - Sberbank CIB',
                name_of_review='Экономика России. Ежемесячный обзор',
            )
        except Exception as e:
            self.__driver = get_driver(logger=self.logger)
            authed_user = ResearchParser(self.__driver, self.logger)
            self.logger.error(
                'При сборе отчетов по "Экономика - Sberbank CIB" во вкладке "Все", '
                'name_of_review="Экономика России. Ежемесячный обзор" произошла ошибка: %s',
                e,
            )
            eco_month = None
        self.logger.info('Блок по экономике собран')

        # bonds
        try:
            bonds_day = authed_user.get_reviews(
                url_part=money,
                tab='Ежедневные',
                title='FX &amp; Ставки - Sberbank CIB',
                name_of_review='Валютный рынок и процентные ставки',
                type_of_review='bonds',
                count_of_review=2,
            )
        except Exception as e:
            self.__driver = get_driver(logger=self.logger)
            authed_user = ResearchParser(self.__driver, self.logger)
            self.logger.error(
                'При сборе отчетов по "FX &amp; Ставки - Sberbank CIB" во вкладке "Ежедневные", '
                'name_of_review="Валютный рынок и процентные ставки", '
                'type_of_review="bonds", '
                'count_of_review=2 произошла ошибка: %s',
                e,
            )
            bonds_day = None

        try:
            bonds_month = authed_user.get_reviews(
                url_part=money,
                tab='Все',
                title='FX &amp; Ставки - Sberbank CIB',
                name_of_review='Обзор рынка процентных ставок',
            )
        except Exception as e:
            self.__driver = get_driver(logger=self.logger)
            authed_user = ue.ResearchParser(self.__driver, self.logger)
            self.logger.error(
                'При сборе отчетов по "FX &amp; Ставки - Sberbank CIB" во вкладке "Все",'
                'name_of_review="Обзор рынка процентных ставок" произошла ошибка: %s',
                e,
            )
            bonds_month = None
        self.logger.info('Блок по ставкам собран')

        # exchange
        try:
            exchange_day = authed_user.get_reviews(
                url_part=money,
                tab='Ежедневные',
                title='FX &amp; Ставки - Sberbank CIB',
                name_of_review='Валютный рынок и процентные ставки',
                type_of_review='exchange',
                count_of_review=2,
            )
        except Exception as e:
            self.__driver = get_driver(logger=self.logger)
            authed_user = ResearchParser(self.__driver, self.logger)
            self.logger.error(
                'При сборе отчетов по "FX &amp; Ставки - Sberbank CIB" во вкладке "Ежедневные", '
                'name_of_review="Валютный рынок и процентные ставки", '
                'type_of_review="exchange",'
                'count_of_review=2 произошла ошибка: %s',
                e,
            )
            exchange_day = None
        try:
            exchange_month_uan = authed_user.get_reviews(
                url_part=economy, tab='Все', title='Экономика - Sberbank CIB', name_of_review='Ежемесячный обзор по юаню'
            )
        except Exception as e:
            self.__driver = get_driver(logger=self.logger)
            authed_user = ResearchParser(self.__driver, self.logger)
            self.logger.error(
                'При сборе отчетов по "Экономика - Sberbank CIB" во вкладке "Все",'
                'name_of_review="Ежемесячный обзор по юаню" произошла ошибка: %s',
                e,
            )
            exchange_month_uan = None
        try:
            exchange_month_soft = authed_user.get_reviews(
                url_part=economy,
                tab='Все',
                title='Экономика - Sberbank CIB',
                name_of_review='Ежемесячный обзор по мягким валютам'
            )
        except Exception as e:
            self.__driver = get_driver(logger=self.logger)
            authed_user = ResearchParser(self.__driver, self.logger)
            self.logger.error(
                'При сборе отчетов по "Экономика - Sberbank CIB" во вкладке "Все", '
                'name_of_review="Ежемесячный обзор по мягким валютам" произошла ошибка: %s',
                e,
            )
            exchange_month_soft = None
        self.logger.info('Блок по курсам валют собран')

        # commodity
        try:
            commodity_day = authed_user.get_reviews(
                url_part=comm,
                tab='Ежедневные',
                title='Сырьевые товары - Sberbank CIB',
                name_of_review='Сырьевые рынки',
                type_of_review='commodity',
            )
            self.logger.info('Блок по сырью собран')
        except Exception as e:
            self.__driver = get_driver(logger=self.logger)
            authed_user = ResearchParser(self.__driver, self.logger)
            self.logger.error(
                'При сборе отчетов по "Сырьевые товары - Sberbank CIB" во вкладке "Ежедневные", '
                'name_of_review="Сырьевые рынки", '
                'type_of_review="commodity" произошла ошибка: %s',
                e,
            )
            commodity_day = None

        exchange_month = exchange_month_uan + exchange_month_soft
        reviews = {
            'Economy day': eco_day,
            'Economy month': eco_month,
            'Bonds day': bonds_day,
            'Bonds month': bonds_month,
            'Exchange day': exchange_day,
            'Exchange month': exchange_month,
            'Commodity day': commodity_day,
        }

        clients_table = authed_user.get_companies_financial_indicators_table()
        self.__driver = authed_user.driver
        self.logger.info('Страница с клиентами собрана')

        authed_user.get_industry_reviews()
        self.__driver = authed_user.driver
        self.logger.info('Страница с отчетами по направлениям собрана')

        try:
            authed_user.get_weekly_review()
            self.logger.info('Weekly pulse собран')
        except Exception as e:
            self.__driver = get_driver(logger=self.logger)
            self.logger.error('При сборе отчетов weekly pulse произошла ошибка: %s', e)

        return reviews, key_eco_table, clients_table

    def save_reviews(self, reviews_to_save: Dict[str, List[Tuple]]) -> None:
        """
        Save all reviews into the database.
        :param reviews_to_save: dict of list of the reviews
        """
        # TODO: мб сделать одну таблицу для обзоров ?

        table_name_for_review = {
            'Economy day': 'report_eco_day',
            'Economy month': 'report_eco_mon',
            'Bonds day': 'report_bon_day',
            'Bonds month': 'report_bon_mon',
            'Exchange day': 'report_exc_day',
            'Exchange month': 'report_exc_mon',
            'Commodity day': 'report_met_day',
        }

        for review_name, table_name in table_name_for_review.items():
            reviews_list = reviews_to_save.get(review_name)

            if reviews_list is not None:
                pd.DataFrame(reviews_list).to_sql(table_name, if_exists='replace', index=False, con=engine)
                self.logger.info(f'Таблица {table_name} записана: {reviews_list}')
            else:
                self.logger.warning(f'Таблица {table_name} не обновлена: {reviews_list}')

        self.logger.info('Все собранные отчеты с research записаны')

    def save_clients_financial_indicators(self, clients_table):
        if clients_table is not None:
            clients_table.to_sql('financial_indicators', if_exists='replace', index=False, con=engine)
            self.logger.info('Таблица financial_indicators записана')
        else:
            self.logger.warning(f'Таблица financial_indicators не обновлена')

    def save_key_eco_table(self, key_eco_table):
        if key_eco_table is not None:
            key_eco_table.to_sql('key_eco', if_exists='replace', index=False, con=engine)
            self.logger.info('Таблица key_eco записана')
        else:
            self.logger.warning(f'Таблица key_eco не обновлена')

    def save_date_of_last_build(self):
        cur_time = datetime.datetime.now().strftime(config.BASE_DATETIME_FORMAT)
        cur_time_in_box = pd.DataFrame([[cur_time]], columns=['date_time'])
        cur_time_in_box.to_sql('date_of_last_build', if_exists='replace', index=False, con=engine)
        self.logger.info('Таблица date_of_last_build записана')


def get_next_collect_datetime(next_research_getting_time: str) -> datetime.datetime:
    """
    Возвращает дату_время следующей сборки

    :param next_research_getting_time: строка формата %H:%M
    """
    now = datetime.datetime.now()
    next_collect_dt = datetime.datetime.strptime(next_research_getting_time, "%H:%M")
    next_collect_dt = datetime.datetime(now.year, now.month, now.day, next_collect_dt.hour, next_collect_dt.minute)

    if next_collect_dt < now:
        next_collect_dt += datetime.timedelta(days=1)
    return next_collect_dt


async def run_parse_cib(logger):
    postgres_pool = await asyncpg.create_pool(
        user=config.DB_USER,
        password=config.DB_PASS,
        host=config.DB_HOST,
        port=config.DB_PORT,
        database=config.DB_NAME,
        max_inactive_connection_lifetime=60,
    )
    await ResearchAPIParser(logger, postgres_pool).parse_pages()


def run_researches_getter(next_research_getting_time: str, logger: Logger.logger) -> None:
    start_tm = time.time()

    logger.info('Инициализация сборщика researches и графиков')
    runner = ResearchesGetter(logger)
    logger.info('Загрузка прокси')
    runner.parser_obj.get_proxy_addresses()

    try:
        driver = get_driver(logger)
    except Exception as e:
        logger.error('Ошибка при подключении к контейнеру selenium: %s', e)
        driver = None

    runner.set_driver(driver)

    if driver:
        try:
            logger.info('Начало сборки отчетов с research')
            reviews_dict, key_eco_table, clients_table = runner.collect_research()
            logger.info('Сохранение собранных данных')
            runner.save_clients_financial_indicators(clients_table)
            runner.save_key_eco_table(key_eco_table)
            runner.save_reviews(reviews_dict)
        except Exception as e:
            logger.error('Ошибка при сборке отчетов с Research: %s', e)

        try:
            logger.info('Поднятие новой сессии')
            session = req.Session()
            logger.info('Сборки графиков')
            runner.commodities_plot_collect(session)
        except Exception as e:
            logger.error('Ошибка при парсинге источников по сырью: %s', e)

        try:
            driver.quit()
        except Exception as e:
            # предполагается, что такая ошибка возникает, если в процессе сбора данных у нас сдох селениум,
            # тогда вылетает MaxRetryError
            logger.error('Ошибка во время закрытия подключения к selenium: %s', e)

    logger.info('Запись даты и времени последней успешной сборки researches и графиков')
    runner.save_date_of_last_build()

    # Запуск парсинга CIB через условный апиай
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_parse_cib(logger))
    loop.close()

    work_time = time.time() - start_tm
    end_dt = datetime.datetime.now().strftime(config.INVERT_DATETIME_FORMAT)
    next_collect_dt = get_next_collect_datetime(next_research_getting_time).strftime(config.INVERT_DATETIME_FORMAT)
    end_msg = f'Сборка завершена за {work_time:.3f} секунд в {end_dt}. Следующая сборка в {next_collect_dt}'
    print(end_msg)
    logger.info(end_msg)


def main():
    """
    Сборщик researches и графиков
    Сборка происходит каждый день в '08:00', '10:00', '12:00', '14:00', '16:00', '18:00'
    Время сборки указано в списке в config.RESEARCH_GETTING_TIMES_LIST
    """
    sentry.init_sentry(dsn=config.SENTRY_RESEARCH_PARSER_DSN)

    warnings.filterwarnings('ignore')
    # логгер для сохранения действий программы + пользователей
    logger = selector_logger(config.log_file, config.LOG_LEVEL_INFO)
    res_get_times_len = len(config.RESEARCH_GETTING_TIMES_LIST)

    if config.DEBUG:
        next_collect_time = config.RESEARCH_GETTING_TIMES_LIST[(0 + 1) % res_get_times_len]
        run_researches_getter(next_collect_time, logger)

    # сборка происходит каждый день в
    for index, collect_time in enumerate(config.RESEARCH_GETTING_TIMES_LIST):
        next_collect_time = config.RESEARCH_GETTING_TIMES_LIST[(index + 1) % res_get_times_len]

        schedule.every().day.at(collect_time).do(run_researches_getter, next_research_getting_time=next_collect_time, logger=logger)

    while True:
        schedule.run_pending()
        time.sleep(config.STATS_COLLECTOR_SLEEP_TIME)


if __name__ == '__main__':
    main()
