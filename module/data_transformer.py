from pandas.plotting import table
import matplotlib.pyplot as plt
import pandas as pd


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
    def get_table_from_html(euro_standart: bool, html: str) -> list[pd.DataFrame]:
        """
        Take all tables from html code
        :param euro_standart: Bool value for separators of decimals and thousands
        :param html: HTML codes as text
        :return: list with DataFrames
        """
        if euro_standart:
            return pd.read_html(html)
        return pd.read_html(html, decimal=',', thousands='.')

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
