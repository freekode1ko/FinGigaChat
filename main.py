from dateutil.relativedelta import relativedelta
from module.logger_base import selector_logger
import module.data_transformer as dt
import module.user_emulator as ue
import module.crawler as crawler

from sql_model.commodity_pricing import CommodityPricing
from sql_model.commodity import Commodity
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, NullPool
from typing import List, Tuple, Dict
from selenium import webdriver

from pathlib import Path
import requests as req
from lxml import html
import pandas as pd
import numpy as np
import datetime
import warnings
import config
import time
import json
import re


class Main:
    def __init__(self):
        parser_obj = crawler.Parser(logger)
        # user_obj = ue.ResearchParser()
        # rebase = config.research_base_url
        path_to_source = './sources/ТЗ.xlsx'
        transformer_obj = dt.Transformer()
        psql_engine = config.psql_engine
        list_of_companies = config.list_of_companies
        data_market_base_url = config.data_market_base_url

        # self.rebase = rebase
        # self.user_object = user_object
        self.psql_engine = psql_engine
        self.parser_obj = parser_obj
        self.path_to_source = path_to_source
        self.transformer_obj = transformer_obj
        self.list_of_companies = list_of_companies
        self.data_market_base_url = data_market_base_url
        self.commodities = self.transformer_obj.url_updater()
        self.metals_wire_table = None

    def table_collector(self, session: req.sessions.Session):
        all_tables = []
        urls = self.transformer_obj.load_urls_as_list(self.path_to_source, 'Источник')
        df_urls = pd.DataFrame(urls).dropna().drop_duplicates()
        urls = df_urls.values.tolist()
        for url in urls:
            euro_standard, page_html = self.parser_obj.get_html(url[2], session)
            try:
                tables = self.transformer_obj.get_table_from_html(euro_standard, page_html)
                all_tables.extend([[url[0].split('/')[0], *url[1:], table] for table in tables])
                logger.info(f'Таблиц добавлено: {len(tables)}')
            except ValueError as val_err:
                logger.error(f'Таблицы не найдены. {val_err}: {page_html[:100]}')
        return all_tables

    def graph_collector(self, url, session: req.sessions.Session, driver, name=''):
        logger.info(f'Сборка графиков. Источник: {url}')
        if 'api.investing' in url:
            InvAPI_obj = ue.InvestingAPIParser(driver, logger)
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
            graph_url = '{}chart?s=lmahds03:com&' \
                        'span=5y&' \
                        'securify=new&' \
                        'url=/commodity/{}&' \
                        'AUTH={}&' \
                        'ohlc=0'.format(self.data_market_base_url, name, auth[-1][1:-1])
            data = req.get(graph_url, verify=False)

            self.transformer_obj.five_year_graph(data, name)

    def get_metals_wire_table_data(self, driver):
        metals_wire_parser_obj = ue.MetalsWireParser(driver, logger)
        self.metals_wire_table = metals_wire_parser_obj.get_table_data()

    def commodities_plot_collect(self, session: req.sessions.Session, driver):
        self.get_metals_wire_table_data(driver)
        commodity_pricing = pd.DataFrame()
        logger.info(f'Сборка по сырью {len(self.commodities)}')
        for commodity in self.commodities:
            link = self.commodities[commodity]['links'][0]
            name = self.commodities[commodity]['naming']
            logger.info(commodity)
            logger.info(self.commodities[commodity]['links'][0])

            self.graph_collector(link, session, driver, commodity)
            if len(self.commodities[commodity]['links']) > 1:
                url = self.commodities[commodity]['links'][1]
                InvAPI_obj = ue.InvestingAPIParser(driver, logger)
                streaming_price = InvAPI_obj.get_streaming_chart_investing(url)

                ''' What's the difference?
                dict_row = {'Resource': commodity.split(',')[0], 'SPOT': round(float(streaming_price), 1),
                            'alias': self.commodities[commodity]['alias'].lower().strip(),
                            'unit': self.commodities[commodity]['measurables']}
                '''
                dict_row = {'Resource': self.commodities[commodity]['naming'], 'SPOT': round(float(streaming_price), 1)}
                dict_row['alias'] = self.commodities[commodity]['alias'].lower().strip()
                dict_row['unit'] = self.commodities[commodity]['measurables']
                dict_row['Resource'] = commodity.split(',')[0]

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
        commodity = pd.read_sql_query("SELECT * FROM commodity", con=engine)
        commodity_ids = pd.DataFrame()

        for i, row in commodity_pricing.iterrows():
            commodity_id = commodity[commodity['name'] == row['alias']]['id']

            dict_row = {'commodity_id': commodity_id.values[0]}
            commodity_ids = pd.concat([commodity_ids, pd.DataFrame(dict_row, index=[0])], ignore_index=True)

        df_combined = pd.concat([commodity_pricing, commodity_ids], axis=1)
        df_combined = df_combined.rename(
            columns={'Resource': 'subname', 'SPOT': 'price', '1M diff.': 'm_delta', 'YTD diff.': 'y_delta',
                     "Cons-s'23": 'cons'})
        df_combined = df_combined.loc[:, ~df_combined.columns.str.contains('^Unnamed')]
        df_combined = df_combined.drop(columns=['alias'])

        engine = create_engine(self.psql_engine, poolclass=NullPool)
        Session = sessionmaker(bind=engine)
        session = Session()
        q = session.query(CommodityPricing)

        if q.count() == 28:
            for i, row in df_combined.iterrows():
                session.query(CommodityPricing).filter(CommodityPricing.subname == row['subname']). \
                    update({"price": row['price'], "m_delta": np.nan, "y_delta": row['y_delta'], "cons": row['cons']})
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
                    cons=row['cons'])
                session.merge(commodity_price_obj, load=True)
                session.commit()

            q_gas = session.query(Commodity).filter(Commodity.name == 'газ')
            commodity_price_obj = CommodityPricing(
                commodity_id=q_gas[0].id,
                subname='Газ',
                unit=np.nan,
                price=np.nan,
                m_delta=np.nan,
                y_delta=np.nan,
                cons=np.nan)
            session.merge(commodity_price_obj, load=True)
            session.commit()

        session.close()

    @staticmethod
    def bond_block(table_bonds: list) -> pd.DataFrame:
        bonds_kot = pd.DataFrame(columns=['Название', 'Доходность', 'Осн,', 'Макс,', 'Мин,', 'Изм,', 'Изм, %', 'Время'])
        if table_bonds[0] == 'Облигации' and table_bonds[1] == 'Блок котировки':
            bonds_kot = pd.concat([bonds_kot, table_bonds[3]])
            logger.info('Таблица Облигации (Котировки) собрана')
        return bonds_kot

    @staticmethod
    def economic_block(table_eco: list, page_eco: str):
        eco_frst_third = []
        world_bet = pd.DataFrame(columns=['Country', 'Last', 'Previous', 'Reference', 'Unit'])
        rus_infl = pd.DataFrame(columns=['Дата', 'Ключевая ставка, % годовых',
                                         'Инфляция, % г/г', 'Цель по инфляции, %'])
        if table_eco[0] == 'Экономика' and page_eco == 'KeyRate':
            eco_frst_third.append(['Текущая ключевая ставка Банка России', table_eco[3]['Ставка'][0]])
            logger.info('Таблица Экономика (KeyRate) собрана')

        elif table_eco[0] == 'Экономика' and page_eco == 'ruonia':
            ruonia = table_eco[3].loc[table_eco[3][0] == 'Ставка RUONIA, %'][2].values.tolist()[0]
            eco_frst_third.append(['Текущая ставка RUONIA', ruonia])
            logger.info('Таблица Экономика (ruonia) собрана')

        elif table_eco[0] == 'Экономика' and page_eco == 'interest-rate':
            if 'Actual' in table_eco[3]:
                eco_frst_third.append(['LPR Китай', table_eco[3]['Actual'][0]])
                logger.info('Таблица interest-rate (LPR Китай) собрана')

            elif 'Country' in table_eco[3]:
                world_bet = pd.concat([world_bet, table_eco[3]])
                logger.info('Таблица interest-rate (Country) собрана')

        elif table_eco[0] == 'Экономика' and page_eco == 'infl':
            rus_infl = pd.concat([rus_infl, table_eco[3]])
            logger.info('Таблица Экономика (infl) собрана')

        return eco_frst_third, world_bet, rus_infl

    @staticmethod
    def find_number(data_list):
        """ Находит первое число в списке """
        for item in data_list[:20]:
            try:
                return float(item)
            except ValueError:
                pass
        return None

    def exchange_block(self, table_exchange: list, exchange_page: str, session: req.sessions.Session):
        exchange_kot = []
        if table_exchange[0] == 'Курсы валют' and exchange_page in ['usd-rub', 'eur-rub', 'cny-rub', 'eur-usd']:
            if exchange_page == 'usd-rub':
                euro_standard, page_html = self.parser_obj.get_html(table_exchange[2], session)
                tables = pd.read_html(page_html)
                for table in tables:
                    try:
                        exchange_table = table[table['Exchange'] == 'Real-time Currencies']
                        if not exchange_table.empty:
                            row = ['usd-rub', exchange_table['Last'].values[0]]
                            exchange_kot.append(row)
                            logger.info('Таблица exchange_kot (usd-rub) собрана')
                            break
                    except IndexError:
                        logger.warning('Не та таблица попала на обработку')
                    except Exception as ex:
                        logger.error(f'Ошибка при обработке таблицы: {ex}')
            elif {'Exchange', 'Last', 'Time'}.issubset(table_exchange[3].columns):
                row = [exchange_page, table_exchange[3].loc[table_exchange[3]['Exchange'] ==
                                                            'Real-time Currencies']['Last'].values.tolist()[0]]
                exchange_kot.append(row)
                logger.info('Таблица exchange_kot (Exchange) собрана')

        elif table_exchange[0] == 'Курсы валют' and exchange_page in ['usd-cnh', 'usdollar']:
            euro_standard, page_html = self.parser_obj.get_html(table_exchange[2], session)
            tree = html.fromstring(page_html)
            data = tree.xpath('//*[@id="__next"]/div[2]/div//text()')
            price = self.find_number(data)
            row = [exchange_page, price]
            exchange_kot.append(row)
            logger.info('Таблица exchange_kot (usd-cnh) собрана')
        return exchange_kot

    def metal_block(self, table_metals: list, page_metals: str, session: req.sessions.Session):
        U7N23 = []
        metals_kot = []
        metals_coal_kot = []
        metals_bloom = pd.DataFrame(columns=['Metals', 'Price', 'Day'])

        if table_metals[0] == 'Металлы' and page_metals == 'LMCADS03:COM':
            euro_standard, page_html = self.parser_obj.get_html(table_metals[2], session)
            tree = html.fromstring(page_html)
            object_xpath = '//*[@id="__next"]/div/div[2]/div[6]/div/main/div/div[1]/div[4]/div'
            price = tree.xpath('{}/div[1]/text()'.format(object_xpath))
            price_diff = tree.xpath('{}/div[2]/span/span/text()'.format(object_xpath))
            temp_df = pd.DataFrame(columns=['Metals', 'Price', 'Day'])
            try:
                row = ['Медь', price[0], price_diff[0]]
                temp_df = pd.DataFrame([row], columns=['Metals', 'Price', 'Day'])
            except Exception as ex:
                logger.error(f'Ошибка ({ex}) получения таблицы с медью!')
            metals_bloom = pd.concat([metals_bloom, temp_df], ignore_index=True)
            logger.info('Таблица metals_bloom собрана')

        elif table_metals[0] == 'Металлы' and page_metals == 'U7*0':
            if {'Last', 'Change'}.issubset(table_metals[3].columns):
                jap_coal = table_metals[3][table_metals[3].Symbol.str.contains('U7.24')]
                U7N23.append(['кокс. уголь', jap_coal.values.tolist()[0][1]])
                logger.info('Таблица U7N24 собрана')

        elif table_metals[0] == 'Металлы' and page_metals == 'commodities':
            if 'Metals' in table_metals[3].columns:
                temp = table_metals[3].loc[table_metals[3]['Metals'].isin(['Gold USD/t,oz', 'Silver USD/t,oz',
                                                                           'Platinum USD/t,oz', 'Lithium CNY/T'])]
                metals_kot.append(temp)
                logger.info('Таблица metals_kot (Metals) собрана')

            elif 'Industrial' in table_metals[3].columns:
                temp = table_metals[3].loc[table_metals[3]['Industrial'].isin(['Aluminum USD/T', 'Nickel USD/T',
                                                                               'Lead USD/T', 'Zinc USD/T',
                                                                               'Palladium USD/t,oz', 'Cobalt USD/T',
                                                                               'Iron Ore 62% fe USD/T'])]
                metals_kot.append(temp.rename(columns={'Industrial': 'Metals'}))
                logger.info('Таблица metals_kot (Industrial) собрана')

            elif 'Energy' in table_metals[3].columns:
                temp = table_metals[3].loc[table_metals[3]['Energy'].isin(['Coal USD/T'])]
                metals_kot.append(temp.rename(columns={'Energy': 'Metals'}))
                logger.info('Таблица metals_kot (Energy) собрана')

        elif table_metals[0] == 'Металлы' and page_metals == 'coal-(api2)-cif-ara-futures-historical-data':
            if 'Price' in table_metals[3].columns:
                table_metals[3]['Date'] = table_metals[3]['Date'].astype('datetime64[ns]')
                # day_day = table_metals[3]['Date'][0] - relativedelta(days=1)
                week_day = table_metals[3]['Date'][0] - relativedelta(weeks=1)
                month_day = table_metals[3]['Date'][0] - relativedelta(months=1)
                year_day = table_metals[3]['Date'][0] - relativedelta(years=1)

                # day_table = table_metals[3].loc[table_metals[3]['Date'] == str(day_day).split()[0]]
                week_table = table_metals[3].loc[table_metals[3]['Date'] == str(week_day).split()[0]]
                month_table = table_metals[3].loc[table_metals[3]['Date'] == str(month_day).split()[0]]
                year_table = table_metals[3].loc[table_metals[3]['Date'] == str(year_day).split()[0]]
                temp_table = pd.concat([table_metals[3].head(1), week_table,
                                        month_table, year_table], ignore_index=True)

                temp_table['Metals'] = 'Эн. уголь'
                temp_table['%'] = temp_table.groupby('Metals')['Price'].pct_change()
                temp_table['%'] = temp_table.groupby('Metals')['Price'].pct_change()
                try:
                    metals_coal_kot.append([temp_table['Metals'][0], temp_table['Price'][0],
                                            *temp_table['%'].tolist()[1:], str(temp_table['Date'][0]).split()[0]])
                    logger.info('Таблица metals_coal_kot собрана')
                except ValueError:
                    metals_coal_kot.append([temp_table['Metals'][0], temp_table['Price'][0],
                                            *temp_table['%'].tolist()[0:], str(temp_table['Date'][0]).split()[0]])
                    logger.warning('Сдвиг в таблице с котировками (metals_coal_kot)')
        return metals_coal_kot, metals_kot, metals_bloom, U7N23

    def main(self) -> None:
        session = req.Session()
        all_tables = self.table_collector(session)
        engine = create_engine(self.psql_engine, poolclass=NullPool)
        logger.info('Котировки собраны, запускаем обработку')
        all_tables.append(['Металлы', 'Блок котировки',
                           'https://www.bloomberg.com/quote/LMCADS03:COM', [pd.DataFrame()]])
        bonds_kot = pd.DataFrame(columns=['Название', 'Доходность', 'Осн,', 'Макс,',
                                          'Мин,', 'Изм,', 'Изм, %', 'Время'])
        exchange_kot = []
        eco_frst_third = []
        world_bet = pd.DataFrame(columns=['Country', 'Last', 'Previous', 'Reference', 'Unit'])
        rus_infl = pd.DataFrame(columns=['Дата', 'Ключевая ставка, % годовых',
                                         'Инфляция, % г/г', 'Цель по инфляции, %'])
        U7N23 = []
        metals_kot = []
        metals_coal_kot = []
        metals_bloom = pd.DataFrame(columns=['Metals', 'Price', 'Day'])

        size_tables = len(all_tables)
        logger.info(f'Обработка собранных таблиц ({size_tables}).')
        for enum, tables_row in enumerate(all_tables):
            logger.info('{}/{}'.format(enum + 1, size_tables))
            url_index = -1 if tables_row[2].split('/')[-1] else -2
            source_page = tables_row[2].split('/')[url_index]
            logger.info(f'Сборка таблицы {source_page} из блока {tables_row[0]}')
            # BONDS BLOCK
            bonds_kot = pd.concat([bonds_kot, self.bond_block(tables_row)])

            # ECONOMIC BLOCK
            eco_list, world_bet_df, rus_infl_df = self.economic_block(tables_row, source_page)
            eco_frst_third += eco_list
            world_bet = pd.concat([world_bet, world_bet_df])
            rus_infl = pd.concat([rus_infl, rus_infl_df])

            # EXCENGE BLOCK
            exchange_kot += self.exchange_block(tables_row, source_page, session)

            # METALS BLOCK
            metal_coal_ls, metal_cat_ls, metal_bloom_df, U7_ls = self.metal_block(tables_row, source_page, session)
            U7N23 += U7_ls
            metals_coal_kot += metal_coal_ls
            metals_kot += metal_cat_ls
            metals_bloom = pd.concat([metals_bloom, metal_bloom_df])

        # Запись Металов и Сырья в БД и Локальное хранилище
        metal_writer = pd.ExcelWriter('sources/tables/metal.xlsx')
        big_table = pd.DataFrame(columns=['Metals', 'Price', 'Day', '%', 'Weekly', 'Monthly', 'YoY', 'Date'])
        metals_coal_kot_table = pd.DataFrame(metals_coal_kot, columns=['Metals', 'Price', 'Weekly', 'Date'])
        U7N23_df = pd.DataFrame(U7N23, columns=['Metals', 'Price'])
        for table in metals_kot:
            big_table = pd.concat([big_table, table], ignore_index=True)
        big_table = pd.concat([big_table, metals_coal_kot_table, metals_bloom, U7N23_df], ignore_index=True)

        big_table.to_excel(metal_writer, sheet_name='Металы')
        logger.info('Записана страница с Металлами')
        big_table.to_sql('metals', if_exists='replace', index=False, con=engine)
        logger.info('Таблица metals записана')

        # Запись Курсов в БД и Локальное хранилище
        exchange_writer = pd.ExcelWriter('sources/tables/exc.xlsx')
        fx_df = pd.DataFrame(exchange_kot, columns=['Валюта', 'Курс']) \
            .drop_duplicates(subset=['Валюта'], ignore_index=True)
        fx_df.to_excel(exchange_writer, sheet_name='Курсы валют')
        logger.info('Записана страница с Курсами')
        # Write to fx DB
        fx_df.to_sql('exc', if_exists='replace', index=False, con=engine)
        logger.info('Таблица exc записана')

        # Запись Экономики в БД и Локальное хранилище
        eco_writer = pd.ExcelWriter('sources/tables/eco.xlsx')
        eco_stake = pd.DataFrame(eco_frst_third)
        eco_stake.to_excel(eco_writer, sheet_name='Ставка')
        logger.info('Записана страница с Ставкой')
        world_bet.to_excel(eco_writer, sheet_name='Ключевые ставки ЦБ мира')
        logger.info('Записана страница с КС ЦБ')
        rus_infl.to_excel(eco_writer, sheet_name='Инфляция в России')
        logger.info('Записана страница с Инфляцией')

        eco_stake.to_sql('eco_stake', if_exists='replace', index=False, con=engine)
        logger.info('Таблица eco_stake записана')
        world_bet.to_sql('eco_global_stake', if_exists='replace', index=False, con=engine)
        logger.info('Таблица eco_global_stake записана')
        rus_infl.to_sql('eco_rus_influence', if_exists='replace', index=False, con=engine)
        logger.info('Таблица eco_rus_influence записана')

        # Запись Котировок в БД и Локальное хранилище
        bonds_writer = pd.ExcelWriter('sources/tables/bonds.xlsx')
        bonds_kot.to_excel(bonds_writer, sheet_name='Блок котировки')
        logger.info('Записана страница с Котировками')
        bonds_kot.to_sql('bonds', if_exists='replace', index=False, con=engine)
        logger.info('Таблица bonds записана')

        logger.info('Закрытие записи локальных бэкапов')
        bonds_writer.close()
        eco_writer.close()
        exchange_writer.close()
        metal_writer.close()

        return None

    def collect_research(self, driver) -> (dict, dict):
        """
        Collect all type of reviews from CIB Research
        And get page html with fin data about companies from CIB Research
        :return: dict with data reviews, dict with html page
        """

        logger.info('Начало сборки с research')
        economy, money, comm = 'econ', 'money', 'comm'
        authed_user = ue.ResearchParser(driver, logger)

        # economy
        key_eco_table = authed_user.get_key_econ_ind_table()
        eco_day = authed_user.get_reviews(url_part=economy, tab='Ежедневные', title='Экономика - Sberbank CIB')
        eco_month = authed_user.get_reviews(url_part=economy, tab='Все', title='Экономика - Sberbank CIB',
                                            name_of_review='Экономика России. Ежемесячный обзор')
        logger.info('Блок по экономике собран')

        # bonds
        bonds_day = authed_user.get_reviews(url_part=money, tab='Ежедневные', title='FX &amp; Ставки - Sberbank CIB',
                                            name_of_review='Валютный рынок и процентные ставки',
                                            type_of_review='bonds', count_of_review=2)
        bonds_month = authed_user.get_reviews(url_part=money, tab='Все', title='FX &amp; Ставки - Sberbank CIB',
                                              name_of_review='Обзор рынка процентных ставок')
        logger.info('Блок по ставкам собран')

        # exchange
        exchange_day = authed_user.get_reviews(url_part=money, tab='Ежедневные', title='FX &amp; Ставки - Sberbank CIB',
                                               name_of_review='Валютный рынок и процентные ставки',
                                               type_of_review='exchange', count_of_review=2)
        exchange_month_uan = authed_user.get_reviews(url_part=economy, tab='Все', title='Экономика - Sberbank CIB',
                                                     name_of_review='Ежемесячный обзор по юаню')
        exchange_month_soft = authed_user.get_reviews(url_part=economy, tab='Все', title='Экономика - Sberbank CIB',
                                                      name_of_review='Ежемесячный дайджест по мягким валютам')
        logger.info('Блок по курсам валют собран')

        # commodity
        commodity_day = authed_user.get_reviews(url_part=comm, tab='Ежедневные', title='Сырьевые товары - Sberbank CIB',
                                                name_of_review='Сырьевые рынки', type_of_review='commodity')
        logger.info('Блок по сырью собран')

        exchange_month = exchange_month_uan + exchange_month_soft
        reviews = {
            'Economy day': eco_day,
            'Economy month': eco_month,
            'Bonds day': bonds_day,
            'Bonds month': bonds_month,
            'Exchange day': exchange_day,
            'Exchange month': exchange_month,
            'Commodity day': commodity_day
        }

        # companies
        companies_pages_html = dict()
        for company in self.list_of_companies:
            page_html = authed_user.get_company_html_page(url_part=company[0])
            companies_pages_html[company[1]] = page_html
        logger.info('Страница с компаниями собрана')
        # print('companies page...ok')

        clients_table = authed_user.get_companies_financial_indicators_table()
        logger.info('Страница с клиентами собрана')
        # print('clients table...ok')

        authed_user.get_industry_reviews()
        logger.info('Страница с отчетами по направлениям собрана')
        # print('industry reviews...ok')

        authed_user.get_weekly_review()
        logger.info('Weekly pulse собран')

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
            'Commodity day': 'report_met_day'
        }

        for review_name in table_name_for_review:
            table_name = table_name_for_review.get(review_name)
            reviews_list = reviews_to_save.get(review_name)
            pd.DataFrame(reviews_list).to_sql(table_name, if_exists='replace', index=False, con=engine)
            logger.info(f'Таблица {reviews_list} записана')

        logger.info('Все собранные отчеты с research записаны')

    def save_clients_financial_indicators(self, clients_table):
        engine = create_engine(self.psql_engine, poolclass=NullPool)
        clients_table.to_sql('financial_indicators', if_exists='replace', index=False, con=engine)
        logger.info('Таблица financial_indicators записана')

    def save_key_eco_table(self, key_eco_table):
        engine = create_engine(self.psql_engine, poolclass=NullPool)
        key_eco_table.to_sql('key_eco', if_exists='replace', index=False, con=engine)
        logger.info('Таблица key_eco записана')

    def save_date_of_last_build(self):
        engine = create_engine(self.psql_engine, poolclass=NullPool)
        cur_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        cur_time_in_box = pd.DataFrame([[cur_time]], columns=['date_time'])
        cur_time_in_box.to_sql('date_of_last_build', if_exists='replace', index=False, con=engine)
        logger.info('Таблица date_of_last_build записана')

    def process_companies_data(self, company_pages_html) -> None:
        """
        Process and save fin mark of the companies.
        :param company_pages_html: html page with fin mark from CIB Research
        """
        # TODO: изменить сохранение ?

        list_of_companies_df = pd.DataFrame(self.list_of_companies, columns=['ID', 'Name', 'URL'])
        comp_size = len(self.list_of_companies)
        page_tables = []

        logger.info('Начало процесса обработки фин.показателей компаний')
        for comp_num, company in enumerate(company_pages_html):
            # print('{}/{}'.format(comp_num + 1, comp_size))
            logger.info('{}/{}'.format(comp_num + 1, comp_size))
            page_html = company_pages_html.get(company)
            tables = self.transformer_obj.get_table_from_html(True, page_html)
            pd.set_option('display.max_columns', None)
            tables[0]["group_no"] = tables[0].isnull().all(axis=1).cumsum()
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
            logger.info(f'Блок с компаниями записан в {path_to_companies}')
            companies_writer.close()


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    logger = selector_logger(Path(__file__).stem, 10)  # логгер для сохранения действий программы + пользователей
    while True:
        hours2wait = 4  # после обновления всех данных - ждем 4 часа

        logger.info('Инициализация сборщика котировок')
        runner = Main()
        logger.info('Загрузка прокси')
        runner.parser_obj.get_proxy_addresses()

        try:
            logger.info('Начало сборки котировок')
            runner.main()
        except Exception as e:
            logger.error(f'Ошибка при сборке котировок: {e}')
            hours2wait = 1

        try:
            # collect and save research data
            logger.info('Подключение к контейнеру selenium')
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.add_argument(f'--user-agent={config.user_agents[0]}')
            driver = webdriver.Remote(command_executor='http://localhost:4444/wd/hub', options=firefox_options)
        except Exception as e:
            logger.error(f'Ошибка при подключении к контейнеру selenium: {e}')
            driver = None
            hours2wait = 1

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
                logger.error(f'Ошибка при сборке отчетов с Research: {e}')
                hours2wait = 1

            try:
                logger.info('Поднятие новой сессии')
                session = req.Session()
                # print('session started')
                logger.info('Сборки графиков')
                runner.commodities_plot_collect(session, driver)
                # print('com writed')
            except Exception as e:
                logger.error(f'Ошибка при парсинге источников по сырью: {e}')
                hours2wait = 1

            try:
                driver.close()
            except Exception as e:
                # предполагается, что такая ошибка возникает, если в процессе сбора данных у нас сдох селениум,
                # тогда вылетает MaxRetryError
                logger.error(f'Ошибка во время закрытия подключения к selenium: {e}')
                hours2wait = 1

        logger.info('Запись даты и времени последней успешной сборки')
        runner.save_date_of_last_build()
        # with open('sources/tables/time.txt', 'w') as f:
        #    f.write(datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
        print(f'Ожидание {hours2wait} часов перед следующей сборкой...')
        logger.info(f'Ожидание {hours2wait} часов перед следующей сборкой...')

        for i in range(hours2wait):
            time.sleep(3600)
            print(f'Ожидание сборки. \n{hours2wait - i+1}/{hours2wait} часа')
            logger.info(f'Ожидание сборки. \n{hours2wait - i+1}/{hours2wait} часа')
