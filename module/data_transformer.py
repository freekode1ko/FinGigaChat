from bot_runner import read_curdatetime
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
import config
import copy
import six


class Transformer:

    @staticmethod
    def load_urls_as_list(path: str, filedName: str) -> pd.DataFrame:
        """
        Get sources url from excel file
        :param path: path to .xlsx file
        :param filedName: Column name where holding all urls
        :return: return list with urls
        """
        return pd.read_excel(path)[['Алиас', 'Блок', filedName]].values.tolist()

    @staticmethod
    def get_table_from_html(euro_standard: bool, html: str):
        """
        Take all tables from html code
        :param euro_standard: Bool value for separators of decimals and thousands
        :param html: HTML codes as text
        :return: list with DataFrames
        """
        # if euro_standard:
        #     return pd.read_html(html)
        html_rep = html.replace('.', ',')
        return pd.read_html(html_rep, decimal=',', thousands='.')

    @staticmethod
    def formatter(f):
        """
        Format value
        :param f: value to format
        :return: formatted value
        """
        try:
            f = float(f)
        except ValueError:
            return str(f)
        except:
            pass

        if pd.isna(f):
            return 'NaN'
        elif isinstance(f, (int, float)):
            if abs(f) < 1000:
                return '{:,.1f}'.format(f).replace('.00', '').replace('.0', '').replace(',', ' ')
            else:
                return '{:,.0f}'.format(f).replace('.00', '').replace('.0', '').replace(',', ' ')

    @staticmethod
    def render_mpl_table(data, name, col_width=1.0, row_height=0.625, font_size=14,
                         header_color='#000000', row_colors=['#030303', '#0E0E0E'],
                         edge_color='grey', bbox=[-0.17, -0.145, 1.3, 1.31],
                         header_columns=0, title=None, alias=None, fin=None, ax=None, **kwargs):
        data = data.fillna('-')
        if title is None:
            title = name
        if alias:
            size = None
            bbox = [-0.17, -0.2, 1.3, 1.145]
            col_widths = [0.2, 0.05, 0.05, 0.05, 0.05, 0.05]

            if ax is None:
                row_height = 1
                size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
                y_delta = size[1] + 0.145
                size = (15, y_delta)
                fig, ax = plt.subplots(figsize=size)
                fig.patch.set_facecolor('black')
                ax.axis('off')

            if fin:
                data = data.reset_index(drop=True)
                for index, row in data.iterrows():
                    if row.to_list().count('-') == 5:
                        new_values = [''] * 5
                        new_values.insert(0, data.iloc[index]['Финансовые показатели'])
                        data.loc[index] = new_values

                vectorized_formatter = np.vectorize(Transformer.formatter)
                cell_text = vectorized_formatter(data.values)
            else:
                cell_text = data.values

            mpl_table = ax.table(cellText=cell_text, bbox=bbox, colLabels=data.columns, colWidths=col_widths,
                                 cellLoc='center', **kwargs)

            plt.subplots_adjust(bottom=0.25)
            mpl_table.auto_set_font_size(False)
            mpl_table.set_fontsize(font_size)

            for k, cell in six.iteritems(mpl_table._cells):
                cell.set_edgecolor(edge_color)
                if k[0] == 0 or k[1] < header_columns:
                    cell.set_text_props(weight='bold', color='w', fontsize=20)
                    cell.set_facecolor(header_color)
                    cell.get_text().set_color('white')
                else:
                    cell.set_text_props(fontsize=18)
                    cell.set_facecolor(row_colors[k[0] % len(row_colors)])
                    cell.get_text().set_color('white')
                    if all(mpl_table._cells.get((k[0], j), None) is None
                           or mpl_table._cells[(k[0], j)]._text.get_text() == '' for j in range(2, 3)):
                        cell.set_text_props(weight='bold', fontsize=20, color='white')
                        cell.set_linewidth(0)
                        rgb_color = (30 / 255, 31 / 255, 36 / 255)
                        cell.set_facecolor(rgb_color)

            title_loc = 'center'

            if fin:
                y_height = 1
                fontsize = 26
            else:
                y_height = 1.1
                fontsize = 20

            ax.text(0.5, y_height, alias, fontsize=fontsize, fontweight='bold',
                    color='white', ha=title_loc, va='top', transform=ax.transAxes,
                    bbox=dict(facecolor='none', edgecolor='none'),
                    clip_on=False)

            sample_of_img_title_view = 'Sber Analytical Research. Данные на {}*'
            sample_of_img_title_view = sample_of_img_title_view.format(read_curdatetime().split()[0])
            title_loc = 'left'
            ax.text(-0.1, -0.245, sample_of_img_title_view, fontsize=10, fontweight='bold',
                    color='white', ha=title_loc, va='top', transform=ax.transAxes,
                    bbox=dict(facecolor='none', edgecolor='none'),
                    clip_on=False)
        else:
            if ax is None:
                size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
                fig, ax = plt.subplots(figsize=size)
                fig.facecolor = 'black'
                ax.axis('off')

            mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns,
                                 cellLoc='center', **kwargs)
            mpl_table.auto_set_font_size(False)
            mpl_table.set_fontsize(font_size)

            for k, cell in six.iteritems(mpl_table._cells):
                cell.set_edgecolor(edge_color)
                if k[0] == 0 or k[1] < header_columns:
                    cell.set_text_props(weight='bold', color='w')
                    cell.set_facecolor(header_color)
                    cell.get_text().set_color('white')
                else:
                    cell.set_facecolor(row_colors[k[0] % len(row_colors)])
                    cell.get_text().set_color('white')

        # save png and return it to user
        png_path = '{}/img/{}_table.png'.format('./sources', name)
        plt.savefig(png_path, transparent=False)

    def __draw_plot(df, name):
        labels = []
        xticks = []
        for i, date in enumerate(df['date']):
            date_obj_year = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S').year
            if date_obj_year not in labels:
                labels.append(date_obj_year)
                xticks.append(df.iloc[i]['x'])

        while len(labels) > 5:
            del labels[0]
            del xticks[0]

        first = df.loc[df['x'] == xticks[0], 'x'].index[0]
        fig, ax = plt.subplots()
        fig.canvas.draw()

        for spine in ax.spines.values():
            spine.set_visible(False)

        labels_new = []
        for i, label in enumerate(labels):
            if i != len(labels) - 1:
                labels_new.append(label)
                labels_new.append('')
            else:
                labels_new.append(label)
                labels_new.append('')

        xticks_new = []
        for i, xtick in enumerate(xticks):
            if i != len(labels) - 1:
                xticks_new.append(xtick)
                xticks_new.append((xticks[i + 1] - xticks[i]) / 2 + xtick)
            else:
                xticks_new.append(xtick)
                xticks_new.append((xticks[i] - xticks[i - 1]) / 2 + xtick)

        minor_locator = ticker.AutoMinorLocator(n=2)
        plt.gca().yaxis.set_minor_locator(minor_locator)
        plt.gca().tick_params(which='minor', length=4, color='black', width=1)

        def format_yticks(value, pos):
            return '{:,.0f}'.format(value).replace(',', ' ')

        formatter = ticker.FuncFormatter(format_yticks)
        ax.yaxis.set_major_formatter(formatter)

        plt.xticks(xticks_new)
        ax.set_xticklabels(labels_new)
        ax.yaxis.set_tick_params(length=0)

        color = (30 / 255, 212 / 255, 132 / 255)
        ax.plot(df['x'][first:], df['y'][first:], color=color)
        ax.yaxis.tick_right()

        plt.xlim(df['x'].iloc[first], df['x'].iloc[-1])

        y = df['y'].iloc[-1]
        ax.axhline(y=y, color=color, linestyle='dotted')

        x = df['x'].iloc[-1]
        delta_x = (x / 100)
        y = round(y, 1)
        delta_y = (y / 100) * 5
        x_name = df['x'].iloc[first]
        y_name = df['y'][first:].max()

        ax.text(x_name, y_name, name, fontsize=12)
        ax.text(x - delta_x, y + delta_y, y, fontsize=10, weight='bold')
        ax.plot(x, y, 'o', markersize=6, color=color)

    @staticmethod
    def five_year_graph(data, name):
        """
        Plot 5Y charts
        :param data: data to plot in Dataframe or json format
        :param name: charts name
        """

        if isinstance(data, pd.DataFrame):
            Transformer.__draw_plot(data, name)
        else:
            df = pd.DataFrame(data.json()['series'][0]['data'])
            Transformer.__draw_plot(df, name)

        name = name.replace('/', '_')
        name = name.replace(' ', '_')
        name = name.split(',')
        name = f'{name[0]}_graph.png'
        # save png and return it to user
        png_path = '{}/img/{}'.format('./sources', name)
        plt.savefig(png_path, transparent=False)

    @staticmethod
    def unix_to_default(timestamp):
        """
        Transform unix-time to world-time
        :param timestamp: unix formatted timestamp
        """

        date_time = datetime.datetime.fromtimestamp(timestamp / 1000)
        formatted_date = date_time.strftime('%Y-%m-%dT%H:%M:%S')
        return formatted_date

    @staticmethod
    def default_to_unix():
        """
        Transform world-time now to unix-time
        """

        now = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        date_time = datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
        unix_timestamp = int(date_time.timestamp())
        return str(unix_timestamp)

    @staticmethod
    def url_updater():
        """
        Create urls to charts 
        """

        unix_timestamp = Transformer.default_to_unix()
        charts_links = copy.deepcopy(config.charts_links)
        commodities = copy.deepcopy(config.dict_of_commodities)

        for commodity in commodities:
            if len(commodities[commodity]['links']) > 1:
                name = commodities[commodity]['links'][0]
                commodities[commodity]['links'][0] = charts_links['investing_link'].replace('name_name', name)
            elif commodities[commodity]['naming'] != 'Gas':
                name = commodities[commodity]['links'][0]
                commodities[commodity]['links'][0] = charts_links['metals_wire_link'].replace('name_name', name)
                commodities[commodity]['links'][0] = commodities[commodity]['links'][0] \
                    .replace('date_date', unix_timestamp)
        return commodities


class Newsletter:
    """ Создает текста для рассылок """
    __newsletter_dict = dict(weekly_result='Основные события прошедшей недели',
                             weekly_event='Календарь и прогнозы текущей недели')

    @classmethod
    def get_newsletter_dict(cls):
        return cls.__newsletter_dict

    @classmethod
    def make_weekly_result(cls):
        """ Создает текст для рассылки "Итоги недели" """
        title = 'Итоги недели'
        slide_path_text = 'sources/weeklies/week_results.png'
        slide_path_table = 'sources/weeklies/rialto_pulse.png'
        img_path_list = [slide_path_text, slide_path_table]
        newsletter = (f'<b>{title}</b>\n'
                      f'')
        return title, newsletter, img_path_list

    @classmethod
    def make_weekly_event(cls):
        """ Создает текст для рассылки "Что нас ждет на этой неделе?" """
        title = 'Что нас ждет на этой неделе?'
        slide_path_text = 'sources/weeklies/important_events.png'
        slide_path_table = 'sources/weeklies/exc_rate_prediction.png'
        img_path_list = [slide_path_text, slide_path_table]
        newsletter = (f'<b>{title}</b>\n'
                      f'')
        return title, newsletter, img_path_list

