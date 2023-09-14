import tkinter as tk
import tkinter.ttk as ttk
from tkinter import BooleanVar
from tkinter import filedialog

from utils import PhotoshopFiller

import os
from pathlib import Path


class Window:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.font_style = ('Arial', 12)

        self.init_window()
        self.init_widgets()
        self.root.mainloop()

    def init_window(self):
        self.root.minsize(600,400)
        self.root.geometry("700x400")
        self.root.title("Testing")
        self.root['pady'] = 30
        self.root['padx'] = 30

        self.conf_grid()

    def conf_grid(self):
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.columnconfigure(2, weight=2)

        self.root.rowconfigure(0)
        self.root.rowconfigure(1, pad=15)
        self.root.rowconfigure(2)
        self.root.rowconfigure(3, pad=15)
        self.root.rowconfigure(4, weight = 4)

    def init_widgets(self):
        #1
        self.btnPhotoshop = tk.Button(self.root, text="Select Photoshop", command=self._select_psd, font=self.font_style)
        self.lblPhotoshopPath = tk.Label(self.root, text=r"practice.psd", font=self.font_style)

        #2
        self.btnCsv = tk.Button(self.root, text="Select Csv", command=self._select_csv, font=self.font_style)
        self.lblCsvPath = tk.Label(self.root, text=r"data.csv", font=self.font_style)

        #3
        self.cmbSizes = ttk.Combobox(self.root, font=self.font_style)
        self.cmbSizes.state(["readonly"])
        self.populate_cmbSizes()

        self.grpColorModes = tk.Frame(self.root)
        self.colorModes = True
        self.rbtnRGB = tk.Radiobutton(self.grpColorModes, text="RGB", variable=self.colorModes, value=BooleanVar(value=True), font=self.font_style)
        self.rbtnCMYK = tk.Radiobutton(self.grpColorModes, text="CMYK", variable=self.colorModes, value=BooleanVar(value=False), font=self.font_style)

        self.rbtnCMYK.select()

        self.btnStart = tk.Button(self.root, text="START", command=self._start, font=self.font_style, width=15)
        #4
        self.progressBar = ttk.Progressbar(self.root)

        #5
        self.txtResult = tk.Text(self.root)
        self.txtResult.insert(tk.END,"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam ut purus varius, mollis nisi ut, euismod mi. In tempor purus ut dictum fermentum. Sed vulputate et sapien at pretium. Phasellus at arcu sit amet nunc hendrerit ultricies. Morbi dapibus auctor malesuada. Nam lacinia condimentum elit, in malesuada elit luctus sit amet. Phasellus in elit non nibh mollis porttitor. Morbi quis eros id orci sodales finibus eu nec neque. Donec ex ante, eleifend at congue et, volutpat eget quam. Duis elit ligula, cursus at vehicula eu, dictum vitae nisl. Cras molestie erat vel vestibulum vehicula. Nunc quis dignissim metus. Sed porta nec leo ac euismod. Sed tincidunt elit vitae quam tincidunt, ac ultricies nisi mollis.")
        self.txtResult['state'] = "disabled"

        self.put_widgets()

    def put_widgets(self):
        #1
        self.btnPhotoshop.grid(row=0, column=0, sticky="WE", padx=(0,30))
        self.lblPhotoshopPath.grid(row=0, column=1, sticky="W", columnspan=2)

        #2
        self.btnCsv.grid(row=1, column=0, sticky="WE", padx=(0,30))
        self.lblCsvPath.grid(row=1, column=1, sticky="W", columnspan=2)

        #3
        self.cmbSizes.grid(row=2, column=0, sticky="WE", padx=(0,30))
        self.grpColorModes.grid(row=2, column=1, sticky="W")
        self.rbtnRGB.pack(side="left")
        self.rbtnCMYK.pack(side="left", padx=20)
        self.btnStart.grid(row=2, column=2, sticky="WE")

        #4
        self.progressBar.grid(row=3, column=0, columnspan=3, sticky="WE", pady=(20,0))

        #5
        self.txtResult.grid(row=4, column=0, columnspan=3, sticky="NEWS")

    def _select_psd(self):
        psd_path = filedialog.askopenfilename(title="Select Photoshop Document", filetypes=[("psd files", "*.psd")])
        self.lblPhotoshopPath['text'] = psd_path

    def _select_csv(self):
        csv_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("csv files", "*.csv")])
        self.lblCsvPath['text'] = csv_path

    def _start(self):
        print(self.cmbSizes.get())


    def populate_cmbSizes(self):
        sizes = ['Select Size']
        for size in os.listdir(str(Path(__file__).parent) + "/Sizes"):
            sizes.append(size[:-5])
        self.cmbSizes['values'] = sizes
        self.cmbSizes.current(0)

gui = Window()

print("TEST")
print(gui.lblCsvPath['text'])