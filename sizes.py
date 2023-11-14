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

    def __init__(self, path) -> None:
        self.sizes = ClothSizes.read_clothing(path)
        self.name = path[6:-5]

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

    # METHODS
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
        sizes = []
        clothing = Helper.extract_json(file_path, file_path)

        for size in clothing["sizes"]:
            sizes.append(
                Size(
                    size["name"],
                    size["width"],
                    size["height"],
                    size["shortsize"],
                )
            )
        return sizes
