import photoshop.api as ps
from enumeration import UnitPreference

class PhotoshopWorkspace():
    def __dir__():
        return " "

    def __init__(self, version=None, ruler_unit = UnitPreference.INCHES, image_quality=12):
        self.application = ps.Application(version=version)
        self.set_unit_preference(ruler_unit)
        self.__jpg_save_preference = ps.JPEGSaveOptions(image_quality)

    @property
    def active_layer(self):
        return self.document.activeLayer

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
    def unit_preference(self):
        return self.application.preferences.rulerUnits
    
    #METHODS
    def close(self):
        self.document.close(ps.SaveOptions.DoNotSaveChanges)

    def convert_cmyk(self, path):
        self.open(f"{path}.jpg")
        self.document.changeMode(ps.ChangeMode.ConvertToCMYK)
        self.document.close(ps.SaveOptions.SaveChanges)

    def create_placeholder(self):
        self.document.duplicate(f"{self.document_name} - placeholder")

    def exceed_max_length(self, length, max):
        return length > max

    def fill_layers(self, key:str, value:str):
        for layer in self.iterate_layers():
            layer_name = layer.name.split()
            if len(layer_name) > 0 and layer_name[0] == key:
                layer.textItem.contents = value
                
                if len(layer_name) == 1:
                    continue
                self.active_layer = layer

                parameter = layer_name[1]


    def get_layer_dimension(self):
        dimension = {}
        bounds = self.active_layer.bounds
        dimension['height'] = bounds[3] - bounds[1]
        dimension['width'] = bounds[2] - bounds[0]
        return dimension

    def get_max_length(self, parameter):
        try:
            max = float(parameter)
            return max
        except:
            return None

    def get_ruler_unit(self, ruler_unit):
        if ruler_unit == UnitPreference.INCHES:
            rulerunit = ps.Units.Inches
        elif ruler_unit == UnitPreference.CENTIMETERS:
            rulerunit = ps.Units.CM
        elif ruler_unit == UnitPreference.PIXELS:
            rulerunit = ps.Units.Pixels
        
        return rulerunit
    
    def iterate_layers(self):
        for layer in self.layers:
            yield layer

    def open(self, path):
        self.application.open(path)

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
        


    


myApp = PhotoshopWorkspace("2021")
print(myApp.document_fullname)
print(myApp.document_name)
print(myApp.unit_preference)
dimension = myApp.get_layer_dimension()
print(dimension['width'])
print(dimension['height'])