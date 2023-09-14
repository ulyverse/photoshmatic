import tkinter as tk
import tkinter.ttk as ttk
from tkinter import BooleanVar
from tkinter import filedialog

root = tk.Tk()
root.minsize(600,400)
root.geometry("700x400")
root.title("Testing")

root['padx'] = 30
root['pady'] = 30

font_style = ('Arial', 12)

btn_width = 15

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=2)
root.columnconfigure(2, weight=2)

root.rowconfigure(0)
root.rowconfigure(1, pad=15)
root.rowconfigure(2)
root.rowconfigure(3, pad=15)
root.rowconfigure(4, weight = 4)

#1
btnPhotoshop = tk.Button(root, text="Select Photoshop", font=font_style)
lblPhotoshopPath = tk.Label(root, text=r"practice.psd", font=font_style)

#2
btnCsv = tk.Button(root, text="Select Csv", font=font_style)
lblCsvPath = tk.Label(root, text=r"data.csv", font=font_style)

#3
cmbSizes = ttk.Combobox(root, font=font_style)
cmbSizes.state(["readonly"])
cmbSizes['values'] = ('Select Size', 'Size1')
cmbSizes.current(0)

grpColorModes = tk.Frame(root)
colorModes = True
rbtnRGB = tk.Radiobutton(grpColorModes, text="RGB", variable=colorModes, value=BooleanVar(value=True), font=font_style)
rbtnCMYK = tk.Radiobutton(grpColorModes, text="CMYK", variable=colorModes, value=BooleanVar(value=False), font=font_style)

rbtnCMYK.select()

btnStart = tk.Button(root, text="START", font=font_style, width=btn_width)
#4
progressBar = ttk.Progressbar(root)

#5
txtResult = tk.Text(root)
txtResult.insert(tk.END,"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam ut purus varius, mollis nisi ut, euismod mi. In tempor purus ut dictum fermentum. Sed vulputate et sapien at pretium. Phasellus at arcu sit amet nunc hendrerit ultricies. Morbi dapibus auctor malesuada. Nam lacinia condimentum elit, in malesuada elit luctus sit amet. Phasellus in elit non nibh mollis porttitor. Morbi quis eros id orci sodales finibus eu nec neque. Donec ex ante, eleifend at congue et, volutpat eget quam. Duis elit ligula, cursus at vehicula eu, dictum vitae nisl. Cras molestie erat vel vestibulum vehicula. Nunc quis dignissim metus. Sed porta nec leo ac euismod. Sed tincidunt elit vitae quam tincidunt, ac ultricies nisi mollis.")
txtResult['state'] = "disabled"


btnPhotoshop.grid(row=0, column=0, sticky="WE", padx=(0,30))
lblPhotoshopPath.grid(row=0, column=1, sticky="W", columnspan=2)

btnCsv.grid(row=1, column=0, sticky="WE", padx=(0,30))
lblCsvPath.grid(row=1, column=1, sticky="W", columnspan=2)

cmbSizes.grid(row=2, column=0, sticky="WE", padx=(0,30))
grpColorModes.grid(row=2, column=1, sticky="W")
rbtnRGB.pack(side="left")
rbtnCMYK.pack(side="left", padx=20)
btnStart.grid(row=2, column=2, sticky="WE")

progressBar.grid(row=3, column=0, columnspan=3, sticky="WE", pady=(20,0))

txtResult.grid(row=4, column=0, columnspan=3, sticky="NEWS")


root.mainloop()