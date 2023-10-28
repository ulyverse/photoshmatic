# dependency modules
import photoshop.api as ps

# custom modules
from enumeration import UnitPreference
from enumeration import Dimension
from utils import Helper


def __dir__():
    return " "


class PhotoshopWorkspace:
    def __dir__(self):
        return " "

    def __init__(
        self, version=None, ruler_unit=UnitPreference.INCHES.value, image_quality=12
    ):
        self.application = ps.Application(version=version)
        self.set_unit_preference(ruler_unit)
        self.__jpg_save_preference = ps.JPEGSaveOptions(image_quality)

    @property
    def application(self):
        return self.__application

    @application.setter
    def application(self, app: ps.Application):
        self.__application = app

    @property
    def current_layer(self):
        return self._current_layer

    @current_layer.setter
    def current_layer(self, layer):
        self._current_layer = layer

    @property
    def document(self):
        return self.application.activeDocument

    @property
    def document_name(self):
        return self.document.name

    @property
    def document_fullname(self):
        return str(self.document.fullName)

    @property
    def layers(self):
        return self.document.layers

    @property
    def text_direction(self):
        return self.current_layer.textItem.direction

    @property
    def unit_preference(self):
        return self.application.preferences.rulerUnits

    # METHODS
    def apply_parameter(self, max_length, param=""):
        layer_dimension = self.get_current_layer_dimension()
        horizontal = self.is_current_layer_horizontal()
        orientation = (
            Dimension.WIDTH
            if horizontal and not Helper.compare_insensitive(param, "h")
            else Dimension.HEIGHT
        )

        if self.exceed_max_length(layer_dimension[orientation], max_length):
            ratio = (
                max_length
                / layer_dimension[orientation]
                * self.get_text_scale(horizontal)
            )
            not_ellipse = True

            try:
                self.current_layer.textItem.kind
            except Exception:
                not_ellipse = False

            if not_ellipse:
                if horizontal or (
                    Helper.compare_insensitive(param, "h") and horizontal
                ):
                    self.set_horizontal_scale(ratio)
                else:
                    self.set_vertical_scale(ratio)

            else:
                self.ellipse_scale(max_length, ratio)

    def close(self):
        self.document.close(ps.SaveOptions.DoNotSaveChanges)

    def convert_cmyk(self, path):
        self.open(f"{path}.jpg")
        self.document.changeMode(ps.ChangeMode.ConvertToCMYK)
        self.document.close(ps.SaveOptions.SaveChanges)

    def create_document_placeholder(self):
        self.document.duplicate(f"{self.document_name} - placeholder")

    def ellipse_scale(self, max_length, ratio):
        scale = ratio
        while self.get_current_layer_dimension()[Dimension.WIDTH] > max_length:
            self.set_horizontal_scale(scale)
            scale -= 5

    def exceed_max_length(self, length, max_length):
        return length > max_length

    def fill_layers(self, key: str, value: str):
        for layer in self.iterate_layers():
            if layer.visible is False:
                continue

            layer_name = layer.name.split()
            if len(layer_name) > 0 and layer_name[0] == key:
                layer.textItem.contents = value

                if len(layer_name) == 1:
                    continue

                max_length = self.get_max_length(layer_name[1])
                if max_length is None:
                    continue

                self.current_layer = layer
                param = layer_name[1][:1]  # get parameter incase someone puts H
                self.apply_parameter(max_length, param)

    def get_current_layer_dimension(self):
        dimension = {}
        bounds = self.current_layer.bounds
        dimension[Dimension.WIDTH] = bounds[2] - bounds[0]
        dimension[Dimension.HEIGHT] = bounds[3] - bounds[1]
        return dimension

    def get_horizontal_scale(self):
        return self.current_layer.textItem.horizontalScale

    def get_max_length(self, parameter):
        return (
            Helper.try_parse(parameter)
            if parameter[0].isdigit()
            else Helper.try_parse(parameter[2:])
        )

    def get_ruler_unit(self, ruler_unit):
        rulerunit = None
        if ruler_unit == UnitPreference.INCHES.value:
            rulerunit = ps.Units.Inches
        elif ruler_unit == UnitPreference.CENTIMETERS.value:
            rulerunit = ps.Units.CM
        elif ruler_unit == UnitPreference.PIXELS.value:
            rulerunit = ps.Units.Pixels

        return rulerunit

    def get_text_scale(self, is_horizontal):
        return (
            self.get_horizontal_scale() if is_horizontal else self.get_vertical_scale()
        )

    def get_vertical_scale(self):
        return self.current_layer.textItem.verticalScale

    def is_current_layer_horizontal(self):
        return self.text_direction == ps.Direction.Horizontal

    def iterate_layers(self):
        for layer in self.layers:
            yield layer

    def open(self, path):
        self.application.open(path)

    def print(self):
        for layer in self.iterate_layers():
            print(layer.name)

    def resize_image(self, width, height):
        self.document.resizeImage(width, height, self.document.resolution)

    def resize_layer(self, horizontal, vertical, anchor):
        self.current_layer.resize(horizontal, vertical, anchor)

    def revert_state(self):
        self.document.activeHistoryState = self.saved_state

    def save_as(self, path):
        self.document.saveAs(path, self.__jpg_save_preference)

    def save_state(self):
        self.saved_state = self.document.activeHistoryState

    def set_horizontal_scale(self, ratio):
        self.current_layer.textItem.horizontalScale = ratio

    def set_unit_preference(self, ruler_unit):
        self.application.preferences.rulerUnits = self.get_ruler_unit(ruler_unit)

    def set_vertical_scale(self, ratio):
        self.current_layer.textItem.verticalScale = ratio
