"""
this is the monolith version of the current utils.py
this shouldn't be used.
"""

#dependency modules
import pandas as pd
from photoshop import Session

#built-in modules
import json
from pathlib import Path

#custom modules
from sizes import Size

psd_path = Path(r"C:\Users\johna\Desktop\Photoshamatic\Photo1\Test1\practice2.psd")
csv_path = Path(r"C:\Users\johna\Desktop\Photoshamatic\Photo1\Test1\test.csv")
json_path = Path(r"C:\Users\johna\Desktop\Photoshamatic\Sizes\upper_jersey.json")


#import sizes
with open(str(json_path)) as s:
    json_raw = json.load(s)

sizes = []

for json_raw_sizes in json_raw['sizes']:
    sizes.append(Size(json_raw_sizes['name'], json_raw_sizes['width'], json_raw_sizes['height']))


#import csv
df = pd.read_csv(str(csv_path))

#import photoshop
with Session(str(psd_path), "open") as ps:

    #local variables
    doc = ps.active_document
    layers = doc.layers
    columns = df.columns

    #photoshop settings
    options = ps.JPEGSaveOptions(quality=12)
    ps.app.preferences.rulerUnits = ps.Units.Inches

    #color mode
    isRGB = True
    doc.changeMode(ps.ChangeMode.ConvertToRGB if isRGB else ps.ChangeMode.ConvertToCMYK)

    #checking for labels
    csvHasLabel = False
    psHasLabel = False
    csvLabel = None

    for col in columns:
        if col == "label":
            csvHasLabel = True
            csvLabel = col
            break

    for layer in layers:
        if(layer.name == "label"):
            psHasLabel = True
            break

    #changing labels
    if csvHasLabel and psHasLabel:
        for i in layers:
            if(i.name == "label"):
                i.textItem.contents = "Testing"

    noMatchLayers = []

    #removing labels in df if has any
    if csvHasLabel:
        noMatchLayers.append(csvLabel)

    #removing any columns in df that have no corresponding layers
    for col in columns:
        notInLayer = True
        for layer in layers:
            if col.lower().strip() == "size" or layer.name == col:
                notInLayer = False
                break
        if notInLayer:
            noMatchLayers.append(col)

    df.drop(noMatchLayers,axis=1,inplace=True)

    #refresh column (important!)
    columns = df.columns

    #filling documents with csv
    for row in range(len(df.index)):
        doc_num = row + 1
        new_copy = ps.app.activeDocument.duplicate(f"{doc_num}")
        path = str(psd_path.parent) + f"\{doc_num}"

        current_row_size = df.loc[row, 'size']

        for col in columns:
            currentLayer = new_copy.layers.getByName(col)
            currentLayer.textItem.contents = df.loc[row, col]
        
        for size in sizes:
            if size.name == current_row_size:
                new_copy.resizeImage(size.width, size.height, new_copy.resolution)

        ps.active_document.saveAs(path, options)
