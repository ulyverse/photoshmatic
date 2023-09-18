#built-in modules
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import messagebox
import time

import os
from pathlib import Path

#custom module
from utils import PhotoshopFiller
from utils import Helper


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
            self._set_text_settings()
            self.progressBar.stop()
            self._populate_txtResult()
            self._txt_append_text(self.txtResult, "Running script...")
            start_time = time.time()

            log = self.ps_filler.start()

            self._txt_append_text(self.txtResult, f"Execution time: {time.time()-start_time:0.2f} seconds\n")
            self.progressBar['value'] = 100

            self._txt_append_text(self.txtResult, "Remarks:")

            if log != "":
                self._txt_append_text(self.txtResult, log)

            messagebox.showinfo("Success", "Done")

    def update_progress_bar(self, progress):
        self.progressBar['value'] = progress

    def _init_window(self):
        self.font_style = ('Arial', 12)
        self.root = tk.Tk()
        self.root.minsize(600,400)
        self.root.geometry("700x400")
        self.root.title("Photoshop CSV Filler")
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

        self.grpTextSettings = tk.Frame(self.root)

        self.lblTextSettings = tk.Label(self.grpTextSettings, text="Text Transform: ", font=self.font_style)
        self.lblTextSettings.pack(side="left")

        self.cmbTextSettings = ttk.Combobox(self.grpTextSettings, font=self.font_style)
        self.cmbTextSettings.state(["readonly"])
        self.cmbTextSettings['values'] = Helper.get_textsettings()
        self.cmbTextSettings.current(0)
        self.cmbTextSettings.pack(side="left")
        

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
        self.grpTextSettings.grid(row=2, column=1, sticky="WE", padx=(0,30))
        self.btnStart.grid(row=2, column=2, sticky="WE")

        #4
        self.progressBar.grid(row=3, column=0, columnspan=3, sticky="WE", pady=(20,0))

        #5
        self.txtResult.grid(row=4, column=0, columnspan=3, sticky="NEWS")

    def _select_psd(self):
        psd_path = filedialog.askopenfilename(title="Select Photoshop Document", filetypes=[("psd files", "*.psd *.tif")])
        if psd_path != "":
            self.lblPhotoshopPath['text'] = Path(psd_path).name
            self.ps_filler.init_photoshop(psd_path)

    def _select_csv(self):
        csv_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("csv files", "*.csv")])
        if csv_path != "":
            self.lblCsvPath['text'] = Path(csv_path).name
            self.ps_filler.init_dataframe(csv_path)

    def _select_sizes(self):
        json_path = f"{Path(__file__).parent}\sizes\{self.cmbSizes.get()}.json"
        self.ps_filler.init_sizes(json_path)

    def _set_text_settings(self):
        self.ps_filler.text_settings = self.cmbTextSettings.get()

    def _mbox_error(self,message:str, title:str = None):
        messagebox.showerror(title if title != None else "Error", message)

    def _populate_cmbSizes(self):
        sizes = ['Select Size']
        for size in os.listdir(str(Path(__file__).parent) + "/sizes"):
            sizes.append(size[:-5])
        self.cmbSizes['values'] = sizes
        self.cmbSizes.current(0)

    def _populate_txtResult(self):
        self._txt_refresh_text(self.txtResult)
        self._txt_append_text(self.txtResult, "REMINDERS:")
        self._txt_append_text(self.txtResult, " - layers inside a folder cannot be altered")
        self._txt_append_text(self.txtResult, " - you need to reselect csv to apply changes")
        self._txt_append_text(self.txtResult, " - don't click on another tab in photoshop while the script is running")

    def _txt_refresh_text(self, txt:tk.Text):
        txt['state'] = "normal"
        txt.delete("1.0", tk.END)
        txt['state'] = "disabled"

    def _txt_append_text(self, txt: tk.Text, content:str):
        txt['state'] = "normal"
        txt.insert(tk.END, f"{content}\n")
        txt['state'] = "disabled"