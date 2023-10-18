#dependency modules
import pandas as pd
from photoshop import api as ps

#built-in modules
import hashlib
import json
import uuid
from enum import Enum
from pathlib import Path

#custom modules
from sizes import Size


def __dir__():
    return " "

class PhotoshopFiller:
    def __dir__(self):
        return " "

    def start(self, callback = None, convertCMYK = False):
        log = ""
        debug_cur_row_num = -1
        debug_cur_col_num = -1
        try:
            num_rows = len(self.df.index)
            self._open_photoshop_file()
            psd_name = self._app.activeDocument.name
            folder_path = fr"{str(self._psd_path.parent)}\{psd_name[:-4]} - {self.size_file_name}"
            Path(folder_path).mkdir(exist_ok=True)
            error = self._check_param_error()
            if error != None: log += f"Parameter invalid in these layers: {error}\n"
            self._app.activeDocument.duplicate(f"{psd_name} - placeholder")
            for row in range(num_rows):
                debug_cur_row_num = row
                savedState = self._app.activeDocument.activeHistoryState

                col_num = row + 1

                #format file name
                file_info = []
                for ecol in self._get_existing_essentialcol():
                    ecol_value = self.df.loc[row,ecol]
                    if Helper.is_cell_not_empty(ecol_value):
                        file_info.append(ecol_value)

                file_format = '_'.join(file_info)

                #create path
                path = fr"{folder_path}\{col_num}"
                if file_format != "":
                    path += f"- {file_format}"

                #fill layers
                for col in self.df.columns:
                    debug_cur_col_num = col
                    cur_cell_value = self.df.loc[row, col]
                    cur_cell_text = Helper.text_transform(cur_cell_value if Helper.is_cell_not_empty(cur_cell_value) else "", self.text_settings)
                    self._fill_layers(col, cur_cell_text)

                #change sizes
                if 'size' in self._get_existing_essentialcol():
                    cur_size = self.df.loc[row,'size']
                    if Helper.is_cell_not_empty(cur_size):
                        short = self._get_shortsize(cur_size)
                        if short != None:
                            self._fill_layers("shortsize", short)

                    size_found = self._change_doc_size(cur_size)

                    if size_found == False:
                        log += f"picture #{col_num} size not found\n"

                self._app.activeDocument.saveAs(path, self._jpg_savepref)
                self._app.activeDocument.activeHistoryState = savedState

                if convertCMYK:
                    self._convert_to_cmyk(path)

                progress = col_num/num_rows*100
                if callback != None:
                    callback(progress)

            self._app.activeDocument.close(ps.SaveOptions.DoNotSaveChanges)
        except Exception as e:
            log += repr(e)
            if debug_cur_row_num != -1 and debug_cur_col_num != -1:
                log += f"\nstopped at column: [{debug_cur_col_num}] row: [{debug_cur_row_num}], cell value: [{self.df.loc[debug_cur_row_num, debug_cur_col_num]}]"
        return log

    def _convert_to_cmyk(self, path):
        file_type = ".jpg"
        self._app.open(path+file_type)
        self._app.activeDocument.changeMode(ps.ChangeMode.ConvertToCMYK)
        self._app.activeDocument.close(ps.SaveOptions.SaveChanges)

    def _change_doc_size(self, size_name) -> bool:
        size_found = False
        size = self._get_size(size_name)
        if(size != None):
            self._app.activeDocument.resizeImage(size.width, size.height, self._app.activeDocument.resolution)
            size_found = True

        return size_found
    
    def _get_shortsize(self, size_name):
        size = self._get_size(size_name)
        if(size != None):
            return size.short_size
    
    def _get_size(self, size_name):
        for size in self.sizes:
            if size.name == size_name:
                return size
        return None
    
    def _check_param_error(self):
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
            if layer_name[0] == layerName:
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

    def init_photoshop(self, file_path:str):
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
        self.size_file_name = file_path[6:-5]
        self.sizes = []
        try:
            with open(str(file_path)) as s:
                json_raw = json.load(s)
                
            for json_raw_sizes in json_raw['sizes']:
                self.sizes.append(Size(json_raw_sizes['name'], json_raw_sizes['width'], json_raw_sizes['height'], json_raw_sizes['shortsize']))
        except json.decoder.JSONDecodeError as e:
                raise Exception(repr(e))
        except FileNotFoundError:
            raise Exception(f"{file_path} is missing")

    def init_dataframe(self, file_path):
        columns = Helper.get_columns(file_path)
        num_idx = Helper.find_number_column(columns)
        self.df = pd.read_csv(file_path, encoding=self._get_character_encoding(), dtype={num_idx:str})

    def _get_existing_essentialcol(self):
        required_col = ['name','size',Config.get_np_number_preference()]
        existing_col = []
        for rcol in required_col:
            for ecol in self.df.columns:
                if rcol in ecol.lower():
                    existing_col.append(ecol)
        return existing_col

    def print_sizes(self):
        for size in self.sizes:
            print(f"{size.width} {size.height} {size.short_size} {size.name}")

    def print_df(self):
        print(self.df)
        

class Helper:
    def __dir__():
        return " "
    
    def find_number_column(columns:list[str]) -> int:
        for x,column in enumerate(columns):
            if column.lower() == Config.get_np_number_preference():
                return x
        return -1

    def get_columns(file_path:str) -> list[str]:
        with open(file_path, "r") as file:
            return file.readline().strip("\n").split(",")

    def try_parse(digit:str) -> float | None:
        try:
            num = float(digit)
            return num
        except:
            return None

    def is_cell_not_empty(scalar) -> bool:
        return pd.isna(scalar) == False

    def get_textsettings():
        txtset = list()
        for text_setting in TextSettings:
            txtset.append(text_setting.value)

        return txtset

    def get_uniq_identifier():
        return hashlib.md5((Helper.get_mad()+"hehexd").encode("utf-8")).hexdigest()
    
    def get_mad():
        return ':'.join(("%012X" % uuid.getnode())[i:i+2] for i in range(0, 12, 2))

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
    

class Config:
    data = None

    @classmethod
    def load_config(cls):
        if cls.data is None:
            try:
                with open("settings/settings.json", "r") as f:
                    cls.data = json.load(f)
            except json.decoder.JSONDecodeError as e:
                raise Exception(repr(e))
            except FileNotFoundError:
                raise Exception("settings/settings.json is missing")
            
    @classmethod
    def get_company_name(cls) -> str:
        if cls.data is None:
            cls.load_config()
        company_name =  Config.data["company_name"]
        return company_name if company_name != "" else "PHOTOMATIC"
    
    @classmethod
    def get_jpg_quality(cls):
        if cls.data is None:
            cls.load_config()
        data = cls.data["jpg_quality"]
        return data if type(data) == int and data > 0 else 12
    
    @classmethod
    def get_ps_version(cls):
        if cls.data is None:
            cls.load_config()
        return cls.data["ps_version"] if cls.data["ps_version"] != "" else None
    
    @classmethod    
    def get_character_encoding(cls):
        if cls.data is None:
            cls.load_config()
        return cls.data["char_encoding"] if cls.data["char_encoding"] != "" else "mbcs"
    
    @classmethod    
    def get_rulerunit_preference(cls):
        if cls.data is None:
            cls.load_config()
        return cls.data["rulerunit_preference"] if cls.data["rulerunit_preference"] != "" else "in"
    
    @classmethod    
    def get_np_number_preference(cls):
        if cls.data is None:
            cls.load_config()
        data = cls.data["naming_preference"]["number"] 
        return data if data != "" else "number"
    
    @classmethod    
    def get_sc_resize_image(cls):
        if cls.data is None:
            cls.load_config()
        data = cls.data["size_config"]["resize_image"]
        return data if data != None and type(data) == bool else True
    
    @classmethod    
    def get_sc_sizes(cls):
        if cls.data is None:
            cls.load_config()
        return cls.data["size_config"]["sizes"]
    

class TextSettings(Enum):
    DEFAULT = "default"
    UPPERCASE = "uppercase"
    LOWERCASE = "lowercase"
    CAPITALIZE = "capitalize"


class Parameter(Enum):
    WIDTH = "w"
    HEIGHT = "h"


class UnitPreference(Enum):
    INCHES = "in"
    CENTIMETERS = "cm"
    PIXELS = "px"