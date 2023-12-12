# dependency modules
import os
from pathlib import Path

# custom modules
from configuration import Config
from data import PandasDataTable
from enumeration import Gender
from enumeration import TextSettings
from sizes import ClothSizes
from utils import Helper
from workspace import PhotoshopWorkspace


def __dir__():
    return " "


class PhotomaticCoreEngine:
    def __dir__(self):
        return " "

    def __init__(self, resize_image: bool | None = None) -> None:
        self.resize_image = (
            resize_image if resize_image is not None else Config.get_resize_image()
        )
        self.__workspace = None
        self.__datatable = None
        self.__cloth_sizes = None

        self.__project_name = None
        self.__output_path = None

    @property
    def cloth_sizes(self) -> ClothSizes | None:
        return self.__cloth_sizes

    @cloth_sizes.setter
    def cloth_sizes(self, value: str):
        self.__cloth_sizes = ClothSizes(value)

    @property
    def datatable(self) -> PandasDataTable | None:
        return self.__datatable

    @datatable.setter
    def datatable(self, value):
        self.__datatable = PandasDataTable(
            value, encoding=Config.get_character_encoding()
        )

    @property
    def output_path(self) -> str | None:
        return self.__output_path

    @output_path.setter
    def output_path(self, value):
        self.__output_path = value

    @property
    def project_name(self) -> str | None:
        return self.__project_name

    @project_name.setter
    def project_name(self, value):
        self.__project_name = value

    @property
    def resize_image(self) -> bool:
        return self._resize_image

    @resize_image.setter
    def resize_image(self, value: bool):
        self._resize_image = value

    # [todo] ps_workspace -> interface workspace
    @property
    def workspace(self) -> PhotoshopWorkspace | None:
        return self.__workspace

    @workspace.setter
    def workspace(self, value):
        self.__workspace = value

    # METHODS
    def __change_doc_size(self, size_name) -> bool:
        if self.workspace is None:
            raise TypeError("App is None")
        if self.cloth_sizes is None:
            raise TypeError("Cloth sizes is None")

        size = self.cloth_sizes.get_size(size_name)

        if size is not None:
            self.workspace.resize_image(size.width, size.height)
            return True

        return False

    def __check_parameter_error(self):
        if self.workspace is None:
            raise TypeError("App is None")
        if self.datatable is None:
            raise TypeError("Data is None")

        error = set()
        for layer in self.workspace.iterate_layers():
            layer_name = layer.name.split()

            if len(layer_name) == 1:
                continue

            is_param_error = (
                True
                if layer_name[0] in self.datatable.columns
                and self.workspace.get_max_length(layer_name[1]) is None
                else False
            )
            if is_param_error and layer.name not in error:
                error.add(layer.name)

        if len(error) > 0:
            return error

    def __create_filename(self, item_number, item_name):
        if self.workspace is None:
            raise TypeError("App is None")

        file_name = ""
        if Config.get_fn_folder_name() is True:
            file_name += f"{self.project_name} - "

        file_name += f"#{item_number} - "
        if item_name != "":
            file_name += f"{item_name}"

        if Config.get_fn_document_name() is True:
            file_name += f" - {self.workspace.get_document_name()}"

        return file_name

    def __create_fullname(self, folder_path, file_name):
        path = rf"{folder_path}\{file_name}"

        return path

    def __create_itemname(self, row):
        # OPTIMIZE THIS, IT UNEFFICIENTLY CALLING OVER AND OVER AGAIN...
        if self.datatable is None:
            raise TypeError("Datatable is None")

        file_info = []
        for ecol in self.__get_fileformat_columns():
            ecol_value = self.datatable.at(row, ecol)
            if not self.datatable.is_na(ecol_value):
                file_info.append(ecol_value.replace(".", ""))

        file_name = "_".join(file_info)
        return file_name

    def drop_clothes(self, columns: list[str]):
        if self.datatable is None:
            raise TypeError("Datatable is None")

        self.datatable.drop(columns)

    def extract_size_in_file(self, document_name: str) -> str | list | None:
        """
        gets the size in a file, i.e, 'small - mydesign.psd' returns small, small could also be s
        """
        file_name_arr = document_name[:-4].replace("-", " ").replace("_", " ").split()
        for file in file_name_arr:
            for size in Config.get_sc_sizes():
                if isinstance(size, list):
                    for s in size:
                        if Helper.compare_insensitive(s, file):
                            return size
                else:
                    if Helper.compare_insensitive(size, file):
                        return size
        return None

    def filter_by_clothes(self, target_cloth: str):
        if self.datatable is None:
            raise TypeError("Datatable is None")

        if not self.datatable.has_column(target_cloth):
            return False

        target_cloth = target_cloth.lower()

        self.datatable.apply(target_cloth, lambda s: target_cloth in s.lower())

        if self.datatable.has_column("size"):
            self.datatable.change_size(target_cloth)

        return True

    def filter_by_gender(self, gender: Gender):
        if self.datatable is None:
            raise TypeError("Datatable is None")

        condition = None
        if gender == Gender.MALE:
            condition = ["M", "Boy", "Male"]
        elif gender == Gender.FEMALE:
            condition = ["F", "Girl", "Female"]

        if not self.datatable.has_column("gender") or condition is None:
            return False

        self.datatable.filter("gender", condition)
        return True

    def __filter_by_size(self):
        if self.datatable is None:
            raise TypeError("Datatable is None")

        if self.resize_image is False and self.workspace is not None:
            size_in_file = self.extract_size_in_file(self.workspace.document_name)
            if size_in_file is None:
                raise ValueError(
                    rf"Missing size in document's file name: {self.workspace.document_name}"
                )
            self.datatable.filter("size", size_in_file, drop_option=False)
        elif self.workspace is None:
            raise TypeError("App is None")

    def has_clothes_column(self):
        if self.datatable is None:
            raise TypeError("Datatable is None")

        return self.datatable.has_column("clothes")

    def __get_fileformat_columns(self):
        # THIS CAN BE CACHED?
        if self.datatable is None:
            raise TypeError("Datatable is None")

        format_col = ["name", "size", Config.get_np_number_preference()]
        existing_col = []
        for fcol in format_col:
            if self.datatable.has_column(fcol):
                existing_col.append(fcol)
        return existing_col

    def initialize_components(
        self,
        workspace_path: str,
        clothing_path: str,
        datatable_path: str,
    ):
        try:
            self.initialize_workspace(workspace_path)
            self.open_size(clothing_path)
            self.open_datatable(datatable_path)
        except Exception as e:
            raise Exception(str(e))

    def print_df(self):
        if self.datatable is None:
            raise TypeError("Datatable is None")
        self.datatable.print()

    def print_layers(self):
        if self.workspace is None:
            raise TypeError("App is None")
        self.workspace.print()

    def print_sizes(self):
        if self.cloth_sizes is None:
            raise TypeError("Cloth sizes is None")
        self.cloth_sizes.print()

    def open_datatable(self, datatable_path):
        self.datatable = datatable_path

    def open_size(self, file_path: str):
        if file_path == "" or self.resize_image is False:
            return

        self.cloth_sizes = file_path

    def initialize_workspace(self, path):
        self.workspace = PhotoshopWorkspace(
            version=Config.get_ps_version(),
            ruler_unit=Config.get_rulerunit_preference(),
            image_quality=Config.get_jpg_quality(),
        )
        self.workspace.document_file_path = path

    def start(
        self,
        convert_cmyk=False,
        text_settings=TextSettings.DEFAULT,
        progress_callback=False,
    ) -> str:
        if self.workspace is None:
            raise TypeError("App is None")
        if self.resize_image is True and self.cloth_sizes is None:
            raise TypeError("Cloth sizes is None")
        if self.datatable is None:
            raise TypeError("Datatable is None")

        self.workspace.open()
        self.__filter_by_size()
        self.__transform_datatable(text_settings)

        log = ""
        debug_row, debug_col = None, None
        try:
            if self.datatable.is_empty():
                if Config.get_close_document() is True:
                    self.workspace.close()
                return log
            log = f"Starting document: {self.workspace.document_name}\n"

            error = self.__check_parameter_error()
            if error is not None:
                log += f"Parameter invalid in these layers: {error}\n"

            self.workspace.create_document_placeholder()

            idx_exist = self.datatable.has_column("index")

            for row in self.datatable.iterate_rows():
                self.workspace.save_state()

                row_idx = row[0]
                debug_row = row_idx
                row_num = (row[1][0] if idx_exist else row_idx) + 1  # type: ignore

                # fill layers
                for col, cell in row[1].items():
                    if col == "index":
                        continue
                    debug_col = col
                    self.workspace.fill_layers(col, cell)  # type: ignore

                # create filename
                item_name = self.__create_itemname(row_idx)
                file_name = self.__create_filename(row_num, item_name)

                self.workspace.fill_layers("filename", file_name)

                # change size
                if self.resize_image is True and self.datatable.has_column("size"):
                    size = self.datatable.at(row_idx, "size")
                    if not self.datatable.is_na(size):
                        shortsize = self.cloth_sizes.get_shortsize(size)  # type: ignore
                        if shortsize is not None:
                            self.workspace.fill_layers("shortsize", shortsize)

                    size_found = self.__change_doc_size(size)
                    if size_found is False:
                        log += (
                            f"picture #{row_num} size not found, cell value: {size}\n"
                        )

                # save file
                path = self.__create_fullname(self.output_path, file_name)
                self.workspace.save_as(path)
                self.workspace.revert_state()

                if convert_cmyk:
                    self.workspace.convert_cmyk(path)

            self.workspace.close()

            if Config.get_close_document() is True:
                self.workspace.close()
        except Exception as e:
            log += repr(e)
            if debug_row is not None and debug_col is not None:
                log += f"\nStopped at column: {debug_col} row: {debug_row} cell: {self.datatable.at(debug_row, debug_col)}\n"
            raise Exception(log)
        return log

    def __transform_datatable(self, text_setting=TextSettings.DEFAULT):
        if self.datatable is None:
            raise TypeError("Data is None")
        if text_setting == TextSettings.DEFAULT:
            return
        elif text_setting == TextSettings.UPPERCASE:
            self.datatable.transform(lambda s: s.upper() if isinstance(s, str) else s)
        elif text_setting == TextSettings.LOWERCASE:
            self.datatable.transform(lambda s: s.lower() if isinstance(s, str) else s)
        elif text_setting == TextSettings.CAPITALIZE:
            self.datatable.transform(
                lambda s: s.capitalize() if isinstance(s, str) else s
            )


class ClothModel:
    def __dir__(self):
        return " "

    def __init__(self, name, design: Path, sizes=""):
        self.name = name
        self.design = design
        self.sizes = sizes

    @property
    def design(self) -> Path:
        return self._design

    @design.setter
    def design(self, value: Path):
        self._design = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def sizes(self) -> str:
        return self._sizes

    @sizes.setter
    def sizes(self, value):
        self._sizes = value

    # METHODS
    def __str__(self):
        """
        for development use only
        """
        return rf"filter = {self.name} design: {self.design} sizes: {self.sizes} ({self.has_sizes()}) ({len(self.sizes)})"

    def has_sizes(self) -> bool:
        return len(self.sizes) > 0


class PhotomaticModel:
    def __dir__(self):
        return " "

    def __init__(self):
        self.lineup = ""
        self._models = list()

    @property
    def clothes(self) -> list[ClothModel]:
        return self._models

    @clothes.setter
    def clothes(self, value: list[ClothModel]):
        self._models = value

    @property
    def lineup(self) -> str:
        return self._data

    @lineup.setter
    def lineup(self, value: str):
        self._data = value

    # METHODS
    def add(self, model: ClothModel):
        self.clothes.append(model)

    def add_range(self, models: list[ClothModel]):
        self.clothes.extend(models)

    def clear(self):
        self.clothes.clear()

    def complete(self) -> bool:
        for model in self.iter_clothes():
            if model.has_sizes() is False:
                return False
        return True

    def count(self):
        return len(self.clothes)

    def get(self, index) -> ClothModel | None:
        if index < 0 or index >= len(self.clothes):
            return None
        return self.clothes[index]

    def get_all_design_name(self, model_name) -> list[str]:
        models = list()
        for model in self.iter_clothes():
            if model.name == model_name:
                models.append(model.design.name)
        return models

    def get_choices(self) -> set[str]:
        names = set()
        for model in self.iter_clothes():
            names.add(model.name)

        return names

    def get_designs(self) -> list[str]:
        design_names = list()
        for model in self.iter_clothes():
            design_names.append(model.design.name)
        return design_names

    def find(self, design_name) -> ClothModel | None:
        for model in self.iter_clothes():
            if model.design.name == design_name:
                return model
        return None

    def find_fullpath(self, design_path) -> ClothModel | None:
        for model in self.iter_clothes():
            if str(model.design) == design_path:
                return model
        return None

    def index(self, clothmodel) -> int:
        return self.clothes.index(clothmodel)

    def is_empty(self) -> bool:
        return len(self.clothes) == 0

    def iter_clothes(self):
        for model in self.clothes:
            yield model

    def print(self):
        print(f"total: {len(self.clothes)}")
        print(f"lineup: {self.lineup}")
        for model in self.clothes:
            print(model)

    def remove(self, name, design_name):
        self.clothes = [
            x
            for x in self.clothes
            if not (x.name == name and x.design.name in design_name)
        ]


class PhotomaticController:
    def __dir__(self):
        return " "

    def __init__(self):
        self._photomatic_engine = PhotomaticCoreEngine()
        self._photomatic_model = PhotomaticModel()
        self._project_path = None

    @property
    def engine(self) -> PhotomaticCoreEngine:
        return self._photomatic_engine

    @property
    def model(self) -> PhotomaticModel:
        return self._photomatic_model

    @property
    def project_path(self) -> Path | None:
        return self._project_path

    @project_path.setter
    def project_path(self, value: Path):
        self._project_path = value

    # METHODS
    def create_model(self, document_path: Path):
        self.model.add(ClothModel(document_path.name, document_path))

    def create_models(self, documents: dict[str, Path | list[Path]]):
        models = list()
        for key, value in documents.items():
            if isinstance(value, Path):
                models.append(ClothModel(key, value))
            elif isinstance(value, list):
                for doc in value:
                    models.append(ClothModel(key, doc))
        self.model.add_range(models)

    def has_document(self, directory) -> bool:
        folder = os.listdir(directory)
        for file in folder:
            if self.is_document(file):
                return True
        return False

    def is_document(self, file) -> bool:
        filetypes = (".psd", ".tif", ".crd")
        if file.endswith(filetypes):
            return True
        return False

    def scan_root_document(self, root_path: str) -> dict[str, Path | list[Path]]:
        documents = {}
        for item in os.listdir(root_path):
            item_path = Path(os.path.join(root_path, item))
            item_name = item_path.name
            if item_path.is_dir():
                documents[item_name] = self.search_documents(item_path)
            if item_path.is_file() and self.is_document(item_name):
                documents[item_name] = item_path
        return documents

    def search_documents(self, directory) -> list[Path]:
        documents = list()
        for item in os.listdir(directory):
            if self.is_document(item):
                documents.append(Path(os.path.join(directory, item)))
        return documents

    def select_document(self, path) -> int:
        item = Path(path)
        if item.is_dir():
            self.project_path = item
            documents = self.scan_root_document(path)
            self.create_models(documents)
            return len(documents)
        elif item.is_file():
            self.project_path = item.parent
            self.create_model(item)
            return 1
        else:
            return 0

    def select_lineup(self, data_path):
        self.model.lineup = data_path

    def start(
        self,
        cmyk: bool,
        text_settings: TextSettings,
        filter_by_gender: Gender | None = None,
    ):
        log = ""
        if self.model.lineup == "":
            raise TypeError("Data is None")
        if self.model.is_empty():
            raise ValueError("Please select a design file or folder")
        if self.project_path is None:
            raise TypeError("Path is None")

        self.engine.project_name = self.project_path.name
        project_path = rf"{str(self.project_path)}/output - {self.project_path.name}"
        Path(project_path).mkdir(exist_ok=True)

        for clothes in self.model.iter_clothes():
            try:
                output_path = rf"{project_path}/{clothes.name}"
                Path(output_path).mkdir(exist_ok=True)
                self.engine.output_path = output_path
                self.engine.initialize_components(
                    str(clothes.design), clothes.sizes, self.model.lineup
                )

                if (
                    not self.engine.filter_by_clothes(clothes.name)
                    and self.model.count() > 1
                ):
                    log += f"{clothes.name} not found in the lineup column, proceeding to the next document\n"
                    continue

                if filter_by_gender is not None:
                    self.engine.filter_by_gender(filter_by_gender)

                self.engine.drop_clothes(list(self.model.get_choices()))
                log += self.engine.start(cmyk, text_settings)
            except Exception as e:
                error_message = str(e)
                log += f"{str(error_message)}\n"
                if (
                    "'The message filter indicated that the application is busy.'"
                    in error_message
                ):
                    return log

        return log
