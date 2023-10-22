#dependency modules
import pandas as pd
from photoshop import api as ps

#built-in modules
import hashlib
import uuid
from pathlib import Path

#custom modules
from configuration import Config
from enumeration import Parameter
from enumeration import TextSettings
from enumeration import UnitPreference
from sizes import ClothSizes


def __dir__():
    return " "

class PhotomaticPro:
    def __dir__(self):
        return " "

    def start(self, callback = None, convertCMYK = False):
        log = ""
        debug_row, debug_col = None, None
        try:
            self._open_csv()
            self._open_photoshop_file()
            num_rows = len(self.df.index)

            folder_path = self._create_folderpath()
            self._create_outputfolder(folder_path)
            
            error = self._check_parameter_error()
            if error != None: log += f"Parameter invalid in these layers: {error}\n"

            self._create_placeholder()

            for row in range(num_rows):
                debug_row = row
                savedState = self._app.activeDocument.activeHistoryState
                row_num = row + 1

                #get cell values and fill layers
                for col in self.df.columns:
                    debug_col = col
                    cur_cell_value = self.df.loc[row, col]
                    cur_cell_text = Helper.text_transform(cur_cell_value if Helper.is_not_empty(cur_cell_value) else "", self.text_settings)
                    self._fill_layers(col, cur_cell_text)

                #change sizes
                if Config.get_sc_resize_image() == True and 'size' in self._get_existing_filenamecol():
                    cur_size = self.df.loc[row,'size']
                    if Helper.is_not_empty(cur_size):
                        short = self.clothing.get_shortsize(cur_size)
                        if short != None:
                            self._fill_layers("shortsize", short)

                    size_found = self._change_doc_size(cur_size)

                    if size_found == False:
                        log += f"picture #{row_num} size not found\n"

                #create file
                file_format = self._create_fileformat(row)
                path = self._create_filepath(folder_path, row_num, file_format)
                self._app.activeDocument.saveAs(path, self._jpg_savepref)

                self._app.activeDocument.activeHistoryState = savedState

                if convertCMYK:
                    self._convert_to_cmyk(path)

                #pass the variables to callback not make the calculations inside the start() 
                #start() shouldn't be concerned with any progress.
                progress = row_num/num_rows*100
                if callback != None:
                    callback(progress)

            self._app.activeDocument.close(ps.SaveOptions.DoNotSaveChanges)
        except Exception as e:
            log += repr(e)
            if debug_row is not None and debug_col is not None:
                log += f"\nstopped at column: [{debug_col}] row: [{debug_row}], cell: [{self.df.loc[debug_row, debug_col]}]"
        return log
    
    def _create_folderpath(self) -> str:
        psd_name = self._app.activeDocument.name
        folder_path = fr"{str(self._psd_path.parent)}\{psd_name[:-4]}"

        if Config.get_sc_resize_image() == True:
            folder_path += f" - {self.clothing_name}"

        return folder_path
    
    def _create_outputfolder(self, folder_path):
        Path(folder_path).mkdir(exist_ok=True)

    def _create_placeholder(self):
        psd_name = self._app.activeDocument.name
        self._app.activeDocument.duplicate(f"{psd_name} - placeholder")

    def _convert_to_cmyk(self, path):
        file_type = ".jpg"
        self._app.open(path+file_type)
        self._app.activeDocument.changeMode(ps.ChangeMode.ConvertToCMYK)
        self._app.activeDocument.close(ps.SaveOptions.SaveChanges)

    def _change_doc_size(self, size_name) -> bool:
        size_found = False
        size = self.clothing.get_size(size_name)
        if(size != None):
            self._app.activeDocument.resizeImage(size.width, size.height, self._app.activeDocument.resolution)
            size_found = True
        return size_found
    
    def _check_parameter_error(self):
        error = set()
        for layer in self._app.activeDocument.layers:
            layer_name = layer.name.split()
            if len(layer_name) > 1:
                is_param_error = True if self._get_param_digit(layer_name[1]) == None else False
                if is_param_error and layer.name not in error:
                    error.add(layer.name)
        if len(error) > 0:
            return error
                    
    def _get_param_digit(self, val):
        return Helper.try_parse(val) if val[0].isdigit() else Helper.try_parse(val[2:])

    def _fill_layers(self, layerName: str, content: str):
        for layer in self._app.activeDocument.layers:
            layer_name = layer.name.split()
            if len(layer_name) > 0 and layer_name[0] == layerName:
                self._app.activeDocument.activeLayer = layer
                layer.textItem.contents = content

                if len(layer_name) > 1:
                    parameter = layer_name[1]
                    max = self._get_param_digit(parameter)
                    if max != None:
                        self._exceed_length_param(max, parameter[:1])
                        
    def _exceed_length_param(self, max, param:str):
        activate_layer = self._app.activeDocument.activeLayer
        first = 2
        second = 0
        add = 0
        is_height = True if param.lower() == Parameter.HEIGHT.value else False
        if is_height:
            add = 1
        length = activate_layer.bounds[first + add] - activate_layer.bounds[second + add]
        if length > max:
            r = max / length * 100
            if is_height:
                activate_layer.resize(100, r, ps.AnchorPosition.MiddleCenter if is_height == False else ps.AnchorPosition.TopCenter)
            else:
                activate_layer.resize(r, 100, ps.AnchorPosition.MiddleCenter if is_height == False else ps.AnchorPosition.TopCenter)

    def __init__(self) -> None:
        self.text_settings = 0

    def set_photoshop_path(self, file_path:str):
        self._psd_path = Path(file_path)
        
    def _open_photoshop_file(self):
        self._app = ps.Application(version=self._get_ps_version())
        self._app.preferences.rulerUnits = self._get_ruler_unit()
        self._jpg_savepref = ps.JPEGSaveOptions(quality=self._get_jpg_quality())
        self._app.open(str(self._psd_path.absolute()))

    def _get_ruler_unit(self):
        rulerunit_pref = Config.get_rulerunit_preference()
        rulerunit = ps.Units.Inches
        if rulerunit_pref == UnitPreference.CENTIMETERS.value:
            rulerunit = ps.Units.CM
        elif rulerunit_pref == UnitPreference.PIXELS.value:
            rulerunit = ps.Units.Pixels
        
        return rulerunit            

    def _get_jpg_quality(self):
        return Config.get_jpg_quality()
    
    def _get_ps_version(self):
        return Config.get_ps_version()
    
    def _get_character_encoding(self):
        return Config.get_character_encoding()
    
    def init_sizes(self, file_path: str):
        if Config.get_sc_resize_image() == False:
            return

        self.clothing_name = file_path[6:-5]
        self.clothing = ClothSizes(ClothSizes.read_clothing(file_path))

    def set_csv_path(self, file_path):
        self._csv_path = file_path
        
    def _open_csv(self):
        columns = Helper.get_columns(self._csv_path)
        num_idx = Helper.find_number_column(columns)
        self.df = pd.read_csv(self._csv_path, encoding=self._get_character_encoding(), dtype={num_idx:str})
        if Config.get_sc_resize_image() == False:
            self.df = Helper.reduce_df(self.df, Path(self._psd_path).name)

    def _create_fileformat(self, row):
        file_info = []
        for ecol in self._get_existing_filenamecol():
            ecol_value = self.df.loc[row,ecol]
            if Helper.is_not_empty(ecol_value):
                file_info.append(ecol_value)

        file_name = '_'.join(file_info)
        return file_name
    
    def _create_filepath(self, folder_path, row_num, file_row_names):
        #create create file path
        path = fr"{folder_path}\{row_num}"
        if file_row_names != "":
            path += f"- {file_row_names}"
        
        return path

    def _get_existing_filenamecol(self):
        #THIS CAN BE CACHED?
        required_col = ['name','size',Config.get_np_number_preference()]
        existing_col = []
        for rcol in required_col:
            for ecol in self.df.columns:
                if rcol in ecol.lower():
                    existing_col.append(ecol)
        return existing_col

    def print_sizes(self):
        self.clothing.print()

    def print_df(self):
        self._open_csv()
        print(self.df)
            

class Helper:
    def __dir__():
        return " "
    #SPREADSHEET
    def find_number_column(columns:list[str]) -> int:
        for x,column in enumerate(columns):
            if column.lower() == Config.get_np_number_preference():
                return x
        return -1
    #SPREADSHEET
    def get_columns(file_path:str) -> list[str]:
        with open(file_path, "r") as file:
            return file.readline().strip("\n").split(",")
    #HELPER
    def try_parse(digit:str) -> float | None:
        try:
            num = float(digit)
            return num
        except:
            return None
    #SPREADSHEET
    def is_not_empty(scalar) -> bool:
        return pd.isna(scalar) == False
    #PHOTOMATIC?
    def get_textsettings():
        txtset = list()
        for text_setting in TextSettings:
            txtset.append(text_setting.value)

        return txtset
    #HELPER
    def get_uniq_identifier():
        return hashlib.md5((Helper.get_mad()+"hehexd").encode("utf-8")).hexdigest()
    #HELPER
    def get_mad():
        return ':'.join(("%012X" % uuid.getnode())[i:i+2] for i in range(0, 12, 2))
    #HELPER?
    def text_transform(text:str, text_settings:str) -> str:
        if text_settings == TextSettings.DEFAULT.value:
            return text
        elif text_settings == TextSettings.UPPERCASE.value:
            return text.upper()
        elif text_settings == TextSettings.LOWERCASE.value:
            return text.lower()
        elif text_settings == TextSettings.CAPITALIZE.value:
            return text.capitalize()
        
        return text
    #HELPER
    @classmethod
    def get_size_in_file(cls, file_name:str) -> str | list | None:
        '''
            param:
            file_name:str - must include .psd the function strips it, ex: "2XL - Lower 2022 V2.psd"

            note:
            before returning the value it removes '-' and '_' to reduce uncertainty significantly

            returns:
            the found value of config_sc_sizes either "XL" or ['S','SMALL']
        '''
        file_name_arr = file_name[:-4].replace("-"," ").replace("_"," ").split()
        for file in file_name_arr:
            for size in Config.get_sc_sizes():
                if type(size) == list:
                    for s in size:
                        if cls.compare_insensitive(s,file):
                            return size
                else:
                    if cls.compare_insensitive(size,file):
                        return size
        return None

    #HELPER
    def compare_insensitive(str1:str, str2:str) -> bool:
        '''
            compare both strings case insensitivity

            returns True if strings are the same otherwise False
        '''
        return  str1.casefold() == str2.casefold()
    #SS
    def df_isin(df:pd.DataFrame, column:str, condition) -> pd.DataFrame:
        '''
            param:
            df: pandas.DataFrame
            column: str
            condition: list[str]

            note:
            it also resets the index of the dataframe

            returns:
            returns a new DataFrame of the rows based on the condition

            exception:
            throws an error if it cannot find the size column
        '''
        try:
            df = df[df[column].isin(condition)]
            df.reset_index(drop=True,inplace=True)
            return df
        except KeyError:
            raise Exception("'size' column not found in the csv")
    #HELPER?
    def get_size_condition(size_name) -> list[str]:
        '''
            param:
            size_name:str, ex: XL,M,2XS

            returns:
            an array of both the original str, upper and lower of the size_name or an empty list
        '''
        if size_name == None:
            return []

        if type(size_name) == list:
            condition = []
            for size in size_name:
                condition.append(size.lower())
                condition.append(size.upper())
                if len(size) > 3:
                    condition.append(size.capitalize())
            return condition
        
        return [size_name, size_name.lower(), size_name.upper(), size_name.capitalize()]
    #SS
    def find_size_column(columns) -> str:
        '''
            finds the 'size' column case insensitive

            returns:
            the size or an empty string
        '''
        for column in columns:
            if column.lower() == "size":
                return column
        return ""
    #SS
    @classmethod
    def reduce_df(cls, df:pd.DataFrame, psd_name:str) -> pd.DataFrame:
        '''
            gets the size in psd and returns an reduced dataframe or empty row'd dataframe
        '''
        size_name_file = cls.get_size_in_file(psd_name)
        condition = cls.get_size_condition(size_name_file)
        size_name = cls.find_size_column(df.columns)
        return cls.df_isin(df,size_name,condition)