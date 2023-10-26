# dependency modules
from pathlib import Path

# custom modules
from configuration import Config
from data import PandasDataTable
from enumeration import TextSettings
from sizes import ClothSizes
from utils import Helper
from workspace import PhotoshopWorkspace


def __dir__():
    return " "


class PhotomaticPro:
    def __dir__(self):
        return " "

    def __init__(self) -> None:
        self._app = None
        self._clothing = None
        self._data = None

    def _change_doc_size(self, size_name) -> bool:
        if self._app is None:
            raise TypeError("App is None")
        if self._clothing is None:
            raise TypeError("Clothing is None")

        size_found = False
        size = self._clothing.get_size(size_name)
        if size is not None:
            self._app.resize_image(size.width, size.height)
            size_found = True
        return size_found

    def _check_parameter_error(self):
        if self._app is None:
            raise TypeError("App is None")

        error = set()
        for layer in self._app.iterate_layers():
            layer_name = layer.name.split()

            if len(layer_name) == 1:
                continue

            is_param_error = (
                True if self._app.get_max_length(layer_name[1]) is None else False
            )
            if is_param_error and layer.name not in error:
                error.add(layer.name)

        if len(error) > 0:
            return error

    def _create_fileformat(self, row):
        # OPTIMIZE THIS, IT UNEFFICIENTLY CALLING OVER AND OVER AGAIN...
        if self._data is None:
            raise TypeError("Data is none")

        file_info = []
        for ecol in self._get_fileformat_columns():
            ecol_value = self._data.at(row, ecol)
            if not self._data.is_empty(ecol_value):
                file_info.append(ecol_value.replace(".", ""))

        file_name = "_".join(file_info)
        return file_name

    def _create_filepath(self, folder_path, row_num, file_row_names):
        # create create file path
        path = rf"{folder_path}\{row_num}"
        if file_row_names != "":
            path += f"- {file_row_names}"

        return path

    def _create_folderpath(self):
        if self._app is None:
            raise TypeError("App is None")

        psd_name = self._app.document_name
        folder_path = (
            rf"{str(Path(self._app.document_fullname).parent)}\{psd_name[:-4]}"
        )

        if Config.get_sc_resize_image() is True:
            folder_path += f" - {self._clothing.name}"  # type: ignore

        return folder_path

    def _create_outputfolder(self, folder_path):
        Path(folder_path).mkdir(exist_ok=True)

    def _get_fileformat_columns(self):
        # THIS CAN BE CACHED?
        if self._data is None:
            raise TypeError("Data is none")

        format_col = ["name", "size", Config.get_np_number_preference()]
        existing_col = []
        for fcol in format_col:
            if self._data.does_column_exist(fcol):
                existing_col.append(fcol)
        return existing_col

    def initialize_components(
        self,
        workspace_path: str,
        datatable_path: str,
        clothing_path: str,
        text_settings: TextSettings = TextSettings.DEFAULT,
    ):
        try:
            self._open_workspace(workspace_path)
            self._open_sizes(clothing_path)
            self._open_datatable(datatable_path)
            self._transform_datatable(text_settings)
        except Exception as e:
            return repr(e)
        return ""

    def print_df(self):
        if self._data is None:
            raise TypeError("Data is None")
        self._data.print()

    def print_layers(self):
        if self._app is None:
            raise TypeError("App is None")
        self._app.print()

    def print_sizes(self):
        if self._clothing is None:
            raise TypeError("Clothing is None")
        self._clothing.print()

    def _open_datatable(self, datatable_path):
        if self._app is None:
            raise TypeError("App is None")
        self._data = PandasDataTable(
            datatable_path, encoding=Config.get_character_encoding()
        )
        if Config.get_sc_resize_image() is False:
            condition = Helper.get_size_condition(
                self._app.document_name
            )  # side effect if activedocument isn't the right one
            self._data.filter_isin("size", condition)

    def _open_sizes(self, file_path: str):
        if Config.get_sc_resize_image() is False:
            return

        clothing_name = file_path[6:-5]
        self._clothing = ClothSizes(ClothSizes.read_clothing(file_path), clothing_name)

    def _open_workspace(self, path):
        # I THINK I NEED A BUILDER CLASS HERE...
        self._app = PhotoshopWorkspace(
            version=Config.get_ps_version(),
            ruler_unit=Config.get_rulerunit_preference(),
            image_quality=Config.get_jpg_quality(),
        )
        self._app.open(path)

    def start(self, convert_cmyk=False, progress_callback=False):
        if self._app is None:
            raise TypeError("App is None")
        if Config.get_sc_resize_image() is True and self._clothing is None:
            raise TypeError("Clothing is None")
        if self._data is None:
            raise TypeError("Data is None")

        log = ""
        d_row, d_col = None, None
        try:
            folder_path = self._create_folderpath()
            self._create_outputfolder(folder_path)

            error = self._check_parameter_error()
            if error is not None:
                log += f"Parameter invalid in these layers: {error}\n"

            self._app.create_document_placeholder()

            # to avoid calling this over and over again, this is O(N) btw not O(1) where N is columns
            idx_exist = self._data.does_column_exist("index")

            for row in self._data.iterate_rows():
                self._app.save_state()

                row_idx = row[0]
                d_row = row_idx
                row_num = (row[1][0] if idx_exist else row_idx) + 1  # type: ignore

                for col, cell in row[1].items():
                    if col == "index":
                        continue
                    d_col = col
                    self._app.fill_layers(col, cell)  # type: ignore

                if (
                    Config.get_sc_resize_image() is True
                    and self._data.does_column_exist("size")
                ):
                    size = self._data.at(row_idx, "size")
                    if not self._data.is_empty(size):
                        shortsize = self._clothing.get_shortsize(size)  # type: ignore
                        if shortsize is not None:
                            self._app.fill_layers("shortsize", shortsize)

                    size_found = self._change_doc_size(size)
                    if size_found is False:
                        log += f"picture #{row_num} size not found\n"

                # create file
                file_format = self._create_fileformat(row_idx)
                path = self._create_filepath(folder_path, row_num, file_format)
                self._app.save_as(path)

                self._app.revert_state()

                if convert_cmyk:
                    self._app.convert_cmyk(path)

            self._app.close()
        except Exception as e:
            log += repr(e)
            if d_row is not None and d_col is not None:
                log += f"Stopped at column: {d_col} row: {d_row} cell: {self._data.at(d_row, d_col)}"
        return log

    def _transform_datatable(self, text_setting=TextSettings.DEFAULT):
        if self._data is None:
            raise TypeError("Data is None")
        if text_setting == TextSettings.DEFAULT:
            return
        elif text_setting == TextSettings.UPPERCASE:
            self._data.transform(lambda s: s.upper() if isinstance(s, str) else s)
        elif text_setting == TextSettings.LOWERCASE:
            self._data.transform(lambda s: s.lower() if isinstance(s, str) else s)
        elif text_setting == TextSettings.CAPITALIZE:
            self._data.transform(lambda s: s.capitalize() if isinstance(s, str) else s)
