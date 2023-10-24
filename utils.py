# dependency modules
import hashlib
import uuid

# custom modules
from configuration import Config
from enumeration import TextSettings


def __dir__():
    return " "


class Helper:
    def __dir__(self):
        return " "

    # PURE HELPER
    @classmethod
    def compare_insensitive(cls, str1: str, str2: str) -> bool:
        """
        compare both strings case insensitivity

        returns True if strings are the same otherwise False
        """
        return str1.lower() == str2.lower()

    # PHOTOMATIC HELPER
    @classmethod
    def extract_size_in_file(cls, document_name: str) -> str | list | None:
        """
        param:
        file_name:str - must include .psd the function strips it, ex: "2XL - Lower 2022 V2.psd"

        note:
        before returning the value it removes '-' and '_' to reduce uncertainty significantly

        returns:
        the found value of config_sc_sizes either "XL" or ['S','SMALL']
        """
        file_name_arr = document_name[:-4].replace("-", " ").replace("_", " ").split()
        for file in file_name_arr:
            for size in Config.get_sc_sizes():
                if isinstance(size, list):
                    for s in size:
                        if cls.compare_insensitive(s, file):
                            return size
                else:
                    if cls.compare_insensitive(size, file):
                        return size
        return None

    # PURE HELPER
    @classmethod
    def try_parse(cls, digit: str) -> float | None:
        try:
            num = float(digit)
            return num
        except Exception:
            return None

    # SETUP HELPER
    @classmethod
    def get_mac_address(cls):
        return ":".join(("%012X" % uuid.getnode())[i : i + 2] for i in range(0, 12, 2))

    # PHOTOMATIC HELPER
    @classmethod
    def get_size_condition(cls, document) -> list[str]:
        """
        param:
        document: document_name

        extracts the 'size' in the document_name and (see return)

        returns:
        an array of both the original str, upper and lower of the size_name or an empty list
        """
        size_name = cls.extract_size_in_file(document)
        if size_name is None:
            return []

        if isinstance(size_name, list):
            condition = []
            for size in size_name:
                condition.append(size.lower())
                condition.append(size.upper())
                if len(size) > 3:
                    condition.append(size.capitalize())
            return condition

        return [size_name, size_name.lower(), size_name.upper(), size_name.capitalize()]

    @classmethod
    def get_textsetting(cls, settings):
        if settings == TextSettings.DEFAULT.value:
            return TextSettings.DEFAULT
        elif settings == TextSettings.UPPERCASE.value:
            return TextSettings.UPPERCASE
        elif settings == TextSettings.LOWERCASE.value:
            return TextSettings.LOWERCASE
        elif settings == TextSettings.CAPITALIZE.value:
            return TextSettings.CAPITALIZE
        else:
            return None

    # GUI CMB PHOTOMATIC
    @classmethod
    def get_textsettings(cls):
        txtset = list()
        for text_setting in TextSettings:
            txtset.append(text_setting.value)
        return txtset

    # SETUP HELPER
    @classmethod
    def get_uniq_identifier(cls):
        return hashlib.md5(
            (cls.get_mac_address() + "hehexd").encode("utf-8")
        ).hexdigest()
