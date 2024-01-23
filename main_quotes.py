from dateutil.relativedelta import relativedelta
from module.logger_base import selector_logger
import module.data_transformer as dt
import module.crawler as crawler

from sqlalchemy import create_engine, NullPool

from pathlib import Path
import requests as req
from lxml import html
import pandas as pd
import datetime
import warnings
import config
import time
import click

from utils.cli_utils import get_period


class QuotesGetter:
    def __init__(self, logger):
        self.logger = logger
        parser_obj = crawler.Parser(self.logger)
        path_to_source = './sources/ТЗ.xlsx'
        transformer_obj = dt.Transformer()
        psql_engine = config.psql_engine

        self.psql_engine = psql_engine
        self.parser_obj = parser_obj
        self.path_to_source = path_to_source
        self.transformer_obj = transformer_obj

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
                self.logger.info(f'Таблиц добавлено: {len(tables)}')
            except ValueError as val_err:
                self.logger.error(f'Таблицы не найдены. {val_err}: {page_html[:100]}')
        return all_tables

    def bond_block(self, table_bonds: list) -> pd.DataFrame:
        bonds_kot = pd.DataFrame(columns=['Название', 'Доходность', 'Осн,', 'Макс,', 'Мин,', 'Изм,', 'Изм, %', 'Время'])
        if table_bonds[0] == 'Облигации' and table_bonds[1] == 'Блок котировки':
            bonds_kot = pd.concat([bonds_kot, table_bonds[3]])
            self.logger.info('Таблица Облигации (Котировки) собрана')
        return bonds_kot

    def economic_block(self, table_eco: list, page_eco: str):
        eco_frst_third = []
        world_bet = pd.DataFrame(columns=['Country', 'Last', 'Previous', 'Reference', 'Unit'])
        rus_infl = pd.DataFrame(columns=['Дата', 'Ключевая ставка, % годовых',
                                         'Инфляция, % г/г', 'Цель по инфляции, %'])
        if table_eco[0] == 'Экономика' and page_eco == 'KeyRate':
            eco_frst_third.append(['Текущая ключевая ставка Банка России', table_eco[3]['Ставка'][0]])
            self.logger.info('Таблица Экономика (KeyRate) собрана')

        elif table_eco[0] == 'Экономика' and page_eco == 'ruonia':
            ruonia = table_eco[3].loc[table_eco[3][0] == 'Ставка RUONIA, %'][2].values.tolist()[0]
            eco_frst_third.append(['Текущая ставка RUONIA', ruonia])
            self.logger.info('Таблица Экономика (ruonia) собрана')

        elif table_eco[0] == 'Экономика' and page_eco == 'interest-rate':
            if 'Actual' in table_eco[3]:
                eco_frst_third.append(['LPR Китай', table_eco[3]['Actual'][0]])
                self.logger.info('Таблица interest-rate (LPR Китай) собрана')

            elif 'Country' in table_eco[3]:
                world_bet = pd.concat([world_bet, table_eco[3]])
                self.logger.info('Таблица interest-rate (Country) собрана')

        elif table_eco[0] == 'Экономика' and page_eco == 'infl':
            rus_infl = pd.concat([rus_infl, table_eco[3]])
            self.logger.info('Таблица Экономика (infl) собрана')

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
                            self.logger.info('Таблица exchange_kot (usd-rub) собрана')
                            break
                    except IndexError:
                        self.logger.warning('Не та таблица попала на обработку')
                    except Exception as ex:
                        self.logger.error(f'Ошибка при обработке таблицы: {ex}')
            elif {'Exchange', 'Last', 'Time'}.issubset(table_exchange[3].columns):
                row = [exchange_page, table_exchange[3].loc[table_exchange[3]['Exchange'] ==
                                                            'Real-time Currencies']['Last'].values.tolist()[0]]
                exchange_kot.append(row)
                self.logger.info('Таблица exchange_kot (Exchange) собрана')

        elif table_exchange[0] == 'Курсы валют' and exchange_page in ['usd-cnh', 'usdollar']:
            euro_standard, page_html = self.parser_obj.get_html(table_exchange[2], session)
            tree = html.fromstring(page_html)
            data = tree.xpath('//*[@id="__next"]/div[2]/div//text()')
            price = self.find_number(data)
            row = [exchange_page, price]
            exchange_kot.append(row)
            self.logger.info('Таблица exchange_kot (usd-cnh) собрана')
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
                self.logger.error(f'Ошибка ({ex}) получения таблицы с медью!')
            metals_bloom = pd.concat([metals_bloom, temp_df], ignore_index=True)
            self.logger.info('Таблица metals_bloom собрана')

        elif table_metals[0] == 'Металлы' and page_metals == 'U7*0':
            if {'Last', 'Change'}.issubset(table_metals[3].columns):
                jap_coal = table_metals[3][table_metals[3].Symbol.str.contains('U7.24')]
                U7N23.append(['кокс. уголь', jap_coal.values.tolist()[0][1]])
                self.logger.info('Таблица U7N24 собрана')

        elif table_metals[0] == 'Металлы' and page_metals == 'commodities':
            if 'Metals' in table_metals[3].columns:
                temp = table_metals[3].loc[table_metals[3]['Metals'].isin(['Gold USD/t,oz', 'Silver USD/t,oz',
                                                                           'Platinum USD/t,oz', 'Lithium CNY/T'])]
                metals_kot.append(temp)
                self.logger.info('Таблица metals_kot (Metals) собрана')

            elif 'Industrial' in table_metals[3].columns:
                temp = table_metals[3].loc[table_metals[3]['Industrial'].isin(['Aluminum USD/T', 'Nickel USD/T',
                                                                               'Lead USD/T', 'Zinc USD/T',
                                                                               'Palladium USD/t,oz', 'Cobalt USD/T',
                                                                               'Iron Ore 62% fe USD/T'])]
                metals_kot.append(temp.rename(columns={'Industrial': 'Metals'}))
                self.logger.info('Таблица metals_kot (Industrial) собрана')

            elif 'Energy' in table_metals[3].columns:
                temp = table_metals[3].loc[table_metals[3]['Energy'].isin(['Coal USD/T'])]
                metals_kot.append(temp.rename(columns={'Energy': 'Metals'}))
                self.logger.info('Таблица metals_kot (Energy) собрана')

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
                    self.logger.info('Таблица metals_coal_kot собрана')
                except ValueError:
                    metals_coal_kot.append([temp_table['Metals'][0], temp_table['Price'][0],
                                            *temp_table['%'].tolist()[0:], str(temp_table['Date'][0]).split()[0]])
                    self.logger.warning('Сдвиг в таблице с котировками (metals_coal_kot)')
        return metals_coal_kot, metals_kot, metals_bloom, U7N23

    def collect(self) -> None:
        session = req.Session()
        all_tables = self.table_collector(session)
        engine = create_engine(self.psql_engine, poolclass=NullPool)
        self.logger.info('Котировки собраны, запускаем обработку')
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
        self.logger.info(f'Обработка собранных таблиц ({size_tables}).')
        for enum, tables_row in enumerate(all_tables):
            self.logger.info('{}/{}'.format(enum + 1, size_tables))
            url_index = -1 if tables_row[2].split('/')[-1] else -2
            source_page = tables_row[2].split('/')[url_index]
            self.logger.info(f'Сборка таблицы {source_page} из блока {tables_row[0]}')
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
        self.logger.info('Записана страница с Металлами')
        big_table.to_sql('metals', if_exists='replace', index=False, con=engine)
        self.logger.info('Таблица metals записана')

        # Запись Курсов в БД и Локальное хранилище
        exchange_writer = pd.ExcelWriter('sources/tables/exc.xlsx')
        fx_df = pd.DataFrame(exchange_kot, columns=['Валюта', 'Курс']) \
            .drop_duplicates(subset=['Валюта'], ignore_index=True)
        fx_df.to_excel(exchange_writer, sheet_name='Курсы валют')
        self.logger.info('Записана страница с Курсами')
        # Write to fx DB
        fx_df.to_sql('exc', if_exists='replace', index=False, con=engine)
        self.logger.info('Таблица exc записана')

        # Запись Экономики в БД и Локальное хранилище
        eco_writer = pd.ExcelWriter('sources/tables/eco.xlsx')
        eco_stake = pd.DataFrame(eco_frst_third)
        eco_stake.to_excel(eco_writer, sheet_name='Ставка')
        self.logger.info('Записана страница с Ставкой')
        world_bet.to_excel(eco_writer, sheet_name='Ключевые ставки ЦБ мира')
        self.logger.info('Записана страница с КС ЦБ')
        rus_infl.to_excel(eco_writer, sheet_name='Инфляция в России')
        self.logger.info('Записана страница с Инфляцией')

        eco_stake.to_sql('eco_stake', if_exists='replace', index=False, con=engine)
        self.logger.info('Таблица eco_stake записана')
        world_bet.to_sql('eco_global_stake', if_exists='replace', index=False, con=engine)
        self.logger.info('Таблица eco_global_stake записана')
        rus_infl.to_sql('eco_rus_influence', if_exists='replace', index=False, con=engine)
        self.logger.info('Таблица eco_rus_influence записана')

        # Запись Котировок в БД и Локальное хранилище
        bonds_writer = pd.ExcelWriter('sources/tables/bonds.xlsx')
        bonds_kot.to_excel(bonds_writer, sheet_name='Блок котировки')
        self.logger.info('Записана страница с Котировками')
        bonds_kot.to_sql('bonds', if_exists='replace', index=False, con=engine)
        self.logger.info('Таблица bonds записана')

        self.logger.info('Закрытие записи локальных бэкапов')
        bonds_writer.close()
        eco_writer.close()
        exchange_writer.close()
        metal_writer.close()

        return None

    def save_date_of_last_build(self):
        engine = create_engine(self.psql_engine, poolclass=NullPool)
        cur_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        cur_time_in_box = pd.DataFrame([[cur_time]], columns=['date_time'])
        cur_time_in_box.to_sql('date_of_last_build', if_exists='replace', index=False, con=engine)
        self.logger.info('Таблица date_of_last_build записана')


@click.command()
@click.option(
    '-p',
    '--period',
    default="15m",
    show_default=True,
    type=str,
    help="Периодичность сборки котировок\n"
         "s - секунды\n"
         "m - минуты (значение по умолчанию)\n"
         "h - часы\n"
         "d - дни",
)
def main(period):
    """
    Сборщик котировок
    """
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
        runner = QuotesGetter(logger)
        logger.info('Загрузка прокси')
        runner.parser_obj.get_proxy_addresses()

        try:
            logger.info('Начало сборки котировок')
            runner.collect()
        except Exception as e:
            logger.error(f'Ошибка при сборке котировок: {e}')
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
