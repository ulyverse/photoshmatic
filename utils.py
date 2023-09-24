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

class PhotoshopFiller:
    def start(self, callback = None, convertCMYK = False):
        log = ""
        num_rows = len(self.df.index)
        self._open_photoshop_file()
        psd_name = self._app.activeDocument.name
        self._app.activeDocument.duplicate(f"{psd_name} - placeholder")
        for row in range(num_rows):
            savedState = self._app.activeDocument.activeHistoryState

            col_num = row + 1

            file_info = []
            for ecol in self._get_existing_essentialcol():
                ecol_value = self.df.loc[row,ecol]
                if Helper.is_not_na(ecol_value):
                    file_info.append(ecol_value)

            file_format = '_'.join(file_info)

            path = str(self._psd_path.parent) + f"\{col_num}"
            if file_format != "":
                path += f"- {file_format}"

            for col in self.df.columns:
                cur_cell_value = self.df.loc[row, col]
                cur_cell_text = Helper.text_transform(cur_cell_value if Helper.is_not_na(cur_cell_value) else "", self.text_settings)
                self._fill_layers(col, cur_cell_text)

            cur_size = self.df.loc[row,'size']

            if 'size' in self._get_existing_essentialcol() and Helper.is_not_na(cur_size):
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

    def _fill_layers(self, layerName: str, content: str):
        for layer in self._app.activeDocument.layers:
            layer_name = layer.name.split()
            if layer_name[0] == layerName:
                self._app.activeDocument.activeLayer = layer
                layer.textItem.contents = content

                if len(layer_name) > 1:
                    parameter = layer_name[1]
                    max = Helper.try_parse(parameter) if parameter[0].isdigit() else Helper.try_parse(parameter[2:])
                    if max == None:
                        return f"Parameter invalid in {layer.name}"
                    else:
                        self.exceed_length_param(max, parameter[:1])

                    # activate_layer = self._app.activeDocument.activeLayer
                    # width = activate_layer.bounds[2] - activate_layer.bounds[0]
                    # if width > max:
                    #     r = max / width * 100
                    #     activate_layer.resize(r, r, ps.AnchorPosition.MiddleCenter)

    def exceed_length_param(self, max, param:str):
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
            activate_layer.resize(r, r, ps.AnchorPosition.MiddleCenter if is_height == False else ps.AnchorPosition.TopCenter)

    def __init__(self) -> None:
        self.text_settings = 0

    def init_photoshop(self, file_path:str):
        self._psd_path = Path(file_path)
        
    def _open_photoshop_file(self):
        self._app = ps.Application()
        self._app.preferences.rulerUnits = ps.Units.Inches
        self._jpg_savepref = ps.JPEGSaveOptions(quality=12)
        self._app.open(str(self._psd_path.absolute()))
    
    def init_sizes(self, file_path: str):
        self.sizes = []

        with open(str(file_path)) as s:
            json_raw = json.load(s)

        for json_raw_sizes in json_raw['sizes']:
            self.sizes.append(Size(json_raw_sizes['name'], json_raw_sizes['width'], json_raw_sizes['height'], json_raw_sizes['shortsize']))

    def init_dataframe(self, file_path):
        self.df = pd.read_csv(file_path, dtype={'number':str})

    def _get_existing_essentialcol(self):
        required_col = ['name','size','number']
        existing_col = []
        for rcol in required_col:
            if rcol in self.df.columns:
                existing_col.append(rcol)
        return existing_col

    def print_sizes(self):
        for size in self.sizes:
            print(f"{size.width} {size.height} {size.name}")

    def print_df(self):
        print(self.df)
        

class Helper:
    def try_parse(digit:str):
        return float(digit) if digit.isdigit() else None

    def is_not_na(scalar):
        return pd.isna(scalar) == False

    def get_textsettings():
        txtset = list()
        for text_setting in TextSettings:
            txtset.append(text_setting.value)

        return txtset

    def get_uniq_identifier():
        return hashlib.md5(Helper.get_mad().encode("utf-8")).hexdigest()
    
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

    def __init__(self) -> None:
        pass


class TextSettings(Enum):
    DEFAULT = "default"
    UPPERCASE = "uppercase"
    LOWERCASE = "lowercase"
    CAPITALIZE = "capitalize"

class Parameter(Enum):
    WIDTH = "w"
    HEIGHT = "h"


