import tkinter as tk
import tkinter.ttk as ttk
from tkinter import BooleanVar

root = tk.Tk()
root.geometry("700x500")
root.title("Testing")

root['padx'] = 30
root['pady'] = 30

font_style = ('Verdana', 12)

btn_width = 15

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)

root.rowconfigure(0, weight = 1)
root.rowconfigure(1, weight = 1)
root.rowconfigure(2, weight = 1)
root.rowconfigure(3, weight = 4)

#1
btnPhotoshop = tk.Button(root, text="Select Photoshop", font=font_style, width=btn_width)
lblPhotoshopPath = tk.Label(root, text=r"test2.pdf", font=font_style, background="red")

#2
btnCsv = tk.Button(root, text="Select Csv", font=font_style, width=btn_width)
lblCsvPath = tk.Label(root, text=r"test.csv", font=font_style, background="red")

#3
cmbSizes = ttk.Combobox(root, font=font_style, width=btn_width)
cmbSizes.state(["readonly"])
cmbSizes['values'] = ('Select Size', 'Size1')
cmbSizes.current(0)

grpColorModes = tk.Frame(root)
colorModes = True
rbtnRGB = tk.Radiobutton(grpColorModes, text="RGB", variable=colorModes, value=BooleanVar(value=True), font=font_style)
rbtnCMYK = tk.Radiobutton(grpColorModes, text="CMYK", variable=colorModes, value=BooleanVar(value=False), font=font_style)

btnStart = tk.Button(root, text="START", font=font_style, width=btn_width)

#4
progressBar = ttk.Progressbar(root)

#5
txtResult = tk.Text(root, height=10)



btnPhotoshop.grid(row=0, column=0)
lblPhotoshopPath.grid(row=0, column=1, sticky="W", columnspan=2)

btnCsv.grid(row=1, column=0)
lblCsvPath.grid(row=1, column=1, sticky="W", columnspan=2)

cmbSizes.grid(row=2, column=0)
grpColorModes.grid(row=2, column=1)
rbtnRGB.pack(side="left")
rbtnCMYK.pack(side="left")
btnStart.grid(row=2, column=2)

progressBar.grid(row=3, column=0, columnspan=3, sticky="WE")

txtResult.grid(row=4, column=0, columnspan=3)


root.mainloop()