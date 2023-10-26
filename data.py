# dependency modules
import pandas as pd
from pandas.errors import EmptyDataError


def __dir__():
    return " "


class PandasDataTable:
    def __init__(self, path, encoding):
        self.set_dataframe(path, encoding)

    @property
    def columns(self):
        return self.__dataframe.columns

    # Methods
    def at(self, row, col):
        return self.__dataframe.at[row, col]

    def does_column_exist(self, column_name: str) -> bool:
        """
        returns true if column_name exist in the dataframe's column else false
        """
        return column_name.lower() in self.columns

    def filter_isin(self, column, condition: set[str], drop_option: bool = False):
        df = self.__dataframe
        self.__dataframe = df[df[column].isin(condition)]
        self.__dataframe.reset_index(drop=drop_option, inplace=True)

    def get_column(self, column_name: str):
        """
        returns the lowercase of column_name or None if doesn't exist
        """
        return column_name.lower() if self.does_column_exist(column_name) else None

    def is_empty(self, value):
        return value == ""

    def iterate_rows(self):
        for row in self.__dataframe.iterrows():
            yield row

    def print(self):
        """
        only allowed in development
        """
        print(self.__dataframe)

    def set_dataframe(self, path, encoding):
        """
        creates a dataframe that has the columns set to str and lowercased, and replaces the empty cell with ""
        """
        try:
            self.__dataframe = pd.read_csv(path, encoding=encoding, dtype=str)
            self.__dataframe.columns = self.columns.str.lower()
            self.__dataframe.fillna("", inplace=True)
        except EmptyDataError:
            raise EmptyDataError("The file is empty.")
        except FileNotFoundError:
            raise Exception("The file does not exist.")
        except UnicodeDecodeError:
            raise Exception(
                "The character encoding of the data doesn't match the settings > character_encoding "
            )

    def transform(self, option):
        self.__dataframe = self.__dataframe.applymap(option)
