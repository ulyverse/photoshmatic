#built-in modules
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import BooleanVar
from tkinter import filedialog
from tkinter import messagebox
import threading

import os
from pathlib import Path

#custom module
from utils import PhotoshopFiller


class Window:
    def __init__(self) -> None:
        self.ps_filler = PhotoshopFiller()

    def run(self):
        self._init_window()
        self._init_widgets()
        self.root.mainloop()

    def _start(self):
        if self.lblPhotoshopPath['text'] == "":
            self._mbox_error("Please select a photshop document")
        elif self.lblCsvPath['text'] == "":
            self._mbox_error("Please select a csv file")
        elif self.cmbSizes.get() == "Select Size":
            self._mbox_error("Please select a size")
        else:
            self._select_sizes()
            self.progressBar.stop()
            self._txt_append_text(self.txtResult, "Running script...\n")
            log = self.ps_filler.start()

            if log != "":
                self._txt_append_text(self.txtResult, log)

    def _init_window(self):
        self.font_style = ('Arial', 12)
        self.root = tk.Tk()
        self.root.minsize(600,400)
        self.root.geometry("700x400")
        self.root.title("Testing")
        self.root['pady'] = 30
        self.root['padx'] = 30

        self._conf_grid()

    def _conf_grid(self):
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.columnconfigure(2, weight=2)

        self.root.rowconfigure(0)
        self.root.rowconfigure(1, pad=15)
        self.root.rowconfigure(2)
        self.root.rowconfigure(3, pad=15)
        self.root.rowconfigure(4, weight = 4)

    def _init_widgets(self):
        #1
        self.btnPhotoshop = tk.Button(self.root, text="Select Photoshop", command=self._select_psd, font=self.font_style)
        self.lblPhotoshopPath = tk.Label(self.root, font=self.font_style)

        #2
        self.btnCsv = tk.Button(self.root, text="Select Csv", command=self._select_csv, font=self.font_style)
        self.lblCsvPath = tk.Label(self.root, font=self.font_style)

        #3
        self.cmbSizes = ttk.Combobox(self.root, font=self.font_style)
        self.cmbSizes.state(["readonly"])
        self._populate_cmbSizes()

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
        self.txtResult['state'] = "disabled"
        self._populate_txtResult()

        self._put_widgets()

    def _put_widgets(self):
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
        if psd_path != "":
            self.lblPhotoshopPath['text'] = self._shorten_path(psd_path)
            self.ps_filler.init_photoshop(psd_path)

            if self.ps_filler.get_isRGB():
                self.rbtnRGB.select()
            else:
                self.rbtnCMYK.select()

    def _select_csv(self):
        csv_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("csv files", "*.csv")])
        if csv_path != "":
            self.lblCsvPath['text'] = self._shorten_path(csv_path)
            self.ps_filler.init_dataframe(csv_path)

    def _select_sizes(self):
        json_path = f"{Path(__file__).parent}\sizes\{self.cmbSizes.get()}.json"
        self.ps_filler.init_sizes(json_path)
        self.ps_filler.print_sizes()

    def _shorten_path(self, raw_path:str) -> str:
        path = Path(raw_path)
        return f"{raw_path[:2]}/.../{path.parent.name}/{path.name}"

    def _mbox_error(self,message:str, title:str = None):
        messagebox.showerror(title if title != None else "Warning!", message)

    def _populate_cmbSizes(self):
        sizes = ['Select Size']
        for size in os.listdir(str(Path(__file__).parent) + "/sizes"):
            sizes.append(size[:-5])
        self.cmbSizes['values'] = sizes
        self.cmbSizes.current(0)

    def _populate_txtResult(self):
        self._txt_append_text(self.txtResult, "REMINDERS: \n")
        self._txt_append_text(self.txtResult, " - layers inside a folder cannot be altered\n")
        self._txt_append_text(self.txtResult, " - don't click on another tab in photoshop while the script is running\n")
        self._txt_append_text(self.txtResult, " - be wary of the color modes radiobutton\n")
        self._txt_append_text(self.txtResult, " - to configuration settings view settings.json\n")

    def _txt_append_text(self, txt: tk.Text, content:str):
        txt['state'] = "normal"
        txt.insert(tk.END, content)
        txt['state'] = "disabled"