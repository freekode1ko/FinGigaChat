from dateutil.relativedelta import relativedelta
import module.data_transformer as dt
import module.user_emulator as ue
import module.crawler as crawler
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from sqlalchemy import create_engine
import requests as req
from lxml import html
import pandas as pd
import warnings
import config
import time
import datetime
from typing import List, Tuple, Dict


class Main:
    def __init__(self):
        parser_obj = crawler.Parser()
        # user_object = ue.ResearchParser()
        # rebase = config.research_base_url
        path_to_source = './sources/ТЗ.xlsx'
        transformer_obj = dt.Transformer()
        psql_engine = config.psql_engine
        list_of_companies = config.list_of_companies

        # self.rebase = rebase
        # self.user_object = user_object
        self.psql_engine = psql_engine
        self.parser_obj = parser_obj
        self.path_to_source = path_to_source
        self.transformer_obj = transformer_obj
        self.list_of_companies = list_of_companies

    def table_collector(self, session: req.sessions.Session):
        all_tables = []
        urls = self.transformer_obj.load_urls_as_list(self.path_to_source, 'Источник')
        df_urls = pd.DataFrame(urls).dropna().drop_duplicates()
        urls = df_urls.values.tolist()
        for url in urls:
            euro_standard, page_html = self.parser_obj.get_html(url[2], session)
            print(euro_standard, url[2])
            try:
                tables = self.transformer_obj.get_table_from_html(euro_standard, page_html)
                for table in tables:
                    all_tables.append([url[0].split('/')[0], *url[1:], table])
                print('Tables added {}'.format(len(tables)))
            except ValueError as val_err:
                print(url[2])
                print('No tables found: {} : {}'.format(val_err, page_html[:100]))
        return all_tables

    @staticmethod
    def bond_block(table_bonds: list) -> pd.DataFrame:
        bonds_kot = pd.DataFrame(columns=['Название', 'Доходность', 'Осн,', 'Макс,', 'Мин,', 'Изм,', 'Изм, %', 'Время'])
        if table_bonds[0] == 'Облигации' and table_bonds[1] == 'Блок котировки':
            bonds_kot = pd.concat([bonds_kot, table_bonds[3]])
        return bonds_kot

    @staticmethod
    def economic_block(table_eco: list, page_eco: str):
        eco_frst_third = []
        world_bet = pd.DataFrame(columns=['Country', 'Last', 'Previous', 'Reference', 'Unit'])
        rus_infl = pd.DataFrame(
            columns=['Дата', 'Ключевая ставка, % годовых', 'Инфляция, % г/г', 'Цель по инфляции, %'])
        if table_eco[0] == 'Экономика' and page_eco == 'KeyRate':
            eco_frst_third.append(['Текущая ключевая ставка Банка России', table_eco[3]['Ставка'][0]])

        elif table_eco[0] == 'Экономика' and page_eco == 'ruonia':
            ruonia = table_eco[3].loc[table_eco[3][0] == 'Ставка RUONIA, %'][2].values.tolist()[0]
            eco_frst_third.append(['Текущая ставка RUONIA', ruonia])
        elif table_eco[0] == 'Экономика' and page_eco == 'interest-rate':
            if 'Actual' in table_eco[3]:
                eco_frst_third.append(['LPR Китай', table_eco[3]['Actual'][0]])
            elif 'Country' in table_eco[3]:
                world_bet = pd.concat([world_bet, table_eco[3]])
        elif table_eco[0] == 'Экономика' and page_eco == 'infl':
            rus_infl = pd.concat([rus_infl, table_eco[3]])
        return eco_frst_third, world_bet, rus_infl

    def exchange_block(self, table_exchange: list, exchange_page: str, session: req.sessions.Session):
        exchange_kot = []
        if table_exchange[0] == 'Курсы валют' and exchange_page in ['usd-rub', 'eur-rub', 'cny-rub', 'eur-usd']:
            if {'Exchange', 'Last', 'Time'}.issubset(table_exchange[3].columns):
                row = [exchange_page, table_exchange[3].loc[table_exchange[3]['Exchange'] == 'Real-time Currencies'][
                    'Last'].values.tolist()[0]]
                exchange_kot.append(row)

        elif table_exchange[0] == 'Курсы валют' and exchange_page in ['usd-cny', 'usdollar']:
            euro_standart, page_html = self.parser_obj.get_html(table_exchange[2], session)
            tree = html.fromstring(page_html)

            # USDOLLAR
            object_xpath = '//*[@id="__next"]/div[2]/div[2]/div[1]/div[1]/div[3]/div/div[1]/div[1]'
            price = tree.xpath('{}/text()'.format(object_xpath))
            # usd-cny
            if not price:
                object_xpath = '//*[@id="__next"]/div[2]/div/div/div[2]/main/div/div[1]/div[2]/div[1]'
                price = tree.xpath('{}/span/text()'.format(object_xpath))

            row = [exchange_page, *price]
            exchange_kot.append(row)
        return exchange_kot

    def metal_block(self, table_metals: list, page_metals: str, session: req.sessions.Session):
        U7N23 = []
        metals_kot = []
        metals_coal_kot = []
        metals_bloom = pd.DataFrame(columns=['Metals', 'Price', 'Day'])

        if table_metals[0] == 'Металлы' and page_metals == 'LMCADS03:COM':
            euro_standart, page_html = self.parser_obj.get_html(table_metals[2], session)
            tree = html.fromstring(page_html)
            # object_xpath = '//*[@id="root"]/div/div/section/section[1]/div/div[2]/section[1]/section/section/section'
            # price = tree.xpath('{}/div[1]/span[1]/text()'.format(object_xpath))
            # price_diff = tree.xpath('{}/div[2]/span[2]/text()'.format(object_xpath))
            object_xpath = '//*[@id="__next"]/div/div[2]/div[6]/div[1]/main/div/div[1]/div[4]/div'
            price = tree.xpath('{}/div[1]/text()'.format(object_xpath))
            price_diff = tree.xpath('{}/div[2]/span/span/text()'.format(object_xpath))
            try:
                row = ['Медь', price[0], price_diff[0]]
                temp_df = pd.DataFrame([row], columns=['Metals', 'Price', 'Day'])
            except:
                print(row)
                print(page_html)
                raise NameError('HiThere')
            metals_bloom = pd.concat([metals_bloom, temp_df], ignore_index=True)

        elif table_metals[0] == 'Металлы' and page_metals == 'U7*0':
            if {'Last', 'Change'}.issubset(table_metals[3].columns):
                jap_coal = table_metals[3][table_metals[3].Symbol.str.contains('U7.23')]
                U7N23.append(['кокс. уголь', jap_coal.values.tolist()[0][1]])

        elif table_metals[0] == 'Металлы' and page_metals == 'commodities':
            if 'Metals' in table_metals[3].columns:
                temp = table_metals[3].loc[table_metals[3]['Metals'].isin(['Gold USD/t,oz', 'Silver USD/t,oz',
                                                                           'Platinum USD/t,oz', 'Lithium CNY/T'])]
                metals_kot.append(temp)

            elif 'Industrial' in table_metals[3].columns:
                temp = table_metals[3].loc[table_metals[3]['Industrial'].isin(['Aluminum USD/T', 'Nickel USD/T',
                                                                               'Lead USD/T', 'Zinc USD/T',
                                                                               'Palladium USD/t,oz', 'Cobalt USD/T',
                                                                               'Iron Ore 62% fe USD/T'])]
                metals_kot.append(temp.rename(columns={'Industrial': 'Metals'}))

            elif 'Energy' in table_metals[3].columns:
                temp = table_metals[3].loc[table_metals[3]['Energy'].isin(['Coal USD/T'])]
                metals_kot.append(temp.rename(columns={'Energy': 'Metals'}))

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
                temp_table = pd.concat([table_metals[3].head(1), week_table, month_table, year_table],
                                       ignore_index=True)

                temp_table['Metals'] = 'Эн. уголь'
                temp_table['%'] = temp_table.groupby('Metals')['Price'].pct_change()
                temp_table['%'] = temp_table.groupby('Metals')['Price'].pct_change()
                try:
                    metals_coal_kot.append([temp_table['Metals'][0], temp_table['Price'][0],
                                            *temp_table['%'].tolist()[1:], str(temp_table['Date'][0]).split()[0]])
                except ValueError:
                    metals_coal_kot.append([temp_table['Metals'][0], temp_table['Price'][0],
                                            *temp_table['%'].tolist()[0:], str(temp_table['Date'][0]).split()[0]])
        return metals_coal_kot, metals_kot, metals_bloom, U7N23

    def main(self) -> None:
        session = req.Session()
        all_tables = self.table_collector(session)
        engine = create_engine(self.psql_engine)
        print('All collected')
        all_tables.append(
            ['Металлы', 'Блок котировки', 'https://www.bloomberg.com/quote/LMCADS03:COM', [pd.DataFrame()]])
        bonds_kot = pd.DataFrame(columns=['Название', 'Доходность', 'Осн,', 'Макс,', 'Мин,', 'Изм,', 'Изм, %', 'Время'])

        exchange_kot = []
        eco_frst_third = []
        world_bet = pd.DataFrame(columns=['Country', 'Last', 'Previous', 'Reference', 'Unit'])
        rus_infl = pd.DataFrame(
            columns=['Дата', 'Ключевая ставка, % годовых', 'Инфляция, % г/г', 'Цель по инфляции, %'])

        U7N23 = []
        metals_kot = []
        metals_coal_kot = []
        metals_bloom = pd.DataFrame(columns=['Metals', 'Price', 'Day'])

        size_tables = len(all_tables)
        for enum, tables_row in enumerate(all_tables):
            print('{}/{}'.format(enum + 1, size_tables))
            if tables_row[2].split('/')[-1]:
                source_page = tables_row[2].split('/')[-1]
            else:
                source_page = tables_row[2].split('/')[-2]

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

        metal_writer = pd.ExcelWriter('sources/tables/metal.xlsx')
        big_table = pd.DataFrame(columns=['Metals', 'Price', 'Day', '%', 'Weekly', 'Monthly', 'YoY', 'Date'])
        metals_coal_kot_table = pd.DataFrame(metals_coal_kot, columns=['Metals', 'Price', 'Weekly', 'Date'])
        U7N23_df = pd.DataFrame(U7N23, columns=['Metals', 'Price'])
        for table in metals_kot:
            big_table = pd.concat([big_table, table], ignore_index=True)
        big_table = pd.concat([big_table, metals_coal_kot_table, metals_bloom, U7N23_df], ignore_index=True)

        big_table.to_excel(metal_writer, sheet_name='Металы')
        # Write to metals DB
        big_table.to_sql('metals', if_exists='replace', index=False, con=engine)

        exchange_writer = pd.ExcelWriter('sources/tables/exc.xlsx')
        fx_df = pd.DataFrame(exchange_kot, columns=['Валюта', 'Курс']) \
            .drop_duplicates(subset=['Валюта'], ignore_index=True)
        fx_df.to_excel(exchange_writer, sheet_name='Курсы валют')
        # Write to fx DB
        fx_df.to_sql('exc', if_exists='replace', index=False, con=engine)

        eco_writer = pd.ExcelWriter('sources/tables/eco.xlsx')
        eco_stake = pd.DataFrame(eco_frst_third)
        eco_stake.to_excel(eco_writer, sheet_name='Ставка')
        world_bet.to_excel(eco_writer, sheet_name='Ключевые ставки ЦБ мира')
        rus_infl.to_excel(eco_writer, sheet_name='Инфляция в России')
        #write to eco_stake DB
        eco_stake.to_sql('eco_stake', if_exists='replace', index=False, con=engine)
        #write to eco_global_stake DB
        world_bet.to_sql('eco_global_stake', if_exists='replace', index=False, con=engine)
        #write to eco_rus_influence DB
        rus_infl.to_sql('eco_rus_influence', if_exists='replace', index=False, con=engine)

        bonds_writer = pd.ExcelWriter('sources/tables/bonds.xlsx')
        bonds_kot.to_excel(bonds_writer, sheet_name='Блок котировки')
        #write to bonds DB
        bonds_kot.to_sql('bonds', if_exists='replace', index=False, con=engine)

        bonds_writer.close()
        eco_writer.close()
        exchange_writer.close()
        metal_writer.close()

        return None

    def collect_research(self) -> (dict, dict):
        """
        Collect all type of reviews from CIB Research
        And get page html with fin data about companies from CIB Research
        :return: dict with data reviews, dict with html page
        """

        firefox_options = webdriver.FirefoxOptions()
        driver = webdriver.Remote(command_executor='http://localhost:4444/wd/hub', options=firefox_options)

        economy, money, comm = 'econ', 'money', 'comm'
        authed_user = ue.ResearchParser(driver)

        # economy
        eco_day = authed_user.get_reviews(url_part=economy, tab='Ежедневные', title='Экономика - Sberbank CIB')
        # eco_month = authed_user.get_reviews(url_part=economy, tab='Все', title='Экономика - Sberbank CIB',
        #                                     name_of_review='Экономика России. Ежемесячный обзор')
        # print('economy...ok')
        #
        # # bonds
        # bonds_day = authed_user.get_reviews(url_part=money, tab='Ежедневные', title='FX &amp; Ставки - Sberbank CIB',
        #                                     name_of_review='Валютный рынок и процентные ставки', type_of_review='bonds',
        #                                     count_of_review=2)
        #
        # bonds_month = authed_user.get_reviews(url_part=money, tab='Все', title='FX &amp; Ставки - Sberbank CIB',
        #                                       name_of_review='Денежный рынок. Еженедельный обзор')
        # print('bonds...ok')
        # # exchange
        # exchange_day = authed_user.get_reviews(url_part=money, tab='Ежедневные', title='FX &amp; Ставки - Sberbank CIB',
        #                                        name_of_review='Валютный рынок и процентные ставки',
        #                                        type_of_review='exchange', count_of_review=2)
        # exchange_month_uan = authed_user.get_reviews(url_part=economy, tab='Все', title='Экономика - Sberbank CIB',
        #                                              name_of_review='Ежемесячный обзор по юаню')
        # exchange_month_soft = authed_user.get_reviews(url_part=economy, tab='Все', title='Экономика - Sberbank CIB',
        #                                               name_of_review='Ежемесячный дайджест по мягким валютам')
        # print('exchange...ok')
        # # commodity
        # commodity_day = authed_user.get_reviews(url_part=comm, tab='Ежедневные', title='Сырьевые товары - Sberbank CIB',
        #                                         name_of_review='Сырьевые рынки', type_of_review='commodity')
        # print('commodity...ok')
        # exchange_month = exchange_month_uan + exchange_month_soft
        reviews = {
            'Economy day': eco_day,
            # 'Economy month': eco_month,
            # 'Economy month': eco_month,
            # 'Bonds day': bonds_day,
            # 'Bonds month': bonds_month,
            # 'Exchange day': exchange_day,
            # 'Exchange month': exchange_month,
            # 'Commodity day': commodity_day
        }

        # companies
        companies_pages_html = dict()
        for company in self.list_of_companies:
            page_html = authed_user.get_company_html_page(url_part=company[0])
            companies_pages_html[company[1]] = page_html
        print('companies page...ok')

        driver.close()

        return reviews, companies_pages_html

    def save_reviews(self, reviews_to_save:  Dict[str, List[Tuple]]) -> None:
        """
        Save all reviews into the database.
        :param reviews_to_save: dict of list of the reviews
        """
        # TODO: мб сделать одну таблицу для обзоров ?

        engine = create_engine(self.psql_engine)
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

        print('SAVE REVIEWS...ok')

    # def process_companies_data(self, pages_html):
    #     pass


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    while True:
        runner = Main()
        runner.parser_obj.get_proxy_addresses()
        # runner.main()

        # collect and save research data
        reviews_dict, companies_pages_html_dict = runner.collect_research()
        runner.save_reviews(reviews_dict)
        # runner.process_companies_data(companies_pages_html_dict)

        i = 0
        with open('sources/tables/time.txt', 'w') as f:
            f.write(datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
        print('Wait 30 minuts befor recollect data...')
        while i <= 30:
               i += 1
               time.sleep(60)
               print('In waiting. \n{}/30 minuts'.format(30-i))
