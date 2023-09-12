from photoshop import Session
from pathlib import Path
from sizes import Size
import pandas as pd
import os
import json

with Session(r"C:\Users\johna\Desktop\Photoshamatic\Photo1\practice.psd", "open") as ps:
    print("HELLO WORLD!")

    print(ps.active_document.resolution)

# csv_path = Path(r"C:\Users\johna\Desktop\Photoshamatic\Photo1\Book1.csv")
# df = pd.read_csv(str(csv_path))

# print(df)

# csvHasLabel = False
# csvLabel = None

# for col in df.columns:
#     if col == "label":
#         csvHasLabel = True
#         csvLabel = col
#         break

# noMatchLayers = []

# if csvHasLabel:
#     noMatchLayers.append(csvLabel)

# df.drop(noMatchLayers,axis=1,inplace=True)


# print("haslabel" if csvHasLabel else "hasnolabel")
# print(df)




# print(df)

# layers = ["date", "name"]
# noMatchLayers = []

# for col in df.columns:
#         notInLayer = True
#         for layer in layers:
#             if col.lower().strip() == "size" or layer == col:
#                 notInLayer = False
#                 break
#         if notInLayer:
#             noMatchLayers.append(col)


# df.drop(noMatchLayers,axis=1,inplace=True)


# print(df)


# # with Session(r"C:\Users\johna\Desktop\Photoshamatic\Photo1\practice.psd", "open") as ps:
# print("HELLO WORLD!")

# json_path = Path(r"C:\Users\johna\Desktop\Photoshamatic\Sizes\female sleeves.json")

# sizes = []

# with open(str(json_path)) as s:
#     json_sizes = json.load(s)

# for testt in json_sizes['sizes']:
#     sizes.append(Size(testt['name'], testt['width'], testt['height']))

# for size in sizes:
#     print(size.name)
#     print(size.width)
#     print(size.height)

    

    # print(json_sizes['sizes'][1])

    # myStr = "small"

    # for testt in json_sizes['sizes']:
    #     if(testt['name'] == myStr):
    #         myObj = testt
    
    # print(myObj)

    # size_list = []

    # for size in range(len(json_sizes)):
    #     size = json.loads(json_sizes[size], object_hook=Size.deserialize_json)

    # for x in range(size_list):
    #     print(size_list[x].name)

    # isRGB = True
    
    # ps.active_document.changeMode(ps.ChangeMode.ConvertToRGB if isRGB else ps.ChangeMode.ConvertToCMYK)

    # doc = ps.active_document
    # doc.resizeImage(30, 16.875)


    # myPath = Path(r"C:\Users\johna\Desktop\Photoshamatic\Photo1\practice.psd")


    # new_copy = ps.app.activeDocument.duplicate("copy")


    # titleLayer = new_copy.layers.getByName("title")
    # titleLayer.textItem.contents = "lorem ipsum me kasa so good"
    # path = str(myPath.parent) + "\\testedd.jpg"
    # ps.active_document.saveAs(path, options = ps.JPEGSaveOptions(quality=12))

    # savedState = ps.app.activeDocument.activeHistoryState

    # ps.app.executeAction(ps.app.charIDToTypeID("undo"), None)

    # ps.active_document.activeHistoryState = savedState

    


    


