import pandas as pd
from pandas.errors import EmptyDataError

class PandasDataTable():
    def __init__(self, path):
        self.set_dataframe(path)

    @property
    def columns(self):
        return self.__dataframe.columns

    #Methods
    def at(self, row, col):
        return self.__dataframe.at[row,col]
    
    def check_column_exist(self, column_name:str) -> bool:
        '''
            returns true if column_name exist in the dataframe's column else false
        '''
        return column_name.lower() in self.columns

    def filter_isin(self, column, condition, drop_option=True):
        df = self.__dataframe
        self.__dataframe = df[df[column].isin([condition])]
        self.__dataframe.reset_index(drop=drop_option, inplace=True)

    def get_columns(self):
        return self.__dataframe.columns
    
    def is_empty(self, value):
        return pd.isna(value)

    def iterate_rows(self):
        for row in self.__dataframe.iterrows():
            yield row
    
    def print(self):
        '''
        only allowed in development
        '''
        print(self.__dataframe)

    def set_dataframe(self, path):
        '''
        creates a dataframe that has the columns set to str, and lowercased
        '''
        try:
            self.__dataframe = pd.read_csv(path, dtype=str)
            self.__dataframe.columns = self.columns.str.lower()
        except EmptyDataError:
            raise EmptyDataError('The file is empty.')
        except FileNotFoundError:
            raise Exception('The file does not exist.')