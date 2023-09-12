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
        #init photoshop
        self.app = ps.Application()
        self.ps_path = Path(photoshop_path)
        self.jpg_savepref = ps.JPEGSaveOptions(quality=12)
        self.app.preferences.rulerUnits = ps.Units.Inches
        self.app.open(photoshop_path)

        #init tshirt sizes
        self.init_sizes(json_path)
        
        #init data frame
        self.df = pd.read_csv(str(csv_path), dtype={'number':str})

    def fill_layers(self, layerName: str, content: str):
        for layer in self.app.activeDocument.layers:
            if layer.name == layerName:
                layer.textItem.contents = content
        
    def ps_change_colormode(self, isRgb: bool):
        self.app.activeDocument.changeMode(ps.ChangeMode.ConvertToRGB if isRgb else ps.ChangeMode.ConvertToCMYK)
    
    def init_sizes(self, json_path: str):
        self.sizes = []

        with open(str(json_path)) as s:
            json_raw = json.load(s)

        for json_raw_sizes in json_raw['sizes']:
            self.sizes.append(Size(json_raw_sizes['name'], json_raw_sizes['width'], json_raw_sizes['height']))

    def print_sizes(self):
        for size in self.sizes:
            print(f"{size.width} {size.height} {size.name}")

    def print_df(self):
        print(self.df)
        
        

psFiller = PhotoshopFiller(photoshop_path=r"C:\Users\johna\Desktop\Photoshop scripting test\Test 2\practice.psd", 
                       csv_path=r"C:\Users\johna\Desktop\Photoshop scripting test\Test1\customer info.csv",
                       json_path=r"C:\Users\johna\Desktop\Photoshamatic\Sizes\upper_jersey.json")

psFiller.fill_layers("test", "SOMETHING")


