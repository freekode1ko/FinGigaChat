from dateutil.relativedelta import relativedelta
from config import research_base_url as rebase
import module.data_transformer as dt
import module.user_emulator as ue
import module.crawler as crawler
from selenium import webdriver
from lxml import html
import pandas as pd
import warnings
import time


def table_collector() -> list:
    path_to_source = 'Sources/ТЗ.xlsx'
    transformer_obj = dt.Transformer()
    parser_obj = crawler.Parser()
    all_tables = []

    urls = transformer_obj.load_urls_as_list(path_to_source, 'Источник')
    df_urls = pd.DataFrame(urls).dropna().drop_duplicates()
    urls = df_urls.values.tolist()
    for url in urls:
        euro_standard, page_html = parser_obj.get_html(url[2])
        print(euro_standard, url[2])
        try:
            tables = transformer_obj.get_table_from_html(euro_standard, page_html)
            for table in tables:
                all_tables.append([url[0].split('/')[0], *url[1:], table])
            print('Tables added {}'.format(len(tables)))
        except ValueError as val_err:
            print(url[2])
            print('No tables found: {} : {}'.format(val_err, page_html[:100]))
    return all_tables


def bond_block(table_bonds):
    bonds_kot = pd.DataFrame(columns=['Название', 'Доходность', 'Осн,', 'Макс,', 'Мин,', 'Изм,', 'Изм, %', 'Время'])
    if table_bonds[0] == 'Облигации' and table_bonds[1] == 'Блок котировки':
        bonds_kot = pd.concat([bonds_kot, table_bonds[3]])
    return bonds_kot


def economic_block(table_eco, page_eco):
    eco_frst_third = []
    world_bet = pd.DataFrame(columns=['Country', 'Last', 'Previous', 'Reference', 'Unit'])
    rus_infl = pd.DataFrame(columns=['Дата', 'Ключевая ставка, % годовых', 'Инфляция, % г/г', 'Цель по инфляции, %'])
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


def exchange_block(table_exchange, exchange_page):
    exchange_kot = []
    parser_obj = crawler.Parser()
    if table_exchange[0] == 'Курсы валют' and exchange_page in ['usd-rub', 'eur-rub', 'cny-rub', 'eur-usd']:
        if {'Exchange', 'Last', 'Time'}.issubset(table_exchange[3].columns):
            row = [exchange_page, table_exchange[3].loc[table_exchange[3]['Exchange'] == 'Real-time Currencies'][
                'Last'].values.tolist()[0]]
            exchange_kot.append(row)

    elif table_exchange[0] == 'Курсы валют' and exchange_page in ['usd-cny', 'usdollar']:
        euro_standart, page_html = parser_obj.get_html(table_exchange[2])
        tree = html.fromstring(page_html)
        object_xpath = '//*[@id="__next"]/div[2]/div/div/div[2]/main/div/div[1]/div[2]/div[1]'
        price = tree.xpath('{}/span/text()'.format(object_xpath))
        row = [exchange_page, *price]
        exchange_kot.append(row)
    return exchange_kot


def metal_block(table_metals, page_metals):
    U7N23 = []
    metals_kot = []
    metals_coal_kot = []
    parser_obj = crawler.Parser()
    metals_bloom = pd.DataFrame(columns=['Metals', 'Price', 'Day'])

    if table_metals[0] == 'Металлы' and page_metals == 'LMCADS03:COM':
        euro_standart, page_html = parser_obj.get_html(table_metals[2])
        tree = html.fromstring(page_html)
        object_xpath = '//*[@id="root"]/div/div/section/section[1]/div/div[2]/section[1]/section/section/section'
        price = tree.xpath('{}/div[1]/span[1]/text()'.format(object_xpath))
        price_diff = tree.xpath('{}/div[2]/span[2]/text()'.format(object_xpath))
        row = ['Медь', *price, *price_diff]
        temp_df = pd.DataFrame([row], columns=['Metals', 'Price', 'Day'])
        metals_bloom = pd.concat([metals_bloom, temp_df], ignore_index=True)

    elif table_metals[0] == 'Металлы' and page_metals == 'U7*0':
        if {'Last', 'Change'}.issubset(table_metals[3].columns):
            print(table_metals[3])
            jap_coal = table_metals[3][table_metals[3].Symbol.str.contains('U7.23')]
            U7N23.append(['кокс. уголь', jap_coal.values.tolist()[0][1]])

    elif table_metals[0] == 'Металлы' and page_metals == 'commodities':
        if 'Metals' in table_metals[3].columns:
            temp = table_metals[3].loc[table_metals[3]['Metals'].isin(['Gold USD/t.oz', 'Silver USD/t.oz',
                                                                       'Platinum USD/t.oz', 'Lithium CNY/T'])]
            metals_kot.append(temp)

        elif 'Industrial' in table_metals[3].columns:
            temp = table_metals[3].loc[table_metals[3]['Industrial'].isin(['Aluminum USD/T', 'Nickel USD/T',
                                                                           'Lead USD/T', 'Zinc USD/T',
                                                                           'Palladium USD/t.oz', 'Cobalt USD/T',
                                                                           'Iron Ore 62% fe USD/T'])]
            metals_kot.append(temp.rename(columns={'Industrial': 'Metals'}))

        elif 'Energy' in table_metals[3].columns:
            temp = table_metals[3].loc[table_metals[3]['Energy'].isin(['Coal USD/T'])]
            metals_kot.append(temp.rename(columns={'Energy': 'Metals'}))

    elif table_metals[0] == 'Металлы' and page_metals == 'coal-(api2)-cif-ara-futures-historical-data':
        if 'Price' in table_metals[3].columns:
            table_metals[3]['Date'] = table_metals[3]['Date'].astype('datetime64[ns]')
            day_day = table_metals[3]['Date'][0] - relativedelta(days=1)
            week_day = table_metals[3]['Date'][0] - relativedelta(weeks=1)
            month_day = table_metals[3]['Date'][0] - relativedelta(months=1)
            year_day = table_metals[3]['Date'][0] - relativedelta(years=1)

            day_table = table_metals[3].loc[table_metals[3]['Date'] == str(day_day).split()[0]]
            week_table = table_metals[3].loc[table_metals[3]['Date'] == str(week_day).split()[0]]
            month_table = table_metals[3].loc[table_metals[3]['Date'] == str(month_day).split()[0]]
            year_table = table_metals[3].loc[table_metals[3]['Date'] == str(year_day).split()[0]]
            temp_table = pd.concat([table_metals[3].head(1), day_table, week_table, month_table, year_table],
                                   ignore_index=True)

            temp_table['Metals'] = 'Железорудное сырье'
            temp_table['%'] = temp_table.groupby('Metals')['Price'].pct_change()
            metals_coal_kot.append([temp_table['Metals'][0], temp_table['Price'][0],
                                    *temp_table['%'].tolist()[1:], str(temp_table['Date'][0]).split()[0]])
    return metals_coal_kot, metals_kot, metals_bloom, U7N23


def main():
    all_tables = table_collector()
    print('All collected')
    all_tables.append(['Металлы', 'Блок котировки', 'https://www.bloomberg.com/quote/LMCADS03:COM', [pd.DataFrame()]])
    bonds_kot = pd.DataFrame(columns=['Название', 'Доходность', 'Осн,', 'Макс,', 'Мин,', 'Изм,', 'Изм, %', 'Время'])

    exchange_kot = []
    eco_frst_third = []
    world_bet = pd.DataFrame(columns=['Country', 'Last', 'Previous', 'Reference', 'Unit'])
    rus_infl = pd.DataFrame(columns=['Дата', 'Ключевая ставка, % годовых', 'Инфляция, % г/г', 'Цель по инфляции, %'])

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
        bonds_kot = pd.concat([bonds_kot, bond_block(tables_row)])

        # ECONOMIC BLOCK
        eco_list, world_bet_df, rus_infl_df = economic_block(tables_row, source_page)
        eco_frst_third += eco_list
        world_bet = pd.concat([world_bet, world_bet_df])
        rus_infl = pd.concat([rus_infl, rus_infl_df])

        # EXCENGE BLOCK
        exchange_kot += exchange_block(tables_row, source_page)

        # METALS BLOCK
        metal_coal_ls, metal_cat_ls, metal_bloom_df, U7_ls = metal_block(tables_row, source_page)
        U7N23 += U7_ls
        metals_coal_kot += metal_coal_ls
        metals_kot += metal_cat_ls
        metals_bloom = pd.concat([metals_bloom, metal_bloom_df])

    metal_writer = pd.ExcelWriter('sources/tables/metal.xlsx')
    big_table = pd.DataFrame(columns=['Metals', 'Price', 'Day', '%', 'Weekly', 'Monthly', 'YoY', 'Date'])
    metals_coal_kot_table = pd.DataFrame(metals_coal_kot, columns=['Metals', 'Price', 'Day', 'Weekly', 'Date'])
    U7N23_df = pd.DataFrame(U7N23, columns=['Metals', 'Price'])
    for table in metals_kot:
        big_table = pd.concat([big_table, table], ignore_index=True)
    big_table = pd.concat([big_table, metals_coal_kot_table, metals_bloom, U7N23_df], ignore_index=True)
    big_table.to_excel(metal_writer, sheet_name='Металы')

    exchange_writer = pd.ExcelWriter('sources/tables/exc.xlsx')
    pd.DataFrame(exchange_kot, columns=['Валюта', 'Курс']).drop_duplicates() \
        .to_excel(exchange_writer, sheet_name='Курсы валют')

    eco_writer = pd.ExcelWriter('sources/tables/eco.xlsx')
    pd.DataFrame(eco_frst_third).to_excel(eco_writer, sheet_name='Ставка')
    world_bet.to_excel(eco_writer, sheet_name='Ключевые ставки ЦБ мира')
    rus_infl.to_excel(eco_writer, sheet_name='Инфляция в России')

    bonds_writer = pd.ExcelWriter('sources/tables/bonds.xlsx')
    bonds_kot.to_excel(bonds_writer, sheet_name='Блок котировки')

    bonds_writer.close()
    eco_writer.close()
    exchange_writer.close()
    metal_writer.close()

    collect_research()


def collect_research():
    user_object = ue.ResearchParser()
    economy_url = '{}group/guest/econ?countryIsoCode=RUS'.format(rebase)
    money_url = '{}group/guest/money'.format(rebase)
    metal_url = '{}group/guest/comm'.format(rebase)
    company_url = '{}group/guest/companies?companyId='.format(rebase)

    driver = webdriver.Firefox()
    authed_user = user_object.auth(driver)

    ''' MAIN BLOCK '''

    # ECONOMY
    actual_reviews = user_object.get_everyday_reviews(authed_user, economy_url)
    global_eco_review = user_object.get_eco_review(authed_user, economy_url)

    # BONDS
    every_money = user_object.get_everyday_money(authed_user, money_url)
    global_money_review = user_object.get_money_review(authed_user, money_url)

    # EXCHANGE
    every_kurs = user_object.get_everyday_money(authed_user, money_url, text_filter=('Валютный рынок:', 'Прогноз.'))
    global_kurs_review_uan = user_object.get_money_review(authed_user, money_url, 'Ежемесячный обзор по юаню')
    global_kurs_review_soft = user_object.get_money_review(authed_user, money_url,
                                                           'Ежемесячный обзор по мягким валютам')

    # METALS
    every_metals = user_object.get_everyday_money(authed_user, metal_url, 'Сырьевые товары', ('>', '>'))

    ''' COMPANIES '''

    list_of_companies = [
        ['831', 'Полиметалл',
         'https://www.polymetalinternational.com/ru/investors-and-media/reports-and-results/result-centre/'],
        ['675', 'ММК', 'https://mmk.ru/ru/press-center/news/operatsionnye-rezultaty-gruppy-mmk-za-1-kvartal-2023-g/'],
        ['689', 'Норникель', 'https://www.nornickel.ru/investors/disclosure/financials/#accordion-2022'],
        ['827', 'Полюс', 'https://polyus.com/ru/investors/results-and-reports/'],
        ['798', 'Русал', 'https://rusal.ru/investors/financial-stat/annual-reports/'],
        ['714', 'Северсталь', 'https://severstal.com/rus/ir/indicators-reporting/operational-results/']]
    list_of_companies_df = pd.DataFrame(list_of_companies, columns=['ID', 'Name', 'URL'])
    transformer_obj = dt.Transformer()
    page_tables = []

    for company in list_of_companies:
        authed_user.get('{}{}'.format(company_url, company[0]))
        page_html = authed_user.page_source

        tables = transformer_obj.get_table_from_html(True, page_html)
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
            page_tables.append([tables_names[i], company[0], df])

    print('Done! Closing Browser after 30 sec...')
    time.sleep(30)
    driver.close()

    text_writer = pd.ExcelWriter('sources/tables/text.xlsx')
    pd.DataFrame(actual_reviews).to_excel(text_writer, sheet_name='Экономика. День')
    pd.DataFrame(global_eco_review).to_excel(text_writer, sheet_name='Экономика. Месяц')

    pd.DataFrame(every_money).to_excel(text_writer, sheet_name='Облиигации. День')
    pd.DataFrame(global_money_review).to_excel(text_writer, sheet_name='Облиигации. Месяц')

    pd.DataFrame(every_kurs).to_excel(text_writer, sheet_name='Курсы. День')
    pd.DataFrame(global_kurs_review_uan + global_kurs_review_soft).to_excel(text_writer, sheet_name='Курсы. Месяц')

    pd.DataFrame(every_metals[0]).to_excel(text_writer, sheet_name='Металлы. День')
    text_writer.close()

    companies_writer = pd.ExcelWriter('sources/tables/companies.xlsx')
    list_of_companies_df.to_excel(companies_writer, sheet_name='head')
    for df in page_tables:
        df[2].to_excel(companies_writer, sheet_name='{}_{}'.format(df[1], df[0]))
    companies_writer.close()

    return None


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    main()
