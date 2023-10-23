import photoshop.api as ps
from enumeration import UnitPreference
from enumeration import Dimension
from utils import Helper

class PhotoshopWorkspace():
    def __dir__():
        return " "

    def __init__(self, version=None, ruler_unit = UnitPreference.INCHES.value, image_quality=12):
        self.application = ps.Application(version=version)
        self.set_unit_preference(ruler_unit)
        self.__jpg_save_preference = ps.JPEGSaveOptions(image_quality)

    @property
    def active_layer(self):
        return self.document.activeLayer

    @active_layer.setter
    def active_layer(self, layer):
        self.document.activeLayer = layer

    @property
    def application(self):
        return self.__application
    
    @application.setter
    def application(self, app: ps.Application):
        self.__application = app

    @property
    def document(self):
        return self.application.activeDocument

    @property
    def document_name(self):
        return self.document.name
    
    @property
    def document_fullname(self):
        return self.document.fullName
    
    @property
    def layers(self):
        return self.document.layers
    
    @property
    def text_direction(self):
        return self.active_layer.textItem.direction

    @property
    def unit_preference(self):
        return self.application.preferences.rulerUnits
    
    #METHODS
    def apply_parameter(self, max_length):
        layer_dimension = self.get_active_layer_dimension()
        horizontal = self.is_active_layer_horizontal()
        orientation = Dimension.WIDTH if horizontal else Dimension.HEIGHT

        if self.exceed_max_length(layer_dimension[orientation], max_length):
            ratio = max_length/layer_dimension[orientation]*100
            if horizontal:
                self.resize_layer(ratio, 100, ps.AnchorPosition.MiddleCenter)
            else:
                self.resize_layer(100, ratio, ps.AnchorPosition.TopCenter)

    def close(self):
        self.document.close(ps.SaveOptions.DoNotSaveChanges)

    def convert_cmyk(self, path):
        self.open(f"{path}.jpg")
        self.document.changeMode(ps.ChangeMode.ConvertToCMYK)
        self.document.close(ps.SaveOptions.SaveChanges)

    def create_document_placeholder(self):
        self.document.duplicate(f"{self.document_name} - placeholder")

    def exceed_max_length(self, length, max):
        return length > max

    def fill_layers(self, key:str, value:str):
        for layer in self.iterate_layers():
            layer_name = layer.name.split()
            if len(layer_name) > 0 and layer_name[0] == key:
                layer.textItem.contents = value
                
                if len(layer_name) == 1: continue

                max = self.get_max_length(layer_name[1])
                if max is None: continue

                self.active_layer = layer
                self.apply_parameter(max)

    def get_active_layer_dimension(self):
        dimension = {}
        bounds = self.active_layer.bounds
        dimension[Dimension.WIDTH] = bounds[2] - bounds[0]
        dimension[Dimension.HEIGHT] = bounds[3] - bounds[1]
        return dimension

    def get_max_length(self, parameter):
        return Helper.try_parse(parameter) if parameter[0].isdigit() else Helper.try_parse(parameter[2:])

    def get_ruler_unit(self, ruler_unit):
        rulerunit = None
        if ruler_unit == UnitPreference.INCHES.value:
            rulerunit = ps.Units.Inches
        elif ruler_unit == UnitPreference.CENTIMETERS.value:
            rulerunit = ps.Units.CM
        elif ruler_unit == UnitPreference.PIXELS.value:
            rulerunit = ps.Units.Pixels
        
        return rulerunit
    
    def is_active_layer_horizontal(self):
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
        self.active_layer.resize(horizontal, vertical, anchor)

    def revert_state(self):
        self.document.activeHistoryState = self.saved_state

    def save_as(self, path):
        self.document.saveAs(path, self.__jpg_save_preference)

    def save_state(self):
        self.saved_state = self.document.activeHistoryState

    def set_unit_preference(self, ruler_unit):
        self.application.preferences.rulerUnits = self.get_ruler_unit(ruler_unit)
