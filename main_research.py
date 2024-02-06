import datetime
import json
import re
import time
import warnings
from pathlib import Path
from typing import Dict, List, Tuple

import click
import numpy as np
import pandas as pd
import requests as req
from selenium import webdriver
from sqlalchemy import NullPool, create_engine
from sqlalchemy.orm import sessionmaker

import config
import module.crawler as crawler
import module.data_transformer as dt
import module.user_emulator as ue
from module.logger_base import selector_logger
from sql_model.commodity import Commodity
from sql_model.commodity_pricing import CommodityPricing
from utils import sentry
from utils.cli_utils import get_period


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

    def graph_collector(self, url, session: req.sessions.Session, driver, name=''):
        self.logger.info(f'Сборка графиков. Источник: {url}')
        if 'api.investing' in url:
            InvAPI_obj = ue.InvestingAPIParser(driver, self.logger)
            data = InvAPI_obj.get_graph_investing(url)
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

    def get_metals_wire_table_data(self, driver):
        metals_wire_parser_obj = ue.MetalsWireParser(driver, self.logger)
        self.metals_wire_table = metals_wire_parser_obj.get_table_data()

    def commodities_plot_collect(self, session: req.sessions.Session, driver):
        self.get_metals_wire_table_data(driver)
        commodity_pricing = pd.DataFrame()
        self.logger.info(f'Сборка по сырью {len(self.commodities)}')
        for commodity in self.commodities:
            link = self.commodities[commodity]['links'][0]
            name = self.commodities[commodity]['naming']
            self.logger.info(commodity)
            self.logger.info(self.commodities[commodity]['links'][0])

            self.graph_collector(link, session, driver, commodity)
            if len(self.commodities[commodity]['links']) > 1:
                url = self.commodities[commodity]['links'][1]
                InvAPI_obj = ue.InvestingAPIParser(driver, self.logger)
                streaming_price = InvAPI_obj.get_streaming_chart_investing(url)

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

            elif self.commodities[commodity]['naming'] != 'Gas':
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

        engine = create_engine(self.psql_engine, poolclass=NullPool)
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

        engine = create_engine(self.psql_engine, poolclass=NullPool)
        Session = sessionmaker(bind=engine)
        session = Session()
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

        session.close()

    def collect_research(self, driver) -> (dict, dict):
        """
        Collect all type of reviews from CIB Research
        And get page html with fin data about companies from CIB Research
        :return: dict with data reviews, dict with html page
        """

        self.logger.info('Начало сборки с research')
        economy, money, comm = 'econ', 'money', 'comm'
        authed_user = ue.ResearchParser(driver, self.logger)

        # economy
        key_eco_table = authed_user.get_key_econ_ind_table()
        eco_day = authed_user.get_reviews(url_part=economy, tab='Ежедневные', title='Экономика - Sberbank CIB')
        eco_month = authed_user.get_reviews(
            url_part=economy, tab='Все', title='Экономика - Sberbank CIB', name_of_review='Экономика России. Ежемесячный обзор'
        )
        self.logger.info('Блок по экономике собран')

        # bonds
        bonds_day = authed_user.get_reviews(
            url_part=money,
            tab='Ежедневные',
            title='FX &amp; Ставки - Sberbank CIB',
            name_of_review='Валютный рынок и процентные ставки',
            type_of_review='bonds',
            count_of_review=2,
        )
        bonds_month = authed_user.get_reviews(
            url_part=money, tab='Все', title='FX &amp; Ставки - Sberbank CIB', name_of_review='Обзор рынка процентных ставок'
        )
        self.logger.info('Блок по ставкам собран')

        # exchange
        exchange_day = authed_user.get_reviews(
            url_part=money,
            tab='Ежедневные',
            title='FX &amp; Ставки - Sberbank CIB',
            name_of_review='Валютный рынок и процентные ставки',
            type_of_review='exchange',
            count_of_review=2,
        )
        exchange_month_uan = authed_user.get_reviews(
            url_part=economy, tab='Все', title='Экономика - Sberbank CIB', name_of_review='Ежемесячный обзор по юаню'
        )
        exchange_month_soft = authed_user.get_reviews(
            url_part=economy, tab='Все', title='Экономика - Sberbank CIB', name_of_review='Ежемесячный дайджест по мягким валютам'
        )
        self.logger.info('Блок по курсам валют собран')

        # commodity
        commodity_day = authed_user.get_reviews(
            url_part=comm,
            tab='Ежедневные',
            title='Сырьевые товары - Sberbank CIB',
            name_of_review='Сырьевые рынки',
            type_of_review='commodity',
        )
        self.logger.info('Блок по сырью собран')

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

        # companies
        companies_pages_html = dict()
        for company in self.list_of_companies:
            page_html = authed_user.get_company_html_page(url_part=company[0])
            companies_pages_html[company[1]] = page_html
        self.logger.info('Страница с компаниями собрана')

        clients_table = authed_user.get_companies_financial_indicators_table()
        self.logger.info('Страница с клиентами собрана')

        authed_user.get_industry_reviews()
        self.logger.info('Страница с отчетами по направлениям собрана')

        authed_user.get_weekly_review()
        self.logger.info('Weekly pulse собран')

        return reviews, companies_pages_html, key_eco_table, clients_table

    def save_reviews(self, reviews_to_save: Dict[str, List[Tuple]]) -> None:
        """
        Save all reviews into the database.
        :param reviews_to_save: dict of list of the reviews
        """
        # TODO: мб сделать одну таблицу для обзоров ?

        engine = create_engine(self.psql_engine, poolclass=NullPool)
        table_name_for_review = {
            'Economy day': 'report_eco_day',
            'Economy month': 'report_eco_mon',
            'Bonds day': 'report_bon_day',
            'Bonds month': 'report_bon_mon',
            'Exchange day': 'report_exc_day',
            'Exchange month': 'report_exc_mon',
            'Commodity day': 'report_met_day',
        }

        for review_name in table_name_for_review:
            table_name = table_name_for_review.get(review_name)
            reviews_list = reviews_to_save.get(review_name)
            pd.DataFrame(reviews_list).to_sql(table_name, if_exists='replace', index=False, con=engine)
            self.logger.info(f'Таблица {reviews_list} записана')

        self.logger.info('Все собранные отчеты с research записаны')

    def save_clients_financial_indicators(self, clients_table):
        engine = create_engine(self.psql_engine, poolclass=NullPool)
        clients_table.to_sql('financial_indicators', if_exists='replace', index=False, con=engine)
        self.logger.info('Таблица financial_indicators записана')

    def save_key_eco_table(self, key_eco_table):
        engine = create_engine(self.psql_engine, poolclass=NullPool)
        key_eco_table.to_sql('key_eco', if_exists='replace', index=False, con=engine)
        self.logger.info('Таблица key_eco записана')

    def save_date_of_last_build(self):
        engine = create_engine(self.psql_engine, poolclass=NullPool)
        cur_time = datetime.datetime.now().strftime(config.BASE_DATETIME_FORMAT)
        cur_time_in_box = pd.DataFrame([[cur_time]], columns=['date_time'])
        cur_time_in_box.to_sql('date_of_last_build', if_exists='replace', index=False, con=engine)
        self.logger.info('Таблица date_of_last_build записана')

    def process_companies_data(self, company_pages_html) -> None:
        """
        Process and save fin mark of the companies.
        :param company_pages_html: html page with fin mark from CIB Research
        """
        # TODO: изменить сохранение ?

        list_of_companies_df = pd.DataFrame(self.list_of_companies, columns=['ID', 'Name', 'URL'])
        comp_size = len(self.list_of_companies)
        page_tables = []

        self.logger.info('Начало процесса обработки фин.показателей компаний')
        for comp_num, company in enumerate(company_pages_html):
            self.logger.info('{}/{}'.format(comp_num + 1, comp_size))
            page_html = company_pages_html.get(company)
            tables = self.transformer_obj.get_table_from_html(True, page_html)
            pd.set_option('display.max_columns', None)
            tables[0]['group_no'] = tables[0].isnull().all(axis=1).cumsum()
            tables = tables[0].dropna(subset='Unnamed: 1')
            tables_names = tables['Unnamed: 0'].dropna().tolist()

            for i in range(0, len(tables_names)):
                df = tables[tables['group_no'] == i]
                df.reset_index(inplace=True)
                df = df.drop(['Unnamed: 0', 'index', 'group_no'], axis=1)
                df = df.drop(index=df.index[0], axis=0)
                df.rename(columns={'Unnamed: 1': 'Показатели'}, inplace=True)
                page_tables.append([tables_names[i], company, df])

            path_to_companies = 'sources/tables/companies.xlsx'
            companies_writer = pd.ExcelWriter(path_to_companies)
            list_of_companies_df.to_excel(companies_writer, sheet_name='head')
            for df in page_tables:
                df[2].to_excel(companies_writer, sheet_name='{}_{}'.format(df[1], df[0]))
            self.logger.info(f'Блок с компаниями записан в {path_to_companies}')
            companies_writer.close()


@click.command()
@click.option(
    '-p',
    '--period',
    default='4h',
    show_default=True,
    type=str,
    help='Периодичность сборки котировок\n' 's - секунды\n' 'm - минуты (значение по умолчанию)\n' 'h - часы\n' 'd - дни',
)
def main(period):
    """
    Сборщик researches и графиков
    """
    sentry.init_sentry(dsn=config.SENTRY_RESEARCH_PARSER_DSN)
    try:
        period, scale, scale_txt = get_period(period)
    except ValueError as e:
        print(e)
        return

    warnings.filterwarnings('ignore')
    # логгер для сохранения действий программы + пользователей
    logger = selector_logger(Path(__file__).stem, config.LOG_LEVEL_INFO)
    while True:
        current_period = period

        logger.info('Инициализация сборщика котировок')
        runner = ResearchesGetter(logger)
        logger.info('Загрузка прокси')
        runner.parser_obj.get_proxy_addresses()

        try:
            # collect and save research data
            logger.info('Подключение к контейнеру selenium')
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.add_argument(f'--user-agent={config.user_agents[0]}')
            driver = webdriver.Remote(command_executor='http://localhost:4444/wd/hub', options=firefox_options)
        except Exception as e:
            logger.error('Ошибка при подключении к контейнеру selenium: %s', e)
            driver = None
            current_period = 1

        if driver:
            try:
                logger.info('Начало сборки отчетов с research')
                reviews_dict, companies_pages_html_dict, key_eco_table, clients_table = runner.collect_research(driver)
                logger.info('Сохранение собранных данных')
                runner.save_clients_financial_indicators(clients_table)
                runner.save_key_eco_table(key_eco_table)
                runner.save_reviews(reviews_dict)
                runner.process_companies_data(companies_pages_html_dict)
            except Exception as e:
                logger.error('Ошибка при сборке отчетов с Research: %s', e)
                current_period = 1

            try:
                logger.info('Поднятие новой сессии')
                session = req.Session()
                logger.info('Сборки графиков')
                runner.commodities_plot_collect(session, driver)
            except Exception as e:
                logger.error('Ошибка при парсинге источников по сырью: %s', e)
                current_period = 1

            try:
                driver.close()
            except Exception as e:
                # предполагается, что такая ошибка возникает, если в процессе сбора данных у нас сдох селениум,
                # тогда вылетает MaxRetryError
                logger.error('Ошибка во время закрытия подключения к selenium: %s', e)
                current_period = 1

        logger.info('Запись даты и времени последней успешной сборки котировок')
        runner.save_date_of_last_build()
        print(f'Ожидание {current_period} часов перед следующей сборкой...')
        logger.info(f'Ожидание {current_period} часов перед следующей сборкой...')

        for i in range(current_period, 0, -1):
            time.sleep(scale)
            print(f'Ожидание сборки. {i} из {current_period} {scale_txt}')
            logger.info(f'Ожидание сборки. {i} из {current_period} {scale_txt}')


if __name__ == '__main__':
    main()
