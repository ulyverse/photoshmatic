def __dir__():
    return " "

class Size:
    def __init__(self, name: str, width: float, height: float, short_size: str) -> None:
        self.name = name
        self.width = width
        self.height = height
        self.short_size = short_size
    
