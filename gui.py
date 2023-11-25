# dependency modules
import time
import tkinter as tk
from pathlib import Path
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
from components import MyComboboxFrame
from components import MyDataGridView
from components import MyTextBoxFrame
from configuration import Config
from configuration import SettingsManager
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

    def clear(self):
        self.photomatic_controller.model.clear()

    def expire(self):
        self.master.switch_frame(WelcomeFrame)
        messagebox.showinfo("Photmatic", "Your trail has expired")

    def select_doc(self, path):
        self.clear()
        if self.photomatic_controller.select_document(path) == 0:
            messagebox.showinfo("Photomatic", "No documents found")
        return self.photomatic_controller.model

    def start(self):
        cmyk = True if self.start_frame.check_convert_cmyk.get() == 1 else False
        gender = Helper.find_gender(self.start_frame.cmb_gender.get())
        t_transform = Helper.find_textsetting(self.start_frame.cmb_text_transform.get())
        model = self.photomatic_controller.model

        if model.is_empty():
            messagebox.showerror("Photomatic", "Please select document/s")

        elif Config.get_resize_image() and not model.complete():
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


class SettingsTopLevel(ctk.CTkToplevel):
    def __dir__(self):
        return " "

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Photomatic")
        self.resizable(False, False)
        self.grab_set()
        self.settings = SettingsManager()
        padding_y = (0, 10)

        self.app = ctk.CTkFrame(self, fg_color="transparent")
        self.app.pack(pady=20, padx=20)
        self.app_name = MyTextBoxFrame(
            self.app, "Application Name:", "PHOTOMATIC", width=200
        )
        self.app_name.pack(padx=(7, 0), pady=padding_y)
        self.ps_version = MyComboboxFrame(
            self.app,
            "Photoshop Version:",
            ["auto-detect", "2023", "2022", "2021", "2020", "2019", "2018", "2017"],
            width=200,
        )
        self.ps_version.pack(pady=padding_y)
        self.check_resize_image = ctk.CTkCheckBox(self.app, text="Resize Image")
        self.check_resize_image.pack(pady=padding_y)
        self.check_close_document = ctk.CTkCheckBox(
            self.app, text="Close document/s after finishing the operation"
        )
        self.check_close_document.pack(pady=padding_y)
        self.btn_save = ctk.CTkButton(self.app, text="SAVE", command=self.save)
        self.btn_save.pack(pady=10)
        self.btn_exit = ctk.CTkButton(
            self.app,
            text="EXIT",
            fg_color="#BA1A20",
            hover_color="#871216",
            command=self.exit,
        )
        self.btn_exit.pack(pady=(0, 10))

        self.lbl_note = ctk.CTkLabel(
            self,
            text="Note: you need to restart the app to apply changes.",
        )
        self.lbl_note.pack(pady=padding_y, padx=20)

        self.app_name.set(Config.get_app_name())

        version = Config.get_ps_version()
        self.ps_version.set(version if version is not None else "auto-detect")

        if Config.get_resize_image():
            self.check_resize_image.select()
        if Config.get_close_document():
            self.check_close_document.select()

        self.protocol("WM_DELETE_WINDOW", self.save)

    def exit(self):
        self.destroy()

    def save(self):
        answer = messagebox.askyesnocancel("Photomatic", "Do you want to save changes?")
        if answer == ctk.YES:
            self.settings.set_application_name(self.app_name.get())
            self.settings.set_ps_version(self.ps_version.get())
            self.settings.set_resize_image(
                True if self.check_resize_image.get() == 1 else False
            )
            self.settings.set_close_document(
                True if self.check_close_document.get() == 1 else False
            )
            self.settings.save()
            self.destroy()
        elif answer == ctk.NO:
            self.destroy()


class ClothesManagerTopLevel(ctk.CTkToplevel):
    def __dir__(self):
        return " "

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Photomatic")
        self.resizable(False, False)
        self.grab_set()

        self.margin_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.margin_frame.pack(padx=20, pady=20)

        self.manager_frame = None

        if Config.get_resize_image() is True:
            self.manager_frame = ClothesManagerResizeFrame(self.margin_frame)
            self.manager_frame.pack()
        else:
            self.manager_frame = ClothesManagerNoResizeFrame(self.margin_frame)
            self.manager_frame.pack()


class ClothesManagerNoResizeFrame(ctk.CTkFrame):
    def __dir__(self):
        return " "

    def __init__(self, master):
        super().__init__(master)

        self.lbl_clothes_name = ctk.CTkLabel(
            self,
            text="SIZE MANAGER",
            font=ctk.CTkFont("Arial", 25, weight="bold"),
        )
        self.lbl_clothes_name.grid(
            row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 0)
        )

        self.settings_path = "settings/settings.json"
        self.json = Helper.extract_json(self.settings_path, "settings")
        sizes = self.json["size_config"]["sizes"]

        column_config = self.get_column_configuration()

        self.dgv = MyDataGridView(self, column_config, sizes)
        self.dgv.bind_select_event(self.select)

        self.dgv.grid(row=1, column=0, padx=20, pady=(10, 20))

        self.edit_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.edit_frame.grid(row=1, column=1, padx=(0, 20), pady=(10, 0), sticky="n")

        self.txt_shortsize = MyTextBoxFrame(self.edit_frame, "Shortsize:")
        self.txt_shortsize.grid(row=0, column=0, pady=(0, 5), sticky="e")

        self.txt_size = MyTextBoxFrame(self.edit_frame, "Size (optional):")
        self.txt_size.grid(row=1, column=0, pady=(0, 5), sticky="e")

        self.btn_update = ctk.CTkButton(
            self.edit_frame, text="ADD", command=self.update_or_add
        )
        self.btn_update.grid(row=4, pady=(0, 5), column=0, sticky="e")

        self.btn_cancel = ctk.CTkButton(
            self.edit_frame, text="CANCEL", state="disabled", command=self.cancel
        )
        self.btn_cancel.grid(row=5, pady=(0, 5), column=0, sticky="e")

        self.btn_remove = ctk.CTkButton(
            self.edit_frame,
            text="REMOVE",
            fg_color="#BA1A20",
            hover_color="#871216",
            command=self.delete,
        )
        self.btn_remove.grid(row=6, column=0, sticky="e")

        self.option_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.option_frame.grid(
            row=2, column=0, columnspan=2, sticky="w", padx=(20, 0), pady=(0, 20)
        )

        self.btn_save = ctk.CTkButton(self.option_frame, text="SAVE", command=self.save)
        self.btn_save.pack(side="left", padx=(0, 10))

        self.btn_exit = ctk.CTkButton(
            self.option_frame,
            text="EXIT",
            fg_color="#BA1A20",
            hover_color="#871216",
            command=self.exit,
        )
        self.btn_exit.pack(side="left")

    def cancel(self):
        self.dgv.deselect_row()

    def clear_entries(self):
        self.txt_shortsize.delete()
        self.txt_size.delete()

    def delete(self):
        self.dgv.delete_row()

    def exit(self):
        if self.master.master is None:
            return
        self.master.master.destroy()

    def get_column_configuration(self):
        column_config = list()
        column_config.append(
            {"name": "shortsize", "text": None, "width": 95, "anchor": None}
        )
        column_config.append(
            {"name": "size", "text": None, "width": 95, "anchor": None}
        )

        return column_config

    def get_entry_values(self):
        return (
            self.txt_shortsize.get(),
            self.txt_size.get(),
        )

    def select(self):
        self.clear_entries()

        values = self.dgv.get_selected_values()
        if values is None:
            self.btn_cancel.configure(state="disabled")
            self.btn_update.configure(text="ADD")
            return
        else:
            self.btn_cancel.configure(state="normal")
            self.btn_update.configure(text="UPDATE")

        self.txt_shortsize.set(values[0])
        if len(values) > 1:
            self.txt_size.set(values[1])

    def save(self):
        answer = messagebox.askyesnocancel(
            "Photomatic", "Do you want to save changes?", icon=messagebox.WARNING
        )
        if answer is None:
            return
        if answer == ctk.YES:
            sizes_list = []
            for values in self.dgv.get_all():
                values = [value for value in values if value != ""]
                sizes_list.append(values)

            self.json["size_config"]["sizes"] = sizes_list
            Helper.set_json(self.settings_path, self.json)
        self.exit()

    def add_size(self):
        values = self.get_entry_values()
        self.dgv.insert(values)
        self.clear_entries()

    def update_size(self, item):
        item = self.dgv.get_selected_item()
        values = self.get_entry_values()
        self.dgv.update_row(item, values)
        self.dgv.deselect_row()

    def update_or_add(self):
        item = self.dgv.get_selected_item()
        if self.validate_entries() is False:
            return

        if item is None:
            self.add_size()
        else:
            self.update_size(item)

    def validate_entries(self):
        validate = False
        if self.txt_shortsize.get() == "":
            messagebox.showerror("Photomatic", "Please input a shortsize")
        else:
            validate = True

        return validate


class ClothesManagerResizeFrame(ctk.CTkFrame):
    def __dir__(self):
        return " "

    def __init__(self, master):
        super().__init__(master)
        self.rowconfigure(index=(0, 2), weight=0)
        self.rowconfigure(index=1, weight=1)

        self.txt_name = MyTextBoxFrame(self, "Name:", width=160)
        self.txt_name.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
        my_list = Helper.populate_sizes()

        self.clothes_list = tk.Listbox(
            self, activestyle="none", height=12, font=("verdana", 12)
        )
        self.clothes_list.grid(
            row=1, column=0, sticky="ew", rowspan=2, padx=20, pady=(0, 20)
        )
        self.clothes_list.configure(
            highlightbackground="#979da2",
            highlightthickness=2,
        )
        for list in my_list:
            self.clothes_list.insert(ctk.END, list)

        self.option_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.option_frame.grid(
            row=0, column=1, rowspan=2, sticky="n", padx=20, pady=(20, 0)
        )

        self.btn_add = ctk.CTkButton(self.option_frame, text="ADD", command=self.add)
        self.btn_add.pack(pady=(0, 5))
        self.btn_open = ctk.CTkButton(self.option_frame, text="OPEN", command=self.open)
        self.btn_open.pack(pady=(0, 5))
        self.btn_delete = ctk.CTkButton(
            self.option_frame,
            text="DELETE",
            fg_color="#BA1A20",
            hover_color="#871216",
            command=self.delete,
        )
        self.btn_delete.pack(pady=(0, 5))

        self.btn_done = ctk.CTkButton(self, text="DONE", command=self.done)
        self.btn_done.grid(row=2, column=1, pady=(0, 20))

    def add(self):
        file_name = self.txt_name.get()
        if file_name == "":
            return

        if file_name in Helper.populate_sizes():
            messagebox.showinfo(
                "Photomatic", f"{file_name} already exist, please choose another name."
            )
            return

        template = Helper.extract_json("sizes/template.json", "template")
        path = Helper.get_size_path(file_name)
        Helper.set_json(path, template)

        self.clothes_list.insert(ctk.END, file_name)
        self.txt_name.delete()

    def delete(self):
        item = self.get_selected()

        if item is None:
            return

        item_name = self.clothes_list.get(item)

        if messagebox.askyesno(
            "Photomatic",
            f"Are you sure you want to delete this item: {item_name}?\nThis process cannot be undone.",
        ):
            path = Path(Helper.get_size_path(item_name))
            path.unlink(missing_ok=True)
            self.clothes_list.delete(item)

    def done(self):
        if self.master.master is None:
            return
        self.master.master.destroy()

    def get_selected(self):
        return (
            self.clothes_list.curselection()[0]
            if len(self.clothes_list.curselection()) > 0
            else None
        )

    def open(self):
        item = self.get_selected()
        if item is None:
            return

        item_name = self.clothes_list.get(item)
        dialog = ClothesEditorTopLevel(size_path=Helper.get_size_path(item_name))
        self.wait_window(dialog)
        self.lift()
        self.grab_set()


class ClothesEditorTopLevel(ctk.CTkToplevel):
    def __dir__(self):
        return " "

    def __init__(self, size_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Photomatic")
        self.resizable(False, False)
        self.grab_set()
        self.size_path = size_path

        self.lbl_clothes_name = ctk.CTkLabel(
            self,
            text=f"{str(size_path[6:-5]).upper()}",
            font=ctk.CTkFont("Arial", 25, weight="bold"),
        )
        self.lbl_clothes_name.grid(
            row=0, column=0, columnspan=2, sticky="w", padx=(20, 0), pady=(20, 0)
        )

        self.size_path = size_path
        self.json = Helper.extract_json(size_path, "cloth size file")
        sizes = self.json["sizes"]

        column_config = self.get_column_configuration()

        self.dgv = MyDataGridView(self, column_config, sizes)
        self.dgv.bind_select_event(self.select)
        self.dgv.grid(row=1, column=0, padx=20, pady=(10, 20))

        self.edit_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.edit_frame.grid(row=1, column=1, padx=(0, 20), pady=(10, 0), sticky="n")

        self.txt_size = MyTextBoxFrame(self.edit_frame, "Size:")
        self.txt_size.grid(row=0, column=0, pady=(0, 5), sticky="e")

        self.txt_width = MyTextBoxFrame(self.edit_frame, "Width:")
        self.txt_width.grid(row=1, column=0, pady=(0, 5), sticky="e")

        self.txt_height = MyTextBoxFrame(self.edit_frame, "Height:")
        self.txt_height.grid(row=2, column=0, pady=(0, 5), sticky="e")

        self.txt_shortsize = MyTextBoxFrame(self.edit_frame, "Shortsize:")
        self.txt_shortsize.grid(row=3, column=0, pady=(0, 5), sticky="e")

        self.btn_update = ctk.CTkButton(
            self.edit_frame, text="ADD", command=self.update_or_add
        )
        self.btn_update.grid(row=4, pady=(0, 5), column=0, sticky="e")

        self.btn_cancel = ctk.CTkButton(
            self.edit_frame, text="CANCEL", state="disabled", command=self.cancel
        )
        self.btn_cancel.grid(row=5, pady=(0, 5), column=0, sticky="e")

        self.btn_remove = ctk.CTkButton(
            self.edit_frame,
            text="REMOVE",
            fg_color="#BA1A20",
            hover_color="#871216",
            command=self.delete,
        )
        self.btn_remove.grid(row=6, column=0, sticky="e")

        self.option_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.option_frame.grid(row=2, column=0, sticky="w", padx=(20, 0), pady=(0, 20))

        self.btn_save = ctk.CTkButton(self.option_frame, text="SAVE", command=self.save)
        self.btn_save.pack(side="left", padx=(0, 10))

        self.btn_exit = ctk.CTkButton(
            self.option_frame,
            text="EXIT",
            fg_color="#BA1A20",
            hover_color="#871216",
            command=self.exit,
        )
        self.btn_exit.pack(side="left")

        self.protocol("WM_DELETE_WINDOW", self.save)

    def cancel(self):
        self.dgv.deselect_row()

    def clear_entries(self):
        self.txt_size.delete()
        self.txt_width.delete()
        self.txt_height.delete()
        self.txt_shortsize.delete()

    def delete(self):
        self.dgv.delete_row()

    def exit(self):
        self.destroy()

    def get_column_configuration(self):
        column_config = list()
        column_config.append(
            {"name": "name", "text": "Size", "width": 150, "anchor": "w"}
        )
        column_config.append(
            {"name": "width", "text": None, "width": 75, "anchor": None}
        )
        column_config.append(
            {"name": "height", "text": None, "width": 75, "anchor": None}
        )
        column_config.append(
            {
                "name": "shortsize",
                "text": "Shortsize (optional)",
                "width": 115,
                "anchor": None,
            }
        )
        return column_config

    def get_entry_values(self):
        return (
            self.txt_size.get(),
            self.txt_width.get(),
            self.txt_height.get(),
            self.txt_shortsize.get(),
        )

    def select(self):
        self.clear_entries()

        values = self.dgv.get_selected_values()
        if values is None:
            self.btn_cancel.configure(state="disabled")
            self.btn_update.configure(text="ADD")
            return
        else:
            self.btn_cancel.configure(state="normal")
            self.btn_update.configure(text="UPDATE")

        self.txt_size.set(values[0])
        self.txt_width.set(values[1])
        self.txt_height.set(values[2])
        self.txt_shortsize.set(values[3])

    def save(self):
        answer = messagebox.askyesnocancel(
            "Photomatic", "Do you want to save changes?", icon=messagebox.WARNING
        )
        if answer is None:
            return
        if answer == ctk.YES:
            sizes_list = []
            for values in self.dgv.get_all():
                size = {}
                size["name"] = values[0]
                size["width"] = Helper.parse_number(values[1])
                size["height"] = Helper.parse_number(values[2])
                size["shortsize"] = values[3]
                sizes_list.append(size)
            self.json["sizes"] = sizes_list

            Helper.set_json(self.size_path, self.json)
        self.destroy()

    def add_size(self):
        values = self.get_entry_values()
        self.dgv.insert(values)
        self.clear_entries()

    def update_size(self, item):
        values = self.get_entry_values()
        self.dgv.update_row(item, values)
        self.dgv.deselect_row()

    def update_or_add(self):
        item = self.dgv.get_selected_item()
        if self.validate_entries() is False:
            return

        if item is None:
            self.add_size()
        else:
            self.update_size(item)

    def validate_entries(self):
        validate = False
        width = self.txt_width.get()
        height = self.txt_height.get()
        width_num = Helper.try_parse(width)
        height_num = Helper.try_parse(height)
        if self.txt_size.get() == "":
            messagebox.showerror("Photomatic", "Please input a size")
        elif width == "":
            messagebox.showerror("Photomatic", "Please input a width")
        elif width_num is None:
            messagebox.showerror("Photomatic", "Width must be a number")
        elif width_num <= 0:
            messagebox.showerror("Photomatic", "Width must be more than 0")
        elif height == "":
            messagebox.showerror("Photomatic", "Please input a height")
        elif height_num is None:
            messagebox.showerror("Photomatic", "Height must be a number")
        elif height_num <= 0:
            messagebox.showerror("Photomatic", "Height must be more than 0")
        else:
            validate = True

        return validate


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

        self.btn_settings = ctk.CTkButton(
            self,
            text="",
            command=self.open_settings,
            width=25,
            fg_color="transparent",
            hover=False,
            image=PhotoImage(file=r"res/settings.png"),
        )
        self.btn_settings.pack(side="left")

        self.btn_manage_sizes = ctk.CTkButton(
            self,
            text="Manage Sizes",
            fg_color="#6e7174",
            hover_color="#6e7174",
            command=self.open_clothes_manager,
        )
        self.btn_manage_sizes.pack(side="left")

    def open_clothes_manager(self):
        clothes_manager = ClothesManagerTopLevel()
        self.master.wait_window(clothes_manager)

    def open_settings(self):
        settings = SettingsTopLevel()
        self.master.wait_window(settings)
        Config.refresh()


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
        self.columnconfigure(index=0, weight=1)
        self.margin_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.margin_frame.grid(row=0, column=0, sticky="we", pady=10)

        self.btn_select_document = ctk.CTkButton(
            self.margin_frame,
            text="Select Document",
            command=self.select_document,
        )
        self.btn_select_document.pack(side="left", padx=(14, 10))

        self.btn_select_folder = ctk.CTkButton(
            self.margin_frame,
            text="Select Folder",
            command=self.select_documents,
        )
        self.btn_select_folder.pack(side="left", padx=(0, 25))

        self.cmb_sizes = MyComboboxFrame(
            self.margin_frame,
            "Sizes",
            Helper.populate_sizes("-- select size --"),
            self.select_sizes,
        )
        self.cmb_sizes.pack(side="left")

        if Config.get_resize_image() is False:
            self.cmb_sizes.configure("disabled")

        self.btn_clear = ctk.CTkButton(
            self.margin_frame,
            text="Clear",
            fg_color="#6e7174",
            hover_color="#6e7174",
            width=100,
            command=self.clear,
        )
        self.btn_clear.pack(side="right", padx=(0, 14))

        self.lbl_total = ctk.CTkLabel(self.margin_frame, text="")
        self.lbl_total.pack(side="right", padx=(0, 10))
        self.clothes_frame = None

    def clear(self):
        self.remove_document()
        self.cmb_sizes.reset()
        self.app.clear()
        self.update_total_items(0)

    def populate_document(self, clothes):
        self.remove_document()
        self.cmb_sizes.reset()
        self.clothes_frame = ClothesListFrame(
            self, clothes, self.app.photomatic_controller.model
        )
        self.clothes_frame.grid(row=1, column=0)

    def remove_document(self):
        if self.clothes_frame is not None:
            self.clothes_frame.grid_forget()
            self.clothes_frame.destroy()

    def select(self, path):
        model = self.app.select_doc(path)
        if len(model.clothes) > 0:
            if Config.get_resize_image():
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

        model = self.app.photomatic_controller.model
        current_cloth = model.find(self.clothes_frame.selected.get())
        if current_cloth is not None:
            current_cloth.sizes = Helper.get_size_path(value)

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
        if Config.get_resize_image() is True:
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
