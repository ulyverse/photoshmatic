# dependency modules
import json


def __dir__():
    return " "


class Config:
    data = None

    @classmethod
    def load_config(cls):
        if cls.data is None:
            try:
                with open("settings/settings.json", "r") as f:
                    cls.data = json.load(f)
            except json.decoder.JSONDecodeError as e:
                raise Exception(repr(e))
            except FileNotFoundError:
                raise Exception("settings/settings.json is missing")

    @classmethod
    def get_app_name(cls) -> str:
        if cls.data is None:
            cls.load_config()
        data = cls.data["app_name"]
        return data if data != "" else "PHOTOMATIC"

    @classmethod
    def get_jpg_quality(cls):
        if cls.data is None:
            cls.load_config()
        data = cls.data["jpg_quality"]
        return data if type(data) == int and data > 0 else 12

    @classmethod
    def get_ps_version(cls):
        if cls.data is None:
            cls.load_config()
        return cls.data["ps_version"] if cls.data["ps_version"] != "" else None

    @classmethod
    def get_character_encoding(cls):
        if cls.data is None:
            cls.load_config()
        return cls.data["char_encoding"] if cls.data["char_encoding"] != "" else "mbcs"

    @classmethod
    def get_rulerunit_preference(cls):
        if cls.data is None:
            cls.load_config()
        return (
            cls.data["rulerunit_preference"]
            if cls.data["rulerunit_preference"] != ""
            else "in"
        )

    @classmethod
    def get_np_number_preference(cls):
        if cls.data is None:
            cls.load_config()
        data = cls.data["naming_preference"]["number"]
        return data if data != "" else "number"

    @classmethod
    def get_sc_resize_image(cls):
        if cls.data is None:
            cls.load_config()
        data = cls.data["size_config"]["resize_image"]
        return data if data != None and type(data) == bool else True

    @classmethod
    def get_sc_sizes(cls):
        if cls.data is None:
            cls.load_config()
        return cls.data["size_config"]["sizes"]
