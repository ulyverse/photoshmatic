# dependency modules
import os
import time
import tkinter as tk
from tkinter import BooleanVar
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter.simpledialog import askstring
from requests.exceptions import Timeout


# custom module
import setup
from appcontroller import PhotomaticPro
from configuration import Config
from enumeration import Gender
from utils import Helper


def __dir__():
    return " "


class WindowFrameManager(tk.Tk):
    def __dir__(self):
        return " "

    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Photomatic")
        self._font_style = ("Arial", 12)
        self["pady"] = 10
        self["padx"] = 30
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._frame = None

    def _is_verified(self):
        try:
            if not setup.validate_version():
                self.mbox_error(
                    "This version of the app isn't supported anymore, please update your app to the latest version."
                )
                self.destroy()
                return None
            is_valid_user = setup.validate_registered_device()
            if is_valid_user["status"] == True:
                if is_valid_user["is_expired"] == False:
                    return True
                else:
                    self.mbox_error("Your license key has expired")
        except ConnectionError:
            self.mbox_error(
                "Cannot access the server, please check your internet connection."
            )
        except Timeout:
            self.mbox_error("Request timed out.")
        except Exception as e:
            self.mbox_error(repr(e))

        return False

    def mbox_error(self, message: str, title: str = ""):
        messagebox.showerror(title if title != "" else "Error", message)

    def run(self):
        result = self._is_verified()
        if result:
            self.switch_frame(MainSublimationAppFrame)
        elif result is False:
            self.switch_frame(WelcomeFrame)
        self.mainloop()

    def switch_frame(self, frame_class, *argv):
        if self._frame is not None:
            self._frame.destroy()

        self._frame = frame_class(self, self._font_style, *argv)
        self._frame.grid(row=0, column=0, sticky="NS")


class WelcomeFrame(tk.Frame):
    def __dir__(self):
        return " "

    def __init__(self, master, font):
        tk.Frame.__init__(self, master)
        self.master.minsize(350, 300)
        self._font_style = font
        self._init_widgets()

    def _init_widgets(self):
        self.lbl_company_nane = tk.Label(
            self, text="PHOTOMATIC", font=("Arial Bold Italic", 24)
        )
        self.lbl_company_nane.grid(row=0, column=0, columnspan=2, pady=(0, 50))

        self._lbl_keycode = tk.Label(
            self, text="(enter keycode here)", font=self._font_style
        )
        self._lbl_keycode.grid(row=1, column=0, pady=(0, 1))

        self._txt_keycode = tk.Entry(self, width=29, font=("Consolas", 10))
        self._txt_keycode.grid(row=2, column=0)

        self._btn_keycode = tk.Button(
            self,
            text="ENTER",
            command=self._login,
            font=self._font_style,
            cursor="hand2",
        )
        self._btn_keycode.grid(row=3, column=0, sticky="EW", pady=(20, 40))

        self._lbl_trial_keycode = tk.Label(
            self, text="Enter trial key code", fg="blue", cursor="hand2"
        )
        self._lbl_trial_keycode.grid(row=4, column=0, sticky="EW")
        self._lbl_trial_keycode.bind("<Button-1>", lambda e: self._trial())

    def _login(self):
        key = self._txt_keycode.get()
        if key == "":
            return

        try:
            if setup.enter_license_code(key):
                self.master.switch_frame(MainSublimationAppFrame)
                messagebox.showinfo("Photomatic", "Thank you for purchasing Photomatic")
            else:
                messagebox.showinfo("Photomatic", "Incorrect Keycode, Please try again")
        except ConnectionError:
            self.master.mbox_error(
                "Cannot access the server, please check your internet connection."
            )
        except Timeout:
            self.master.mbox_error("Request timed out.")
        except Exception as e:
            self.master.mbox_error(repr(e))

    def _trial(self):
        trial_key = askstring("T", "enter trial key code here")

        if trial_key == "":
            return
        try:
            if setup.validate_trial_key(trial_key):
                self.master.switch_frame(MainSublimationAppFrame, True)
            else:
                messagebox.showinfo("Photomatic", "Incorrect Keycode, Please try again")
        except ConnectionError:
            self.master.mbox_error(
                "Cannot access the server, please check your internet connection."
            )
        except Timeout:
            self.master.mbox_error("Request timed out.")
        except Exception as e:
            self.master.mbox_error(repr(e))


class MainSublimationAppFrame(tk.Frame):
    def __dir__(self):
        return " "

    def __init__(self, master, font, is_trial=False):
        tk.Frame.__init__(self, master, width=100)

        if is_trial:
            self.master.after(1000 * 60 * 60, self._expire)

        self.master.minsize(875, 475)
        self._font_style = font

        self.rowconfigure(0)
        self.rowconfigure(1, weight=1)

        self._init_frames()
        self._init_widgets()
        self.photomatic = PhotomaticPro()

    def _expire(self):
        messagebox.showinfo("Photomatic", "Your trial has expired")
        self.master.switch_frame(WelcomeFrame)

    def filter_by_gender(self):
        gender = self.cmb_gender.get()
        if gender == "all":
            return
        if gender == "male":
            self.photomatic.filter_by_gender(Gender.MALE)
        elif gender == "female":
            self.photomatic.filter_by_gender(Gender.FEMALE)

    def _init_frames(self):
        self._grp_header = tk.Frame(self)
        self._grp_body = tk.Frame(self, borderwidth=1)

        self._grp_header.grid(row=0)
        self._grp_body.grid(row=1, sticky="N")

        self._grp_body.rowconfigure(0, weight=1)
        self._grp_body.rowconfigure(1, weight=1)

        self._grp_upper_body = tk.Frame(self._grp_body)
        self._grp_lower_body = tk.Frame(self._grp_body)

        self._grp_upper_body.rowconfigure(1, pad=10)

        self._grp_upper_body.columnconfigure(0, weight=1)
        self._grp_upper_body.columnconfigure(1, weight=1)
        self._grp_upper_body.columnconfigure(2, weight=1)
        self._grp_upper_body.columnconfigure(3, weight=1)

        self._grp_upper_body.grid(row=0, sticky="WE")
        self._grp_lower_body.grid(row=1, sticky="WE")

        self._grp_lower_body.columnconfigure(0, weight=1)

    def _init_widgets(self):
        self._lbl_company_name = tk.Label(
            self._grp_header,
            text=Config.get_app_name(),
            font=("Arial Bold Italic", 24),
        )
        self._separator = ttk.Separator(self._grp_header, orient="horizontal")

        # 1
        self.btn_photoshop = tk.Button(
            self._grp_upper_body,
            text="Select Photoshop",
            command=self._select_document,
            font=self._font_style,
            cursor="hand2",
        )
        self.lbl_document_path = tk.Label(self._grp_upper_body, font=self._font_style)

        # 2
        self.btn_csv = tk.Button(
            self._grp_upper_body,
            text="Select Csv",
            command=self._select_datatable,
            font=self._font_style,
            cursor="hand2",
        )
        self.lbl_datatable_path = tk.Label(self._grp_upper_body, font=self._font_style)

        # 3
        self.cmb_sizes = ttk.Combobox(self._grp_upper_body, font=self._font_style)
        self.cmb_sizes.state(
            ["readonly"] if Config.get_sc_resize_image() == True else ["disabled"]
        )
        self._populate_cmb_sizes()

        self.grp_text_settings = tk.Frame(self._grp_upper_body)

        self.lbl_text_settings = tk.Label(
            self.grp_text_settings, text="Text transform: "
        )

        self.cmb_text_settings = ttk.Combobox(self.grp_text_settings, width=10)
        self.cmb_text_settings.state(["readonly"])
        self.cmb_text_settings["values"] = Helper.get_textsettings()
        self.cmb_text_settings.current(0)

        self.grp_filter_gender = tk.Frame(self._grp_upper_body)

        self.lbl_gender = tk.Label(self.grp_filter_gender, text="gender: ")

        self.cmb_gender = ttk.Combobox(self.grp_filter_gender, width=10)
        self.cmb_gender.state(["readonly"])
        self.cmb_gender["values"] = Helper.get_gendersettings()
        self.cmb_gender.current(0)

        self.is_cmyk = BooleanVar()
        self.checkbox_cmyk = ttk.Checkbutton(
            self._grp_upper_body,
            text="Convert image to cmyk",
            variable=self.is_cmyk,
            onvalue=True,
            offvalue=False,
        )

        self.btn_start = tk.Button(
            self._grp_upper_body,
            text="START",
            command=self._start,
            font=self._font_style,
            width=15,
            cursor="hand2",
        )

        # 1
        self.progress_bar = ttk.Progressbar(self._grp_lower_body)

        # 2
        self.txt_result = tk.Text(self._grp_lower_body, width=100, height=10)
        self.txt_result["state"] = "disabled"
        self._refresh_text_box()

        self._put_widgets()

    def _populate_cmb_sizes(self):
        sizes = ["Select Size"]
        for size in os.listdir("sizes/"):
            sizes.append(size[:-5])
        self.cmb_sizes["values"] = sizes
        self.cmb_sizes.current(0)

    def _refresh_text_box(self):
        self._txt_refresh_text(self.txt_result)
        self._txt_append_text(self.txt_result, "REMINDERS:")
        self._txt_append_text(
            self.txt_result,
            " - Don't click anything inside photoshop while the script is running",
        )
        self._txt_append_text(
            self.txt_result,
            " - Layers that you want to be changed by the csv should NOT be inside a group folder",
        )
        self._txt_append_text(
            self.txt_result,
            ' - Text transform doesn\'t always apply! e.g. when the layer has been set to "All Caps"',
        )

    def _put_widgets(self):
        # header
        self._grp_header.grid(row=0, column=0, sticky="WE", pady=(0, 25))
        self._lbl_company_name.grid(row=0, column=0, sticky="E")
        self._separator.grid(row=1, column=0, ipadx=400)

        # upper frame
        # 1
        self.btn_photoshop.grid(row=0, column=0, sticky="WE", padx=(0, 30))
        self.lbl_document_path.grid(row=0, column=1, sticky="W", columnspan=3)

        # 2
        self.btn_csv.grid(row=1, column=0, sticky="WE", padx=(0, 30))
        self.lbl_datatable_path.grid(row=1, column=1, sticky="W", columnspan=3)

        # 3
        self.cmb_sizes.grid(row=2, column=0, sticky="WE", padx=(0, 30))

        self.grp_text_settings.grid(row=2, column=1, sticky="WE")

        self.lbl_text_settings.pack(side="left")
        self.cmb_text_settings.pack(side="left")

        self.grp_filter_gender.grid(row=2, column=2, sticky="WE")
        self.lbl_gender.pack(side="left")
        self.cmb_gender.pack(side="left")

        self.checkbox_cmyk.grid(row=2, column=3, sticky="WE")

        self.btn_start.grid(row=3, column=3, sticky="WE", pady=(10, 0))

        # lower frame
        # 1
        self.progress_bar.grid(
            row=0, column=0, columnspan=4, sticky="WE", pady=(20, 10)
        )

        # 2
        self.txt_result.grid(row=1, column=0, columnspan=4, sticky="NEWS", pady=(0, 20))

    def _select_datatable(self):
        datatable_path = filedialog.askopenfilename(
            title="Select CSV File", filetypes=[("csv files", "*.csv")]
        )
        if datatable_path != "":
            self.lbl_datatable_path["text"] = datatable_path

    def _select_document(self):
        document_path = filedialog.askopenfilename(
            title="Select Photoshop Document", filetypes=[("psd files", "*.psd *.tif")]
        )
        if document_path != "":
            self.lbl_document_path["text"] = document_path

    def _start(self):
        if self.lbl_document_path["text"] == "":
            self.master.mbox_error("Please select a photoshop document")
        elif self.lbl_datatable_path["text"] == "":
            self.master.mbox_error("Please select a csv file")
        elif (
            Config.get_sc_resize_image() == True
            and self.cmb_sizes.get() == "Select Size"
        ):
            self.master.mbox_error("Please select a size")
        else:
            self.progress_bar.stop()
            self._refresh_text_box()
            text_setting = Helper.find_textsetting(self.cmb_text_settings.get())

            sizes = rf"sizes/{self.cmb_sizes.get()}.json"
            document = self.lbl_document_path["text"]
            data_table = self.lbl_datatable_path["text"]
            self._txt_append_text(self.txt_result, "Running script...")

            start_time = time.perf_counter()

            log = self.photomatic.initialize_components(
                document, data_table, sizes, text_setting
            )

            if log == "":
                self.filter_by_gender()
                log += self.photomatic.start(convert_cmyk=self.is_cmyk.get())

            self._txt_append_text(
                self.txt_result,
                f"Execution time: {time.perf_counter()-start_time:0.2f} seconds\n",
            )
            self.progress_bar["value"] = 100

            self._txt_append_text(self.txt_result, "Remarks:")

            if log != "":
                self._txt_append_text(self.txt_result, log)

            messagebox.showinfo("Success", "Done")

    def _txt_append_text(self, txt: tk.Text, content: str):
        txt["state"] = "normal"
        txt.insert(tk.END, f"{content}\n")
        txt["state"] = "disabled"

    def _txt_refresh_text(self, txt: tk.Text):
        txt["state"] = "normal"
        txt.delete("1.0", tk.END)
        txt["state"] = "disabled"

    def update_progress_bar(self, progress):
        self.progress_bar["value"] = progress
