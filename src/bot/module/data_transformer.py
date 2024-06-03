import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import six

from configs import config
from module import weekly_pulse_parse as wp_parse
from utils.base import read_curdatetime


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
        except Exception:
            pass

        if pd.isna(f):
            return 'NaN'
        elif isinstance(f, (int, float)):
            if abs(f) < 1000:
                return '{:,.1f}'.format(f).replace('.00', '').replace('.0', '').replace(',', ' ')
            else:
                return '{:,.0f}'.format(f).replace('.00', '').replace('.0', '').replace(',', ' ')

    @staticmethod
    def render_mpl_table(
        data,
        name,
        col_width=1.0,
        row_height=0.625,
        font_size=18,
        header_color='#000000',
        row_colors=['#030303', '#0E0E0E'],
        edge_color='grey',
        bbox=[-0.17, -0.145, 1.3, 1.31],
        header_columns=0,
        title=None,
        alias=None,
        fin=None,
        ax=None,
        **kwargs,
    ):
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

            mpl_table = ax.table(
                cellText=cell_text, bbox=bbox, colLabels=data.columns, colWidths=col_widths, cellLoc='center', **kwargs
            )

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
                    cell.set_text_props(fontsize=font_size)
                    cell.set_facecolor(row_colors[k[0] % len(row_colors)])
                    cell.get_text().set_color('white')
                    if all(
                        mpl_table._cells.get((k[0], j), None) is None or mpl_table._cells[(k[0], j)]._text.get_text() == ''
                        for j in range(2, 3)
                    ):
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

            ax.text(
                0.5,
                y_height,
                alias,
                fontsize=fontsize,
                fontweight='bold',
                color='white',
                ha=title_loc,
                va='top',
                transform=ax.transAxes,
                bbox=dict(facecolor='none', edgecolor='none'),
                clip_on=False,
            )

            sample_of_img_title_view = 'SberCIB Investment Research. Данные на {}*'
            sample_of_img_title_view = sample_of_img_title_view.format(read_curdatetime().split()[0])
            title_loc = 'left'
            ax.text(
                -0.1,
                -0.245,
                sample_of_img_title_view,
                fontsize=10,
                fontweight='bold',
                color='white',
                ha=title_loc,
                va='top',
                transform=ax.transAxes,
                bbox=dict(facecolor='none', edgecolor='none'),
                clip_on=False,
            )
        else:
            if ax is None:
                size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
                fig, ax = plt.subplots(figsize=size)
                fig.facecolor = 'black'
                ax.axis('off')

            mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, cellLoc='center', **kwargs)
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
        png_path = config.PATH_TO_SOURCES / 'img' / f'{name}_table.png'
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


class Newsletter:
    """Создает текста для рассылок"""

    __newsletter_dict = dict(weekly_result='Основные события прошедшей недели', weekly_event='Календарь и прогнозы текущей недели')

    @classmethod
    def get_newsletter_dict(cls) -> dict[str, str]:
        return cls.__newsletter_dict

    @classmethod
    def make_weekly_result(cls) -> tuple[str, str, list[Path]]:
        """Создает текст для рассылки "Итоги недели" """
        title = 'Итоги недели'
        weekly_dir = config.PATH_TO_SOURCES / 'weeklies'
        slides_fnames = wp_parse.ParsePresentationPDF.get_fnames_by_type(wp_parse.ReportTypes.weekly_results)
        img_path_list = [weekly_dir / i for i in slides_fnames]
        newsletter = f'<b>{title}</b>\n'
        return title, newsletter, img_path_list

    @classmethod
    def make_weekly_event(cls) -> tuple[str, str, list[Path]]:
        """Создает текст для рассылки "Что нас ждет на этой неделе?" """
        title = 'Что нас ждет на этой неделе?'
        weekly_dir = config.PATH_TO_SOURCES / 'weeklies'
        slides_fnames = wp_parse.ParsePresentationPDF.get_fnames_by_type(wp_parse.ReportTypes.weekly_event)
        img_path_list = [weekly_dir / i for i in slides_fnames]
        newsletter = f'<b>{title}</b>\n'
        return title, newsletter, img_path_list
