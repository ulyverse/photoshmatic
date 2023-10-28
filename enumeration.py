# dependency modules
from enum import Enum


def __dir__():
    return " "


class Dimension(Enum):
    WIDTH = 0
    HEIGHT = 1


class Gender(Enum):
    MALE = 0
    FEMALE = 1


class TextSettings(Enum):
    DEFAULT = "default"
    UPPERCASE = "uppercase"
    LOWERCASE = "lowercase"
    CAPITALIZE = "capitalize"


class UnitPreference(Enum):
    INCHES = "in"
    CENTIMETERS = "cm"
    PIXELS = "px"
