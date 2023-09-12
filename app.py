class PhotoshopFiller:
    def __init__(self, photoshop_path = None, csv_path = None, size_path = None) -> None:
        self.photoshop_path = photoshop_path
        self.csv_path = csv_path
        self.size_path = size_path
    
    def create(self):
        pass


test = PhotoshopFiller("Test", "Testsdf2")

print(test.photoshop_path, test.csv_path, test.size_path)

print("Hello world")