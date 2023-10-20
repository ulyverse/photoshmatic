from enum import Enum


class TextSettings(Enum):
    DEFAULT = "default"
    UPPERCASE = "uppercase"
    LOWERCASE = "lowercase"
    CAPITALIZE = "capitalize"


class Parameter(Enum):
    WIDTH = "w"
    HEIGHT = "h"


class UnitPreference(Enum):
    INCHES = "in"
    CENTIMETERS = "cm"
    PIXELS = "px"