from pandas.plotting import table
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import six
import datetime
import config

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
    def get_table_from_html(euro_standart: bool, html: str):
        """
        Take all tables from html code
        :param euro_standart: Bool value for separators of decimals and thousands
        :param html: HTML codes as text
        :return: list with DataFrames
        """
        # if euro_standart:
        #     return pd.read_html(html)
        html_rep = html.replace('.', ',')
        return pd.read_html(html_rep, decimal=',', thousands='.')

    @staticmethod
    def save_df_as_png(df: pd.DataFrame, path_to_source: str,
                       figure_size: tuple, column_width: list,
                       fontsize=10, tabla_scale=(1.2, 1.2), name='') -> None:
        """
        Get png of DataFrame as table
        :param df: DataFrame for converting in png
        :param path_to_source: Path to where save png
        :param figure_size: Size of png space. Tuple(Width, Height)
        :param column_width: Width of all columns. [column1_width, column2_width, ...]
        :param fontsize: Fontsize for text in table
        :param tabla_scale: Scale column widths by xscale and row heights by yscale. (x_scale, y_scale)
        :param name: Name of saved file. By default, will save as /_table.png
        :return: None
        """
        # generate table as png
        fig, ax = plt.subplots(figsize=figure_size)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        ax.set_frame_on(False)
        tabla = table(ax, df, loc='upper right', colWidths=column_width)
        tabla.auto_set_font_size(False)
        tabla.set_fontsize(fontsize)
        tabla.scale(tabla_scale[0], tabla_scale[1])

        # save png and return it to user
        png_path = '{}/img/{}_table.png'.format(path_to_source, name)
        plt.savefig(png_path, transparent=True)

    @staticmethod
    def render_mpl_table(data, name, col_width=1.0, row_height=0.625, font_size=14,
                         header_color='#000000', row_colors=['#030303', '#0E0E0E'],
                         edge_color='grey', bbox=[-0.17, -0.145, 1.3, 1.31],
                         header_columns=0, title=None, ax=None, **kwargs):
        data = data.fillna('-')
        if title is None:
            title = name

        # titles = [title]*len(data.columns.tolist())
        # orig_columns = data.columns.tolist()
        # columns = [(titles[i], orig_columns[i]) for i in range(0, len(titles))]
        # data = pd.DataFrame(data=data.values.tolist(),
        #                    columns=pd.MultiIndex.from_tuples(columns, names=['title', 'columns']))

        if ax is None:
            size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
            fig, ax = plt.subplots(figsize=size)
            fig.facecolor = 'black'
            # rect = patches.Rectangle((-100, -100), 70, 70, linewidth=1, edgecolor='r', facecolor='black', )
            # ax.add_patch(rect)
            # ax.set_title(title, color='black')
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
        plt.savefig(png_path, transparent=True)

    @staticmethod
    def five_year_graph(data, name):
        if type(data).__name__ == 'DataFrame':
            Transformer.__draw_plot(data)
        else:
            df = pd.DataFrame(data.json()['series'][0]['data'])
            Transformer.__draw_plot(df)
        name = name.replace('/','_')
        name = name.replace(' ','_')
        # save png and return it to user
        png_path = '{}/img/{}_graph.png'.format('./sources', name)
        plt.savefig(png_path, transparent=True)

    @staticmethod
    def unix_to_default(timestamp):
        """
        Transform unix-time to world-time
        """
        
        date_time = datetime.datetime.fromtimestamp(timestamp / 1000)
        formatted_date = date_time.strftime('%Y-%m-%dT%H:%M:%S')

        return formatted_date
    
    @staticmethod
    def default_to_unix():
        """
        Transform world-time to unix-time
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

        charts_links = config.charts_links
        commodities = config.dict_of_commodities

        for commodity in commodities:
            if len(commodities[commodity]['links']) == 1 :
                name = commodities[commodity]['links'][0]
                commodities[commodity]['links'][0] = charts_links['metals_wire_link'].replace('name_name', name)
                commodities[commodity]['links'][0] = commodities[commodity]['links'][0].replace('date_date', unix_timestamp)
            else:
                name = commodities[commodity]['links'][0]
                commodities[commodity]['links'][0] = charts_links['investing_link'].replace('name_name', name)

        return commodities
