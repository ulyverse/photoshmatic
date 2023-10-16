#dependency modules
from requests.exceptions import ConnectionError

#built-in modules
import os
import time
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import BooleanVar
from tkinter import filedialog
from tkinter import messagebox

#custom module
import setup
from utils import Helper
from utils import PhotoshopFiller


def __dir__():
    return " "

class WindowFrameManager(tk.Tk):
    def __dir__():
        return " "
    
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Printing Sublimation System")
        self['pady'] = 10
        self['padx'] = 30
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._frame = None

    def switch_frame(self, frame_class):
        if self._frame is not None:
            self._frame.destroy()

        self._font_style = ('Arial', 12)
        self._frame = frame_class(self, self._font_style)
        self._frame.grid(row=0, column=0, sticky="NS")

    def _is_verified(self):
        try:
            if not setup.validate_version():
                self._mbox_error("This version of the app isn't supported anymore, please update your app to the latest version.")
                self.destroy()
                return None
            is_valid_user = setup.validate_registered_device()
            if is_valid_user['status'] == True:
                if is_valid_user['is_expired'] == False:
                    return True
                else:
                    self._mbox_error("Your license key has expired")
        except ConnectionError as e:
            self._mbox_error("Cannot access the server, please check your internet connection.")
        except Exception as e:
            self._mbox_error(repr(e))

        return False
        
    def run(self):
        result = self._is_verified()
        if result:
            self.switch_frame(MainSublimationAppFrame)
        elif result is False:
            self.switch_frame(WelcomeFrame)
        self.mainloop()

    def _mbox_error(self,message:str, title:str = None):
        messagebox.showerror(title if title != None else "Error", message)


class WelcomeFrame(tk.Frame):
    def __dir__():
        return " "
    
    def __init__(self, master, font):
        tk.Frame.__init__(self, master)
        self.master.minsize(350,300)
        self._font_style = font
        self._init_widgets()

    def _init_widgets(self):
        self._lblCompanyName = tk.Label(self, text="PHOTOMATIC", font=("Arial Bold Italic", 24))
        self._lblCompanyName.grid(row=0, column=0, columnspan=2, pady=(0,50))

        self._lblKeycode = tk.Label(self, text="(enter keycode here)", font=self._font_style)
        self._lblKeycode.grid(row=1, column=0, pady=(0,1))

        self._txtKeycode = tk.Entry(self,width=29, font=("Consolas", 10))
        self._txtKeycode.grid(row=2, column=0)

        self._btnKeycode = tk.Button(self, text="ENTER", command=self._login, font=self._font_style)
        self._btnKeycode.grid(row=3, column=0, sticky="EW", pady=(20,0))

    def _login(self):
        try:
            key = self._txtKeycode.get()
            if setup.enter_license_code(key):
                self.master.switch_frame(MainSublimationAppFrame)
                messagebox.showinfo("Printing Sublimation System", "Thank you for purchasing Photomatic")
            else:
                messagebox.showinfo("Printing Sublimation System", "Incorrect Keycode, Please try again")
        except (ConnectionError) as e:
            self.master._mbox_error("Cannot access the server, please check your internet connection.")
        except Exception as e:
            self.master._mbox_error(repr(e))


class MainSublimationAppFrame(tk.Frame):
    def __dir__():
        return " "

    def __init__(self, master, font):
        tk.Frame.__init__(self, master, width=100)

        self.master.minsize(817,400)
        self._font_style = font

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=2)

        self.rowconfigure(0)
        self.rowconfigure(1)
        self.rowconfigure(2, pad=15)
        self.rowconfigure(3)
        self.rowconfigure(4, pad=15)
        self.rowconfigure(5, weight = 4)
        self._init_widgets()
        self.ps_filler = PhotoshopFiller()

    def _start(self):
        if self.lblPhotoshopPath['text'] == "":
            self.master._mbox_error("Please select a photshop document")
        elif self.lblCsvPath['text'] == "":
            self.master._mbox_error("Please select a csv file")
        elif self.cmbSizes.get() == "Select Size":
            self.master._mbox_error("Please select a size")
        else:
            self._select_sizes()
            self._set_text_settings()
            self.progressBar.stop()
            self._populate_txtResult()
            self._txt_append_text(self.txtResult, "Running script...")
            start_time = time.time()

            log = self.ps_filler.start(convertCMYK=self.isCMYK.get())

            self._txt_append_text(self.txtResult, f"Execution time: {time.time()-start_time:0.2f} seconds\n")
            self.progressBar['value'] = 100

            self._txt_append_text(self.txtResult, "Remarks:")

            if log != "":
                self._txt_append_text(self.txtResult, log)

            messagebox.showinfo("Success", "Done")

    def update_progress_bar(self, progress):
        self.progressBar['value'] = progress

    def _init_widgets(self):
        #1
        self.btnPhotoshop = tk.Button(self, text="Select Photoshop", command=self._select_psd, font=self._font_style)
        self.lblPhotoshopPath = tk.Label(self, font=self._font_style)

        #2
        self.btnCsv = tk.Button(self, text="Select Csv", command=self._select_csv, font=self._font_style)
        self.lblCsvPath = tk.Label(self, font=self._font_style)

        #3
        self.cmbSizes = ttk.Combobox(self, font=self._font_style)
        self.cmbSizes.state(["readonly"])
        self._populate_cmbSizes()

        self.grpTextSettings = tk.Frame(self)

        self.lblTextSettings = tk.Label(self.grpTextSettings, text="Text transform: ")

        self.cmbTextSettings = ttk.Combobox(self.grpTextSettings, width=10)
        self.cmbTextSettings.state(["readonly"])
        self.cmbTextSettings['values'] = Helper.get_textsettings()
        self.cmbTextSettings.current(0)
        
        self.isCMYK = BooleanVar()
        self.checkCMYK = ttk.Checkbutton(self.grpTextSettings, text="Convert image to cmyk", variable=self.isCMYK, onvalue=True, offvalue=False)
        
        self.btnStart = tk.Button(self, text="START", command=self._start, font=self._font_style, width=15)

        #4
        self.progressBar = ttk.Progressbar(self)

        #5
        self.txtResult = tk.Text(self, width=100, height=10)
        self.txtResult['state'] = "disabled"
        self._populate_txtResult()

        self._put_widgets()

    def _put_widgets(self):
        #0 this is hacky fix later
        self._hacky_frame = tk.Frame(self)
        self._hacky_frame.grid(row=0, column=0, sticky="WE", pady=(0,25), columnspan=3)

        self._lblCompanyName = tk.Label(self._hacky_frame, text="PHOTOMATIC", font=("Arial Bold Italic", 24))
        self._lblCompanyName.grid(row=0, column=0, sticky="E")
        self._separator = ttk.Separator(self._hacky_frame, orient="horizontal")
        self._separator.grid(row=1, column=0, ipadx=400)

        #1
        self.btnPhotoshop.grid(row=1, column=0, sticky="WE", padx=(0,30))
        self.lblPhotoshopPath.grid(row=1, column=1, sticky="W", columnspan=2)

        #2
        self.btnCsv.grid(row=2, column=0, sticky="WE", padx=(0,30))
        self.lblCsvPath.grid(row=2, column=1, sticky="W", columnspan=2)

        #3
        self.cmbSizes.grid(row=3, column=0, sticky="WE", padx=(0,30))

        #grpTextSettings
        self.grpTextSettings.grid(row=3, column=1, sticky="WE", padx=(0, 30))
        self.lblTextSettings.pack(side="left")
        self.cmbTextSettings.pack(side="left", padx=(0,30))
        self.checkCMYK.pack(side="left")

        self.btnStart.grid(row=3, column=2, sticky="WE")

        #4
        self.progressBar.grid(row=4, column=0, columnspan=3, sticky="WE", pady=(20,0))

        #5
        self.txtResult.grid(row=5, column=0, columnspan=3, sticky="NEWS", pady=(0,20))

    def _select_psd(self):
        psd_path = filedialog.askopenfilename(title="Select Photoshop Document", filetypes=[("psd files", "*.psd *.tif")])
        if psd_path != "":
            self.lblPhotoshopPath['text'] = psd_path
            self.ps_filler.init_photoshop(psd_path)

    def _select_csv(self):
        csv_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("csv files", "*.csv")])

        if csv_path != "":
            self.lblCsvPath['text'] = csv_path
            self.ps_filler.init_dataframe(csv_path)

    def _select_sizes(self):
        json_path = fr"sizes/{self.cmbSizes.get()}.json"
        self.ps_filler.init_sizes(json_path)

    def _set_text_settings(self):
        self.ps_filler.text_settings = self.cmbTextSettings.get()

    def _populate_cmbSizes(self):
        sizes = ['Select Size']
        for size in os.listdir("sizes/"):
            sizes.append(size[:-5])
        self.cmbSizes['values'] = sizes
        self.cmbSizes.current(0)

    def _populate_txtResult(self):
        self._txt_refresh_text(self.txtResult)
        self._txt_append_text(self.txtResult, "REMINDERS:")
        self._txt_append_text(self.txtResult, " - Don't click anything inside photoshop while the script is running")
        self._txt_append_text(self.txtResult, " - Layers that you want to be changed by the csv should NOT be inside a group folder")
        self._txt_append_text(self.txtResult, " - If you have made changes to your csv, you need to reselect the file inorder to apply the changes")
        self._txt_append_text(self.txtResult, " - Text transform does't always apply! e.g. when the layer has been set to \"All Caps\"")

    def _txt_refresh_text(self, txt:tk.Text):
        txt['state'] = "normal"
        txt.delete("1.0", tk.END)
        txt['state'] = "disabled"

    def _txt_append_text(self, txt: tk.Text, content:str):
        txt['state'] = "normal"
        txt.insert(tk.END, f"{content}\n")
        txt['state'] = "disabled"
