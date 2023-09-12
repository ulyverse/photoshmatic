from photoshop import Session
import pandas as pd

df = pd.read_csv(r"C:\Users\johna\Desktop\Photoshamatic\Photo1\Book1.csv")


for col in df.columns:
    print(col)
print(df)

myList = []

for col in df.columns:
    if(col == "yippie"):
        myList.append(col)

df.drop(myList, axis=1, inplace=True)

for col in df.columns:
    print(col)

print(df)

# print(len(df.index))
# Test = df.loc[1,"date"]
# print(Test)

with Session(r"C:\Users\johna\Desktop\Photoshamatic\Photo1\first.psd", "open") as ps:
    layers = ps.active_document.layers


    isInLayers = False
    for layer in layers:
        if layer.name == "name":
            isInLayers = True
            break

    name = ps.active_document.layers.getByName("name")
    name.textItem.contents = "Hi"



        