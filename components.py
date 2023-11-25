from tkinter import messagebox
from tkinter import StringVar
from tkinter import ttk
import customtkinter as ctk


def __dir__():
    return " "


class MyComboboxFrame(ctk.CTkFrame):
    def __dir__(self):
        return " "

    def __init__(self, master, name, values, command=None, width=140):
        super().__init__(master, fg_color="transparent")
        self.values = values
        self.label = ctk.CTkLabel(self, text=name)
        self.label.pack(side="left", padx=(0, 5))

        self.combobox = ctk.CTkComboBox(
            self, values=values, state="readonly", command=command, width=width
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


class MyDataGridView(ctk.CTkFrame):
    def __dir__(self):
        return " "

    def __init__(self, master, column_config, items):
        super().__init__(master)

        columns = []
        for col_conf in column_config:
            columns.append(col_conf["name"])

        self.dgv = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        self.dgv.pack()

        for col_conf in column_config:
            name = col_conf["name"]
            text = col_conf["text"]
            width = col_conf["width"]
            anchor = col_conf["anchor"]
            self.__configure_column(name, text, width, anchor)

        self.dgv.bind("<Delete>", lambda e: self.delete_row())

        self.populate(items)

    def bind_select_event(self, func):
        self.dgv.bind("<<TreeviewSelect>>", lambda e: self.select(func))

    def __configure_column(
        self, name, text: str | None, width=75, anchor: str | None = None
    ):
        self.dgv.column(
            name, width=width, anchor="center" if anchor is None else anchor  # type: ignore
        )
        self.dgv.heading(name, text=text if text is not None else name.capitalize())

    def delete_row(self):
        item = self.get_selected_item()
        if item is not None and messagebox.askyesno(
            "Photomatic", "Are you sure you want to remove item?"
        ):
            self.dgv.delete(item)

    def deselect_row(self):
        item = self.get_selected_item()

        if item is not None:
            self.dgv.selection_remove(item)

    def get_all(self):
        for children in self.dgv.get_children():
            yield self.__get_item_values(children)

    def __get_item_values(self, item):
        return self.dgv.item(item, "values")

    def get_selected_item(self):
        return self.dgv.selection()[0] if len(self.dgv.selection()) > 0 else None

    def get_selected_values(self):
        item = self.get_selected_item()
        if item is None:
            return None
        return self.__get_item_values(item)

    def insert(self, value):
        self.dgv.insert("", ctk.END, values=value)

    def populate(self, items):
        for item in items:
            item_list = list()
            if isinstance(item, dict):
                for key, value in item.items():
                    item_list.append(value)
            elif isinstance(item, list):
                for i in item:
                    item_list.append(i)
            self.insert(item_list)

    def select(self, func):
        func()

    def update_row(self, item, value):
        self.dgv.item(item, values=value)
        self.dgv.selection_remove(item)


class MyTextBoxFrame(ctk.CTkFrame):
    def __init__(self, master, label_name, text_value="", width=140):
        super().__init__(master, fg_color="transparent")

        self.lbl_name = ctk.CTkLabel(self, text=label_name)
        self.lbl_name.pack(side="left", padx=(0, 5))
        self.value = StringVar(self, text_value)
        self.txt_value = ctk.CTkEntry(self, textvariable=self.value, width=width)
        self.txt_value.pack(side="left")

    def delete(self):
        self.value.set("")

    def get(self):
        return self.value.get()

    def set(self, value):
        self.value.set(value)
