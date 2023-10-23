#dependency modules
import pandas as pd
from photoshop import api as ps

#built-in modules
import hashlib
import uuid
from pathlib import Path

#custom modules
from configuration import Config
from data import PandasDataTable
from enumeration import Parameter
from enumeration import TextSettings
from enumeration import UnitPreference
from sizes import ClothSizes


def __dir__():
    return " "

class PhotomaticPro:
    def __dir__(self):
        return " "
    
    def __init__(self) -> None:
        self._data = None
        self._clothing = None
        self._app = None

    def start(
            self, 
            datatable_path:str, 
            document_path:str, 
            clothing_path:str, 
            convert_cmyk = False, 
            text_settings = TextSettings.DEFAULT,
            progress_callback = False
            ):
        log = ""

        self._open_datatable(datatable_path)
        self._transform_datatable(text_settings)
        self.open_photoshop_file()

        folder_path = self._create_folderpath()
        self._create_outputfolder(folder_path)
        
        error = self._check_parameter_error()
        if error != None: log += f"Parameter invalid in these layers: {error}\n"

        self._create_placeholder()

        for row in self._data.iterate_rows():
            #save state
            savedState = self._app.activeDocument.activeHistoryState

            row_idx = row[0]
            #row_num should be based on either row_idx + 1 or if Index column exist get that current existing Index.
            row_num = (row_idx + 1)

            for col, cell in row[1].items():
                self._fill_layers(col, cell)

            if Config.get_sc_resize_image() == True and self._data.does_column_exist('size'):
                size = self._data.at(row_idx, 'size')
                if not self._data.is_empty(size):
                    shortsize = self._clothing.get_shortsize(size)
                    if shortsize != None:
                        self._fill_layers("shortsize", shortsize)

                size_found = self._change_doc_size(size)
                if size_found == False:
                    log += f"picture #{row_num} size not found\n"

            #create file
            file_format = self._create_fileformat(row_idx)
            path = self._create_filepath(folder_path, row_num, file_format)
            self._app.activeDocument.saveAs(path, self._jpg_savepref)

            #restore saved state
            self._app.activeDocument.activeHistoryState = savedState

            if convert_cmyk: self._convert_to_cmyk(path)

        self._app.activeDocument.close(ps.SaveOptions.DoNotSaveChanges)
        return log
    
    def _transform_datatable(self, text_setting = TextSettings.DEFAULT):
        if text_setting == TextSettings.DEFAULT:
            return
        elif text_setting == TextSettings.UPPERCASE:
            self._data.transform(lambda s: s.upper() if type(s) == str else s)
        elif text_setting == TextSettings.LOWERCASE:
            self._data.transform(lambda s: s.lower() if type(s) == str else s)
        elif text_setting == TextSettings.CAPITALIZE:
            self._data.transform(lambda s: s.capitalize() if type(s) == str else s)
    
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
        size = self._clothing.get_size(size_name)
        if(size != None):
            self._app.activeDocument.resizeImage(size.width, size.height, self._app.activeDocument.resolution)
            size_found = True
        return size_found
    
    def _check_parameter_error(self):
        error = set()
        for layer in self._app.activeDocument.layers:
            layer_name = layer.name.split()
            if len(layer_name) > 1:
                is_param_error = True if self._get_parameter_digit(layer_name[1]) == None else False
                if is_param_error and layer.name not in error:
                    error.add(layer.name)
        if len(error) > 0:
            return error
                    
    def _get_parameter_digit(self, val):
        return Helper.try_parse(val) if val[0].isdigit() else Helper.try_parse(val[2:])

    def _fill_layers(self, layer_name: str, content: str):
        for layer in self._app.activeDocument.layers:
            layer_name = layer.name.split()
            if len(layer_name) > 0 and layer_name[0] == layer_name:
                self._app.activeDocument.activeLayer = layer
                layer.textItem.contents = content

                if len(layer_name) > 1:
                    parameter = layer_name[1]
                    max = self._get_parameter_digit(parameter)
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

    def set_photoshop_path(self, file_path:str):
        self._psd_path = Path(file_path)
        
    def open_photoshop_file(self):
        self._app = ps.Application(version=Config.get_ps_version())
        self._app.preferences.rulerUnits = self._get_ruler_unit()
        self._jpg_savepref = ps.JPEGSaveOptions(quality=Config.get_jpg_quality())
        self._app.open(str(self._psd_path.absolute()))

    def _get_ruler_unit(self):
        rulerunit_pref = Config.get_rulerunit_preference()
        rulerunit = ps.Units.Inches
        if rulerunit_pref == UnitPreference.CENTIMETERS.value:
            rulerunit = ps.Units.CM
        elif rulerunit_pref == UnitPreference.PIXELS.value:
            rulerunit = ps.Units.Pixels
        
        return rulerunit

    def _open_sizes(self, file_path: str):
        if Config.get_sc_resize_image() == False:
            return

        self.clothing_name = file_path[6:-5]
        self._clothing = ClothSizes(ClothSizes.read_clothing(file_path))
        
    def _open_datatable(self, datatable_path):
        self._data = PandasDataTable(datatable_path, encoding=Config.get_character_encoding())
        if Config.get_sc_resize_image() == False:
            condition = Helper.get_size_condition(self._app.activeDocument.name)#side effect if activedocument isn't the right one
            self._data.filter_isin('size',condition)

    def _create_fileformat(self, row):
        file_info = []
        for ecol in self._get_existing_filenamecol():
            ecol_value = self._data.at(row,ecol)
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
            for ecol in self._data.columns:
                if rcol in ecol.lower():
                    existing_col.append(ecol)
        return existing_col

    def print_sizes(self):
        self._clothing.print()

    def print_df(self):
        self._data.print()


class Helper:
    def __dir__():
        return " "

    #PURE HELPER
    def try_parse(digit:str) -> float | None:
        try:
            num = float(digit)
            return num
        except:
            return None
        
    #PURE HELPER
    @classmethod
    def compare_insensitive(cls, str1:str, str2:str) -> bool:
        '''
            compare both strings case insensitivity

            returns True if strings are the same otherwise False
        '''
        return  str1.lower() == str2.lower()

    #GUI CMB PHOTOMATIC
    def get_textsettings():
        txtset = list()
        for text_setting in TextSettings:
            txtset.append(text_setting.value)
        return txtset

    #SETUP HELPER
    def get_uniq_identifier():
        return hashlib.md5((Helper.get_mad()+"hehexd").encode("utf-8")).hexdigest()
    
    #SETUP HELPER
    def get_mad():
        return ':'.join(("%012X" % uuid.getnode())[i:i+2] for i in range(0, 12, 2))

    #PHOTOMATIC HELPER
    @classmethod
    def extract_size_in_file(cls, document_name:str) -> str | list | None:
        '''
            param:
            file_name:str - must include .psd the function strips it, ex: "2XL - Lower 2022 V2.psd"

            note:
            before returning the value it removes '-' and '_' to reduce uncertainty significantly

            returns:
            the found value of config_sc_sizes either "XL" or ['S','SMALL']
        '''
        file_name_arr = document_name[:-4].replace("-"," ").replace("_"," ").split()
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
    
    #PHOTOMATIC HELPER
    @classmethod
    def get_size_condition(cls, document) -> list[str]:
        '''
            param:
            document: document_name

            extracts the 'size' in the document_name and (see return)

            returns:
            an array of both the original str, upper and lower of the size_name or an empty list
        '''
        size_name = cls.extract_size_in_file(document)
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