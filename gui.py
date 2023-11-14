# dependency modules
import time

# import tkinter as tk
from tkinter import BooleanVar
from tkinter import filedialog
from tkinter import messagebox
from tkinter import PhotoImage
from tkinter import StringVar
from tkinter.simpledialog import askstring
from requests.exceptions import Timeout
import customtkinter as ctk
import warnings


# custom modules
import setup
from configuration import Config
from core import PhotomaticController
from utils import Helper


def __dir__():
    return " "


warnings.filterwarnings("ignore")
ctk.set_appearance_mode("light")


class WindowFrameManager(ctk.CTk):
    def __dir__(self):
        return " "

    def __init__(self):
        super().__init__()
        self.title("Photomatic")
        self.resizable(False, False)
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
            self.mbox_error(
                "Cannot access the server, please check your internet connection."
            )

        return False

    def mbox_error(self, message: str, title: str = ""):
        messagebox.showerror(title if title != "" else "Error", message)

    def run(self):
        result = self._is_verified()
        if result:
            self.switch_frame(PhotomaticWindowApp)
        elif result is False:
            self.switch_frame(WelcomeFrame)
        self.mainloop()

    def switch_frame(self, frame_class, *argv):
        if self._frame is not None:
            self._frame.destroy()

        self._frame = frame_class(self, *argv)
        self._frame.pack(pady=30, padx=30)


class WelcomeFrame(ctk.CTkFrame):
    def __dir__(self):
        return " "

    def __init__(self, master):
        super().__init__(master)
        self._init_widgets()

    def _init_widgets(self):
        self.lbl_company_nane = ctk.CTkLabel(
            self,
            text="PHOTOMATIC",
            font=ctk.CTkFont("Arial", 30, weight="bold", slant="italic"),
        )
        self.lbl_company_nane.grid(row=0, column=0, columnspan=2, pady=(15, 35))

        self._lbl_keycode = ctk.CTkLabel(self, text="(enter keycode here)")
        self._lbl_keycode.grid(row=1, column=0, pady=(0, 1))

        self._txt_keycode = ctk.CTkEntry(
            self, width=247, font=ctk.CTkFont("Consolas", 15)
        )
        self._txt_keycode.grid(row=2, column=0, padx=15)

        self._btn_keycode = ctk.CTkButton(
            self, text="ENTER", command=self._login, cursor="hand2"
        )
        self._btn_keycode.grid(row=3, column=0, sticky="EW", pady=(10, 35), padx=15)

        self._lbl_trial_keycode = ctk.CTkLabel(
            self, text="Enter trial key code", text_color="blue", cursor="hand2"
        )
        self._lbl_trial_keycode.grid(row=4, column=0, sticky="EW", pady=(0, 15))
        self._lbl_trial_keycode.bind("<Button-1>", lambda e: self._trial())

    def _login(self):
        key = self._txt_keycode.get()
        if key == "":
            return

        try:
            if setup.enter_license_code(key):
                self.master.switch_frame(PhotomaticWindowApp)
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
            self.mbox_error(
                "Cannot access the server, please check your internet connection."
            )

    def _trial(self):
        trial_key = askstring("T", "enter trial key code here")

        if trial_key == "":
            return
        try:
            if setup.validate_trial_key(trial_key):
                self.master.switch_frame(PhotomaticWindowApp, True)
            else:
                messagebox.showinfo("Photomatic", "Incorrect Keycode, Please try again")
        except ConnectionError:
            self.master.mbox_error(
                "Cannot access the server, please check your internet connection."
            )
        except Timeout:
            self.master.mbox_error("Request timed out.")
        except Exception as e:
            self.mbox_error(
                "Cannot access the server, please check your internet connection."
            )


class PhotomaticWindowApp(ctk.CTkFrame):
    def __dir__(self):
        return " "

    def __init__(self, master, is_trial=False):
        super().__init__(master)
        self.photomatic_controller = PhotomaticController()

        if is_trial is True:
            self.after(1000 * 60 * 60, self.expire)

        paddingframe = ctk.CTkFrame(self, fg_color="transparent")
        paddingframe.pack(padx=10, pady=10)

        self.app_header = HeaderFrame(paddingframe)
        self.app_header.pack(fill="x")

        self.cloth_frame = ClothManagerFrame(paddingframe, self)
        self.cloth_frame.pack(fill="x", pady=(15, 0))

        self.datatable_frame = DatatableFrame(paddingframe, self)
        self.datatable_frame.pack(fill="x", pady=15)

        self.start_frame = OptionsAndStartFrame(paddingframe, self)
        self.start_frame.pack(fill="x", pady=(0, 40))

        self.remarks_frame = RemarksFrame(paddingframe)
        self.remarks_frame.pack(fill="x")

    def expire(self):
        self.master.switch_frame(WelcomeFrame)
        messagebox.showinfo("Photmatic", "Your trail has expired")

    def select_doc(self, path):
        self.photomatic_controller.photomatic_model.clear()
        if self.photomatic_controller.select_document(path) == 0:
            messagebox.showinfo("Photomatic", "No documents found")
        return self.photomatic_controller.photomatic_model

    def start(self):
        cmyk = True if self.start_frame.check_convert_cmyk.get() == 1 else False
        gender = Helper.find_gender(self.start_frame.cmb_gender.get())
        t_transform = Helper.find_textsetting(self.start_frame.cmb_text_transform.get())
        model = self.photomatic_controller.photomatic_model

        if model.is_empty():
            messagebox.showerror("Photomatic", "Please select document/s")

        elif Config.get_sc_resize_image() and not model.complete():
            messagebox.showerror("Photomatic", "Please select sizes for all documents")

        elif model.lineup == "":
            messagebox.showerror("Photomatic", "Please select a lineup")

        else:
            self.remarks_frame.reset_remarks()
            start_time = time.perf_counter()
            result = self.photomatic_controller.start(cmyk, t_transform, gender)
            self.remarks_frame.set_progress(1)
            self.remarks_frame.append_remarks(
                f"Execution time: {time.perf_counter()-start_time:0.2f} seconds\n",
            )
            self.remarks_frame.append_remarks("Remarks: ")
            self.remarks_frame.append_remarks(result)
            messagebox.showinfo("Success", "Done")


class HeaderFrame(ctk.CTkFrame):
    def __dir__(self):
        return " "

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.app_title = ctk.CTkLabel(
            self,
            text=Config.get_app_name(),
            font=ctk.CTkFont("Arial", 32, weight="bold", slant="italic"),
        )
        self.app_title.pack(side="right")


class RemarksFrame(ctk.CTkFrame):
    def __dir__(self):
        return " "

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.progress = ctk.CTkProgressBar(self, corner_radius=0)
        self.progress.pack(fill="x", pady=(0, 5))
        self.set_progress(0)

        self.remarks = ctk.CTkTextbox(
            self, width=820, corner_radius=0, state="disabled", font=("verdana", 15)
        )
        self.remarks.pack(fill="both")
        self.reset_remarks()

    def append_remarks(self, text):
        self.remarks.configure(state="normal")
        self.remarks.insert(ctk.END, f"{text}\n")
        self.remarks.see(ctk.END)
        self.remarks.configure(state="disabled")

    def set_progress(self, value: float):
        self.progress.set(value)

    def reset_remarks(self):
        self.clear_remarks()

        self.append_remarks("REMINDERS:")
        self.append_remarks(
            " - Don't click anything inside photoshop while the script is running"
        )
        self.append_remarks(
            " - Layers that you want to be changed by the csv should NOT be inside a group folder"
        )
        self.append_remarks(
            ' - Text transform doesn\'t always apply! e.g. when the layer has been set to "All Caps"\n'
        )

    def clear_remarks(self):
        self.remarks.configure(state="normal")
        self.remarks.delete("1.0", ctk.END)
        self.remarks.configure(state="disabled")


class MyComboboxFrame(ctk.CTkFrame):
    def __dir__(self):
        return " "

    def __init__(self, master, name, values, command=None):
        super().__init__(master, fg_color="transparent")
        self.values = values
        self.label = ctk.CTkLabel(self, text=name)
        self.label.pack(side="left", padx=(0, 5))

        self.combobox = ctk.CTkComboBox(
            self, values=values, state="readonly", command=command
        )
        self.combobox.pack(side="left")
        self.combobox.set(values[0])

    def configure(self, state):
        self.combobox.configure(state=state)

    def get(self):
        return self.combobox.get()

    def set(self, value):
        self.combobox.set(value)

    def reset(self):
        self.set(self.values[0])


class DatatableFrame(ctk.CTkFrame):
    def __dir__(self):
        return " "

    def __init__(self, master, app: PhotomaticWindowApp):
        super().__init__(master, fg_color="transparent")
        self.columnconfigure(1, weight=1)
        self.app = app

        self.btn_select_lineup = ctk.CTkButton(
            self, text="Select Lineup", command=self.select_lineup
        )
        self.btn_select_lineup.grid(row=0, column=0)

        self.text = StringVar(self, value=r"")

        self.txt_datatable_path = ctk.CTkEntry(
            self, state="readonly", textvariable=self.text
        )
        self.txt_datatable_path.grid(row=0, column=1, padx=(10, 0), sticky="we")

    def get(self):
        return self.text.get()

    def select_lineup(self):
        file_path = filedialog.askopenfilename(
            title="Select Spreadsheet File",
            filetypes=[("spreadsheet files", "*.csv *.xlsx")],
        )
        if file_path:
            self.app.photomatic_controller.select_lineup(file_path)
            self.text.set(file_path)


class OptionsAndStartFrame(ctk.CTkFrame):
    def __dir__(self):
        return " "

    def __init__(self, master, app: PhotomaticWindowApp):
        super().__init__(master, fg_color="transparent")
        self.app = app

        self.columnconfigure(index=(0, 1, 2, 3), weight=1)

        self.cmb_text_transform = MyComboboxFrame(
            self, "Text Transform", Helper.populate_textsettings()
        )
        self.cmb_text_transform.grid(row=0, column=0, sticky="w")

        self.cmb_gender = MyComboboxFrame(self, "Gender", Helper.populate_gender())
        self.cmb_gender.grid(row=0, column=1)

        self.cmyk = BooleanVar()
        self.check_convert_cmyk = ctk.CTkCheckBox(
            self, text="Convert image to CMYK", variable=self.cmyk
        )
        self.check_convert_cmyk.grid(row=0, column=2)

        self.btn_start = ctk.CTkButton(self, text="START", command=self.start)
        self.btn_start.grid(row=0, column=3, sticky="we")

    def start(self):
        self.app.start()


class ClothManagerFrame(ctk.CTkFrame):
    def __dir__(self):
        return " "

    def __init__(self, master, app: PhotomaticWindowApp):
        super().__init__(master, fg_color="#cfcfcf")
        self.app = app
        self.cloth_model_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cloth_model_frame.grid(row=0, column=0, sticky="we", pady=10)

        self.btn_selectpsd = ctk.CTkButton(
            self.cloth_model_frame,
            text="Select Document",
            command=self.select_document,
        )
        self.btn_selectpsd.pack(side="left", padx=10)

        self.btn_selectpsd = ctk.CTkButton(
            self.cloth_model_frame,
            text="Select Folder",
            command=self.select_documents,
        )
        self.btn_selectpsd.pack(side="left", padx=(0, 25))

        self.cmb_sizes = MyComboboxFrame(
            self.cloth_model_frame, "Sizes", Helper.populate_sizes(), self.select_sizes
        )
        self.cmb_sizes.pack(side="left")

        if Config.get_sc_resize_image() is False:
            self.cmb_sizes.configure("disabled")

        self.lbl_total = ctk.CTkLabel(self.cloth_model_frame, text="")
        self.lbl_total.pack(side="right", padx=(0, 10))
        self.clothes_frame = None

    def populate_document(self, clothes):
        self.remove_document()
        self.cmb_sizes.reset()
        self.clothes_frame = ClothesListFrame(
            self, clothes, self.app.photomatic_controller.photomatic_model
        )
        self.clothes_frame.grid(row=1, column=0)

    def remove_document(self):
        if self.clothes_frame is not None:
            self.clothes_frame.grid_forget()
            self.clothes_frame.destroy()

    def select(self, path):
        model = self.app.select_doc(path)
        if len(model.clothes) > 0:
            if Config.get_sc_resize_image():
                self.populate_document(model.get_designs())
            else:
                self.populate_document(model.get_choices())

    def select_document(self):
        file_path = filedialog.askopenfilename(
            title="Select Document", filetypes=[("Document Files", "*.psd *.tif *.crd")]
        )
        if file_path:
            self.select(file_path)

    def select_documents(self):
        folder_path = filedialog.askdirectory(title="Select Folder")
        if folder_path:
            self.select(folder_path)

    def select_sizes(self, value):
        if self.clothes_frame is None:
            return
        if self.clothes_frame.selected is None:
            return
        if value == "-- select size --":
            return

        model = self.app.photomatic_controller.photomatic_model
        current_cloth = model.find(self.clothes_frame.selected.get())
        if current_cloth is not None:
            current_cloth.sizes = rf"sizes/{value}.json"

    def update_total_items(self, amount):
        self.lbl_total.configure(text=f"total items: {amount}" if amount != 0 else "")


class ClothesListFrame(ctk.CTkScrollableFrame):
    def __dir__(self):
        return " "

    def __init__(self, master, clothes, model):
        if len(clothes) == 0:
            raise ValueError("no clothes selected")
        super().__init__(
            master,
            width=800,
            height=40,
            orientation="horizontal",
            fg_color="transparent",
        )
        self.handler = master
        self.photomatic_model = model
        self.clothes = []
        self.selected = None

        self.create(clothes)
        self.handler.update_total_items(self.count())

    def count(self):
        return len(self.clothes)

    def create(self, clothes):
        for idx, cloth in enumerate(clothes):
            cloth_widget = ClothFrame(self, cloth)
            cloth_widget.grid(row=0, column=idx, padx=5)
            self.clothes.append(cloth_widget)

        first_item = self.clothes[0]
        self.selected = first_item
        first_item.select()

    def is_empty(self):
        return self.count() == 0

    def print(self):
        print("CLOTHES")
        for cloth in self.clothes:
            print(cloth.get())

    def select(self, selected):
        current_clothes = self.photomatic_model.find(selected.get())
        if Config.get_sc_resize_image() is True:
            if current_clothes.sizes != "":
                self.handler.cmb_sizes.set(current_clothes.sizes[6:-5])
            else:
                self.handler.cmb_sizes.reset()
        self.selected = selected
        for cloth in self.clothes:
            if cloth != self.selected:
                cloth.deselect()

    def remove(self, cloth):
        current = cloth.get()
        if str(current).endswith((".tif", ".psd")):
            model = self.photomatic_model.find(current)
            self.photomatic_model.remove(current, model.design.name)
        else:
            model_names = self.photomatic_model.get_all_design_name(current)
            self.photomatic_model.remove(current, model_names)

        self.clothes.remove(cloth)
        self.handler.update_total_items(self.count())

        if self.is_empty():
            self.grid_forget()


class ClothFrame(ctk.CTkFrame):
    def __dir__(self):
        return " "

    def __init__(self, master: ClothesListFrame, name):
        # selected fg_color = #6e7174
        super().__init__(master, fg_color="#979da2", cursor="hand2")
        self.master_handler = master

        self.lbl_name = ctk.CTkLabel(self, text=name)
        self.lbl_name.grid(row=0, column=0, padx=(10, 0), pady=5)
        self.lbl_name.bind("<Button-1>", self.on_click)

        self.btn_remove = ctk.CTkButton(
            self,
            text="",
            image=PhotoImage(file=r"res/remove.png"),
            fg_color="transparent",
            hover=False,
            width=20,
            command=self.remove,
        )
        self.btn_remove.grid(row=0, column=1, padx=2)

        self.bind("<Button-1>", self.on_click)

    def deselect(self):
        self.configure(fg_color="#979da2")

    def get(self):
        return self.lbl_name.cget("text")

    # event is needed in this method
    def on_click(self, event):
        self.master_handler.select(self)
        self.select()

    def remove(self):
        result = messagebox.askyesno(
            title="Photomatic - Remove Document?",
            message=f"Are you sure you want to remove {self.lbl_name.cget('text')}",
        )

        if not result:
            return

        self.master_handler.remove(self)
        self.grid_forget()
        self.destroy()

    def select(self):
        self.configure(fg_color="#6e7174")
