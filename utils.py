#dependency modules
import pandas as pd
from photoshop import api as ps

#built-in modules
import json
from pathlib import Path

#custom modules
from sizes import Size

class PhotoshopFiller:
    def __init__(self, photoshop_path:str, csv_path:str, json_path:str) -> None:
        self._init_photoshop(photoshop_path)
        self._init_sizes(json_path)
        self._init_dataframe(csv_path)

    def start(self):
        for row in range(len(self.df.index)):
            name = self.app.activeDocument.name
            self.app.activeDocument.duplicate(f"{name} - placeholder")

            doc_num = row + 1
            path = str(self._psd_path.parent) + f"\{doc_num}"


            for col in self.df.columns:
                self._fill_layers(col, self.df.loc[row, col])

            cur_row_size_name = self.df.loc[row, 'size']
            size_found = self._change_doc_size(cur_row_size_name)

            if size_found == False:
                print(f"#{doc_num} size not found")

            self.app.activeDocument.saveAs(path, self._jpg_savepref)
            self.app.activeDocument.close(ps.SaveOptions.DoNotSaveChanges)

    def _change_doc_size(self, size_name) -> bool:
        size_found = False
        for size in self.sizes:
            if size.name == size_name:
                self.app.activeDocument.resizeImage(size.width, size.height, self.app.activeDocument.resolution)
                size_found = True

        return size_found
            

    def _fill_layers(self, layerName: str, content: str):
        for layer in self.app.activeDocument.layers:
            if layer.name == layerName:
                layer.textItem.contents = content
        
    def ps_change_colormode(self, isRgb: bool):
        self.app.activeDocument.changeMode(ps.ChangeMode.ConvertToRGB if isRgb else ps.ChangeMode.ConvertToCMYK)

    def _init_photoshop(self, ps_path:str):
        self.app = ps.Application()
        self._psd_path = Path(ps_path)
        self._jpg_savepref = ps.JPEGSaveOptions(quality=12)
        self.app.preferences.rulerUnits = ps.Units.Inches
        self.app.open(ps_path)
    
    def _init_sizes(self, json_path: str):
        self.sizes = []

        with open(str(json_path)) as s:
            json_raw = json.load(s)

        for json_raw_sizes in json_raw['sizes']:
            self.sizes.append(Size(json_raw_sizes['name'], json_raw_sizes['width'], json_raw_sizes['height']))

    def _init_dataframe(self, csv_path):
        self.df = pd.read_csv(csv_path, dtype={'number':str})

    def print_sizes(self):
        for size in self.sizes:
            print(f"{size.width} {size.height} {size.name}")

    def print_df(self):
        print(self.df)
        
        

psFiller = PhotoshopFiller(photoshop_path=r"C:\Users\johna\Desktop\Photoshop scripting test\Test1\practice2.psd", 
                       csv_path=r"C:\Users\johna\Desktop\Photoshop scripting test\Test1\customer info.csv",
                       json_path=r"C:\Users\johna\Desktop\Photoshamatic\Sizes\upper_jersey.json")

psFiller.start()


