# dependency modules
import hashlib
import json
import os
import subprocess
import uuid


# custom modules
from enumeration import Gender
from enumeration import TextSettings
from enumeration import UnitPreference


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

    @classmethod
    def check_key(cls, key, dictionary):
        return True if key in dictionary else False

    @classmethod
    def extract_json(cls, json_path, name):
        try:
            with open(json_path, "r") as file:
                return json.load(file)
        except json.decoder.JSONDecodeError as e:
            raise Exception(f"File: {name}, {repr(e)}")
        except FileNotFoundError as e:
            raise Exception(f"{name} is missing")

    @classmethod
    def set_json(cls, path, json_object):
        with open(path, "w") as file:
            json.dump(json_object, file, indent=4)

    # SETUP HELPER
    @classmethod
    def find_gender(self, value):
        if value == "all":
            return None
        if value == "male":
            return Gender.MALE
        elif value == "female":
            return Gender.FEMALE

    @classmethod
    def find_textsetting(cls, value):
        for text_setting in TextSettings:
            if text_setting.value == value:
                return text_setting
        return TextSettings.DEFAULT

    @classmethod
    def find_unitpreference(cls, value):
        for unit_pref in UnitPreference:
            if unit_pref == value:
                return UnitPreference
        return UnitPreference.INCHES

    @classmethod
    def get_condition(cls, words) -> set[str]:
        """
        returns a condition for filtering
        """
        if isinstance(words, list):
            condition = set(words)
            for size in words:
                condition.add(size.lower())
                condition.add(size.upper())
                condition.add(size.capitalize())
            return condition

        if isinstance(words, str):
            return set([words, words.upper(), words.lower(), words.capitalize()])

        return set()

    # SETUP HELPER
    @classmethod
    def get_disk_serial_number(cls):
        """returns the serial number of the first disk (alphabetical)"""
        return (
            subprocess.check_output("wmic diskdrive get serialnumber")
            .decode()
            .split("\n")[1]
            .strip()
        )

    @classmethod
    def get_hardware_id(cls):
        return (
            subprocess.check_output("wmic csproduct get uuid")
            .decode()
            .split("\n")[1]
            .strip()
        )

    @classmethod
    def get_mac_address(cls):
        return ":".join(("%012X" % uuid.getnode())[i : i + 2] for i in range(0, 12, 2))

    @classmethod
    def get_uniq_identifier(cls):
        machine_identifier = cls.get_hardware_id()
        if Helper.compare_insensitive(
            machine_identifier, "FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF"
        ):
            machine_identifier = cls.get_disk_serial_number()
        return hashlib.md5((machine_identifier + "hehexd").encode("utf-8")).hexdigest()

    # GUI CMB PHOTOMATIC
    @classmethod
    def populate_gender(cls):
        gender = ["all", "male", "female"]
        return gender

    @classmethod
    def populate_sizes(cls, headings=None):
        sizes = []
        if headings is not None:
            sizes.append(headings)
        for size in os.listdir("sizes/"):
            name = size[:-5]
            if name == "template":
                continue
            sizes.append(name)
        return sizes

    @classmethod
    def populate_textsettings(cls):
        txtset = list()
        for text_setting in TextSettings:
            txtset.append(text_setting.value)
        return txtset

    # PURE HELPER
    @classmethod
    def convert_to_bool(cls, number: int | str):
        return True if number == 1 else False

    @classmethod
    def get_size_path(cls, name: str):
        return rf"sizes/{name}.json"

    @classmethod
    def parse_number(cls, digit: str) -> float | int:
        num = float(digit)
        return int(num) if num == int(num) or digit.rstrip("0").endswith(".") else num

    @classmethod
    def try_parse(cls, digit: str) -> float | None:
        try:
            num = float(digit)
            return num
        except ValueError:
            return None
