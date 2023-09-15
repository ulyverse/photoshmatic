#dependency modules
import pandas as pd
from photoshop import api as ps

#built-in modules
import json
from pathlib import Path
from tkinter import ttk

#custom modules
from sizes import Size

class PhotoshopFiller:
    def start(self, callback = None):
        log = ""
        num_rows = len(self.df.index)
        psd_name = self._app.activeDocument.name
        self._app.activeDocument.duplicate(f"{psd_name} - placeholder")
        for row in range(num_rows):
            savedState = self._app.activeDocument.activeHistoryState

            doc_num = row + 1
            path = str(self._psd_path.parent) + f"\{doc_num}"

            for col in self.df.columns:
                self._fill_layers(col, self.df.loc[row, col])

            cur_row_size_name = self.df.loc[row, 'size']
            size_found = self._change_doc_size(cur_row_size_name)

            if size_found == False:
                log += f"#{doc_num} size incorrect/not found\n"

            self._app.activeDocument.saveAs(path, self._jpg_savepref)
            self._app.activeDocument.activeHistoryState = savedState

            progress = doc_num/num_rows*100
            if callback != None:
                callback(progress)

        self._app.activeDocument.close(ps.SaveOptions.DoNotSaveChanges)
        return log

    def print_sizes(self):
        for size in self.sizes:
            print(f"{size.width} {size.height} {size.name}")

    def print_df(self):
        print(self.df)

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

    def init_photoshop(self, ps_path:str):
        self._app = ps.Application()
        self._psd_path = Path(ps_path)
        self._jpg_savepref = ps.JPEGSaveOptions(quality=12)
        self._app.preferences.rulerUnits = ps.Units.Inches
        self._app.open(ps_path)
    
    def init_sizes(self, json_path: str):
        self.sizes = []

        with open(str(json_path)) as s:
            json_raw = json.load(s)

        for json_raw_sizes in json_raw['sizes']:
            self.sizes.append(Size(json_raw_sizes['name'], json_raw_sizes['width'], json_raw_sizes['height']))

    def init_dataframe(self, csv_path):
        self.df = pd.read_csv(csv_path, dtype={'number':str})
        
        




