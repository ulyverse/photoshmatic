# dependency modules
import json

# custom modules
from utils import Helper


def __dir__():
    return " "


class Size:
    def __dir__(self):
        return " "

    def __init__(self, name: str, width: float, height: float, short_size: str) -> None:
        self.name = name
        self.width = width
        self.height = height
        self.short_size = short_size

    def __str__(self):
        return f"{self.name} {self.width} {self.height} {self.short_size}"


class ClothSizes:
    """
    Controller for sizes
    """

    def __dir__(self):
        return " "

    def __init__(self, sizes: list[Size], name) -> None:
        self.sizes = sizes
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, clothing_name):
        self._name = clothing_name

    @property
    def sizes(self):
        return self._sizes

    @sizes.setter
    def sizes(self, sizes: list[Size]):
        if len(sizes) == 0:
            raise ValueError("Clothing sizes not found")
        self._sizes = sizes

    # method
    def get_shortsize(self, size_name: str):
        size = self.get_size(size_name)
        if size is not None:
            return size.short_size

        return None

    def get_size(self, size_name: str):
        for size in self.sizes:
            if Helper.compare_insensitive(size.name, size_name):
                return size

        return None

    def print(self):
        for size in self.sizes:
            print(str(size))

    @classmethod
    def read_clothing(cls, file_path):
        try:
            sizes = []
            with open(str(file_path)) as s:
                json_raw = json.load(s)

            for json_raw_sizes in json_raw["sizes"]:
                sizes.append(
                    Size(
                        json_raw_sizes["name"],
                        json_raw_sizes["width"],
                        json_raw_sizes["height"],
                        json_raw_sizes["shortsize"],
                    )
                )
            return sizes
        except json.decoder.JSONDecodeError as e:
            raise Exception(repr(e))
        except FileNotFoundError:
            raise Exception(f"{file_path} is missing")
