from photoshop import Session
from photoshop import api as ps
from pathlib import Path
from sizes import Size
import pandas as pd
import os
import json

app = ps.Application()

print(app.activeDocument.name)
app.activeDocument.duplicate("test")
print(app.activeDocument.name)


app.activeDocument.close(ps.SaveOptions.DoNotSaveChanges)
print(app.activeDocument.name)

