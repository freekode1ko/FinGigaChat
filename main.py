from dateutil.relativedelta import relativedelta
import module.data_transformer as dt
import module.crawler as crawler
from lxml import html
import pandas as pd
import warnings


def main():
    path_to_source = 'Sources/ТЗ.xlsx'
    transformer_obj = dt.Transformer()
    parser_obj = crawler.Parser()
    all_tables = []

    urls = transformer_obj.load_urls_as_list(path_to_source, 'Источник')
    df_urls = pd.DataFrame(urls).dropna().drop_duplicates()
    urls = df_urls.values.tolist()
    for url in urls:
        euro_standart, page_html = parser_obj.get_html(url[2])
        print(euro_standart, url[2])
        try:
            tables = transformer_obj.get_table_from_html(euro_standart, page_html)
            for table in tables:
                all_tables.append([url[0].split('/')[0], *url[1:], table])
            print('Tables added {}'.format(len(tables)))
        except ValueError as val_err:
            print(url[2])
            print('No tables found: {} : {}'.format(val_err, page_html[:100]))

    print('All collected')
    all_tables.append(['Металлы', 'Блок котировки', 'https://www.bloomberg.com/quote/LMCADS03:COM', [pd.DataFrame()]])
    bonds_kot = pd.DataFrame(columns=['Название', 'Доходность', 'Осн,', 'Макс,', 'Мин,', 'Изм,', 'Изм, %', 'Время'])
    bonds_anal = pd.DataFrame(columns=['Название', 'Доходность', 'Осн,', 'Макс,', 'Мин,', 'Изм,', 'Изм, %', 'Время'])
    bonds_nov = pd.DataFrame(columns=['Название', 'Доходность', 'Осн,', 'Макс,', 'Мин,', 'Изм,', 'Изм, %', 'Время'])

    eco_frst_thrd = []
    world_bet = pd.DataFrame(columns=['Country', 'Last', 'Previous', 'Reference', 'Unit'])
    rus_infl = pd.DataFrame(columns=['Дата', 'Ключевая ставка, % годовых', 'Инфляция, % г/г', 'Цель по инфляции, %'])

    exchenge_kot = []

    U7M23 = []
    metals_kot = []
    metals_bloom = pd.DataFrame(columns=['Metals', 'Price', 'Day'])
    metals_coal_kot = []

    size_tables = len(all_tables)
    for enum, table in enumerate(all_tables):
        print('{}/{}'.format(enum+1, size_tables))
        if table[2].split('/')[-1]:
            page = table[2].split('/')[-1]
        else:
            page = table[2].split('/')[-2]
        # BONDS BLOCK
        if table[0] == 'Облигации' and table[1] == 'Блок котировки':
            bonds_kot = pd.concat([bonds_kot, table[3]])
        elif table[0] == 'Облигации' and table[1] == 'Блок аналитика':
            bonds_anal = pd.concat([bonds_anal, table[3]])
        elif table[0] == 'Облигации' and table[1] == 'Блок новости':
            bonds_nov = pd.concat([bonds_nov, table[3]])

        # ECONOMIC BLOCK
        elif table[0] == 'Экономика' and page == 'KeyRate':
            eco_frst_thrd.append(['Текущая ключевая ставка Банка России', table[3]['Ставка'][0]])
        elif table[0] == 'Экономика' and page == 'ruonia':
            ruonia = table[3].loc[table[3][0] == 'Ставка RUONIA, %'][2].values.tolist()[0]
            eco_frst_thrd.append(['Текущая ставка RUONIA', ruonia])
        elif table[0] == 'Экономика' and page == 'interest-rate':
            if 'Actual' in table[3]:
                eco_frst_thrd.append(['LPR Китай', table[3]['Actual'][0]])
            elif 'Country' in table[3]:
                world_bet = pd.concat([world_bet, table[3]])
        elif table[0] == 'Экономика' and page == 'infl':
            rus_infl = pd.concat([rus_infl, table[3]])

        # EXCENGE BLOCK
        elif table[0] == 'Курсы валют' and page in ['usd-rub', 'eur-rub', 'cny-rub', 'eur-usd']:
            if {'Exchange', 'Last', 'Time'}.issubset(table[3].columns):
                row = [page, table[3].loc[table[3]['Exchange'] == 'Real-time Currencies']['Last'].values.tolist()[0]]
                exchenge_kot.append(row)
        elif table[0] == 'Курсы валют' and page in ['usd-cny', 'usdollar']:
            euro_standart, page_html = parser_obj.get_html(table[2])
            tree = html.fromstring(page_html)
            object_xpath = '//*[@id="__next"]/div[2]/div/div/div[2]/main/div/div[1]/div[2]/div[1]'
            price = tree.xpath('{}/span/text()'.format(object_xpath))
            row = [page, *price]
            exchenge_kot.append(row)

        # METALS BLOCK
        elif table[0] == 'Металлы' and page == 'LMCADS03:COM':
            euro_standart, page_html = parser_obj.get_html(table[2])
            tree = html.fromstring(page_html)
            object_xpath = '//*[@id="root"]/div/div/section/section[1]/div/div[2]/section[1]/section/section/section'
            price = tree.xpath('{}/div[1]/span[1]/text()'.format(object_xpath))
            price_diff = tree.xpath('{}/div[2]/span[2]/text()'.format(object_xpath))
            row = ['Медь', *price, *price_diff]
            temp_df = pd.DataFrame([row], columns=['Metals', 'Price', 'Day'])
            metals_bloom = pd.concat([metals_bloom, temp_df], ignore_index=True)

        elif table[0] == 'Металлы' and page == 'U7*0':
            if {'Last', 'Change'}.issubset(table[3].columns):
                U7M23.append(['кокс. уголь', table[3].loc[table[3]['Symbol'] == 'U7M23'].values.tolist()[0][1]])

        elif table[0] == 'Металлы' and page == 'commodities':
            if 'Metals' in table[3].columns:
                temp = table[3].loc[table[3]['Metals'].isin(['Gold USD/t.oz', 'Silver USD/t.oz',
                                                             'Platinum USD/t.oz', 'Lithium CNY/T'])]
                metals_kot.append(temp)

            elif 'Industrial' in table[3].columns:
                temp = table[3].loc[table[3]['Industrial'].isin(['Aluminum USD/T', 'Nickel USD/T',
                                                                 'Lead USD/T', 'Zinc USD/T',
                                                                 'Palladium USD/t.oz', 'Cobalt USD/T',
                                                                 'Iron Ore 62% fe USD/T'])]
                metals_kot.append(temp.rename(columns={'Industrial': 'Metals'}))

            elif 'Energy' in table[3].columns:
                temp = table[3].loc[table[3]['Energy'].isin(['Coal USD/T'])]
                metals_kot.append(temp.rename(columns={'Energy': 'Metals'}))

        elif table[0] == 'Металлы' and page == 'coal-(api2)-cif-ara-futures-historical-data':
            if 'Price' in table[3].columns:
                table[3]['Date'] = table[3]['Date'].astype('datetime64[ns]')
                day_day = table[3]['Date'][0] - relativedelta(days=1)
                week_day = table[3]['Date'][0] - relativedelta(weeks=1)
                month_day = table[3]['Date'][0] - relativedelta(months=1)
                year_day = table[3]['Date'][0] - relativedelta(years=1)

                day_table = table[3].loc[table[3]['Date'] == str(day_day).split()[0]]
                week_table = table[3].loc[table[3]['Date'] == str(week_day).split()[0]]
                month_table = table[3].loc[table[3]['Date'] == str(month_day).split()[0]]
                year_table = table[3].loc[table[3]['Date'] == str(year_day).split()[0]]
                temp_table = pd.concat([table[3].head(1), day_table, week_table, month_table, year_table],
                                       ignore_index=True)

                temp_table['Metals'] = 'Железорудное сырье'
                temp_table['%'] = temp_table.groupby('Metals')['Price'].pct_change()
                metals_coal_kot.append([temp_table['Metals'][0], temp_table['Price'][0],
                                        *temp_table['%'].tolist()[1:], str(temp_table['Date'][0]).split()[0]])

    metal_writer = pd.ExcelWriter('sources/tables/metal.xlsx')
    big_table = pd.DataFrame(columns=['Metals', 'Price', 'Day', '%', 'Weekly', 'Monthly', 'YoY', 'Date'])
    metals_coal_kot_table = pd.DataFrame(metals_coal_kot, columns=['Metals', 'Price', 'Day', 'Weekly', 'Date'])
    U7M23_df = pd.DataFrame(U7M23, columns=['Metals', 'Price'])
    for table in metals_kot:
        big_table = pd.concat([big_table, table], ignore_index=True)
    big_table = pd.concat([big_table, metals_coal_kot_table, metals_bloom, U7M23_df], ignore_index=True)
    big_table.to_excel(metal_writer, sheet_name='Металы')

    exchange_writer = pd.ExcelWriter('sources/tables/exc.xlsx')
    pd.DataFrame(exchenge_kot, columns=['Валюта', 'Курс']).drop_duplicates()\
        .to_excel(exchange_writer, sheet_name='Курсы валют')

    eco_writer = pd.ExcelWriter('sources/tables/eco.xlsx')
    pd.DataFrame(eco_frst_thrd).to_excel(eco_writer, sheet_name='Ставка')
    world_bet.to_excel(eco_writer, sheet_name='Ключевые ставки ЦБ мира')
    rus_infl.to_excel(eco_writer, sheet_name='Инфляция в России')

    bonds_writer = pd.ExcelWriter('sources/tables/bonds.xlsx')
    bonds_kot.to_excel(bonds_writer, sheet_name='Блок котировки')
    bonds_anal.to_excel(bonds_writer, sheet_name='Блок аналитика')
    bonds_nov.to_excel(bonds_writer, sheet_name='Блок новости')

    bonds_writer.close()
    eco_writer.close()
    exchange_writer.close()
    metal_writer.close()


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    main()
