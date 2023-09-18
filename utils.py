#dependency modules
import pandas as pd
from photoshop import api as ps

#built-in modules
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
        psd_name = self._app.activeDocument.name
        self._app.activeDocument.duplicate(f"{psd_name} - placeholder")
        for row in range(num_rows):
            savedState = self._app.activeDocument.activeHistoryState

            col_num = row + 1
            cur_name = self.df.loc[row, 'name']
            cur_size = self.df.loc[row, 'size']
            cur_number = self.df.loc[row, 'number']

            path = str(self._psd_path.parent) + f"\{col_num} - {cur_name}_{cur_size}_{cur_number}"

            for col in self.df.columns:
                cur_cell_text = Helper.text_transform(self.df.loc[row, col], self.text_settings)
                self._fill_layers(col, cur_cell_text)

            size_found = self._change_doc_size(cur_size)

            if size_found == False:
                log += f"{col_num} - {cur_name} size incorrect/not found\n"

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
        for size in self.sizes:
            if size.name == size_name:
                self._app.activeDocument.resizeImage(size.width, size.height, self._app.activeDocument.resolution)
                size_found = True

        return size_found

    def _fill_layers(self, layerName: str, content: str):
        for layer in self._app.activeDocument.layers:
            if layer.name == layerName:
                layer.textItem.contents = content

    def __init__(self) -> None:
        self.text_settings = 0

    def init_photoshop(self, file_path:str):
        self._app = ps.Application()
        self._psd_path = Path(file_path)
        self._jpg_savepref = ps.JPEGSaveOptions(quality=12)
        self._app.preferences.rulerUnits = ps.Units.Inches
        self._app.open(file_path)
    
    def init_sizes(self, file_path: str):
        self.sizes = []

        with open(str(file_path)) as s:
            json_raw = json.load(s)

        for json_raw_sizes in json_raw['sizes']:
            self.sizes.append(Size(json_raw_sizes['name'], json_raw_sizes['width'], json_raw_sizes['height']))

    def init_dataframe(self, file_path):
        self.df = pd.read_csv(file_path, dtype={'number':str})

    def print_sizes(self):
        for size in self.sizes:
            print(f"{size.width} {size.height} {size.name}")

    def print_df(self):
        print(self.df)
        
        

class Helper:

    def get_textsettings():
        txtset = list()
        for text_setting in TextSettings:
            txtset.append(text_setting.value)

        return txtset

    def get_uniq_identifier():
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


