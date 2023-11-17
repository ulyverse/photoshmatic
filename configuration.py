# dependency modules
from utils import Helper


def __dir__():
    return " "


class Config:
    data = {}

    def __dir__(self):
        return " "

    @classmethod
    def is_empty(cls):
        return len(cls.data) == 0

    @classmethod
    def load_config(cls):
        if cls.is_empty():
            cls.data = Helper.extract_json("settings/settings.json", "settings.json")

    @classmethod
    def refresh(cls):
        cls.data = Helper.extract_json("settings/settings.json", "settings.json")

    # Configuration Settings
    @classmethod
    def get_app_name(cls) -> str:
        if cls.is_empty():
            cls.load_config()
        data = cls.data["app_name"]
        return data if data != "" else "PHOTOMATIC"

    @classmethod
    def get_character_encoding(cls):
        if cls.is_empty():
            cls.load_config()
        return cls.data["char_encoding"] if cls.data["char_encoding"] != "" else "mbcs"

    @classmethod
    def get_close_document(cls):
        if cls.is_empty():
            cls.load_config()
        return (
            cls.data["close_document"]
            if cls.data["close_document"] is not None
            else True
        )

    @classmethod
    def get_jpg_quality(cls):
        if cls.is_empty():
            cls.load_config()
        data = cls.data["jpg_quality"]
        return data if isinstance(data, int) and data > 0 else 12

    @classmethod
    def get_np_number_preference(cls):
        if cls.is_empty():
            cls.load_config()
        data = cls.data["naming_preference"]["number"]
        return data if data != "" else "number"

    @classmethod
    def get_ps_version(cls):
        if cls.is_empty():
            cls.load_config()
        return cls.data["ps_version"] if cls.data["ps_version"] != "" else None

    @classmethod
    def get_resize_image(cls):
        if cls.is_empty():
            cls.load_config()
        data = cls.data["size_config"]["resize_image"]
        return data if data is not None and isinstance(data, bool) else True

    @classmethod
    def get_rulerunit_preference(cls):
        if cls.is_empty():
            cls.load_config()
        return (
            cls.data["rulerunit_preference"]
            if cls.data["rulerunit_preference"] != ""
            else "in"
        )

    @classmethod
    def get_sc_sizes(cls):
        if cls.is_empty():
            cls.load_config()
        return cls.data["size_config"]["sizes"]


class SettingsManager:
    def __dir__(self):
        return " "

    def __init__(self):
        self.settings_path = "settings/settings.json"
        self.settings = Helper.extract_json(self.settings_path, "settings.json")

    def save(self):
        Helper.set_json(self.settings_path, self.settings)

    def set_application_name(self, value):
        if isinstance(value, str):
            self.settings["app_name"] = value

    def set_close_document(self, value):
        if isinstance(value, bool):
            self.settings["close_document"] = value

    def set_ps_version(self, value):
        if isinstance(value, str):
            if value == "auto-detect":
                value = ""
            self.settings["ps_version"] = value

    def set_resize_image(self, value):
        if isinstance(value, bool):
            self.settings["size_config"]["resize_image"] = value
