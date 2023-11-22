# dependency modules
import pandas as pd
from pandas.errors import EmptyDataError

# custom modules
from utils import Helper


def __dir__():
    return " "


class PandasDataTable:
    def __init__(self, path, encoding="mbcs"):
        self.set_dataframe(path, encoding)

    @property
    def columns(self):
        return self.__dataframe.columns

    # METHODS
    def apply(self, column, function):
        if not self.has_column(column):
            raise ValueError(f"{column} does not exist in the datatable")

        self.__dataframe = self.__dataframe[self.__dataframe[column].apply(function)]

    def at(self, row, col):
        return self.__dataframe.at[row, col]

    def change_size(self, column):
        if not self.has_column(column):
            raise ValueError(f"{column} does not exist in the datatable")

        delimeter = ":"

        condition = self.__dataframe[column].str.contains(delimeter)

        target_has_size = True in condition.values

        if target_has_size:
            self.__dataframe.loc[condition, "size"] = (
                self.__dataframe[column].str.split(delimeter).str.get(1).str.strip()
            )

    def has_column(self, column_name: str) -> bool:
        """
        returns true if column_name exist in the dataframe's column else false
        """
        return column_name.lower() in self.columns

    def drop(self, columns):
        self.__dataframe.drop(columns=columns, inplace=True, errors="ignore")

    def filter(self, column, where: str | list[str] | None, drop_option: bool = True):
        if not self.has_column(column):
            raise ValueError(f"{column} does not exist in the datatable")

        condition = Helper.get_condition(where)
        self.filter_isin(column, condition, drop_option)

    def filter_isin(self, column, condition: set[str], drop_option: bool = True):
        df = self.__dataframe
        self.__dataframe = df[df[column].isin(condition)]
        self.__dataframe.reset_index(drop=drop_option, inplace=True)

    def is_na(self, value):
        return value == ""

    def is_empty(self):
        return len(self.__dataframe.index) == 0

    def iterate_rows(self):
        for row in self.__dataframe.iterrows():
            yield row

    def print(self):
        """
        for development use only
        """
        print(self.__dataframe)

    def set_dataframe(self, path, encoding):
        """
        creates a dataframe that has the columns set to str and lowercased, and replaces the empty cell with ""
        """
        try:
            dataframe = None
            if path.endswith(".csv"):
                dataframe = pd.read_csv(path, encoding=encoding, dtype=str)
            elif path.endswith(".xlsx"):
                dataframe = pd.read_excel(path, dtype=str)
            else:
                raise Exception("Incorrect file type")
            self.__dataframe = dataframe
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
