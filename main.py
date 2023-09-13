from utils import PhotoshopFiller



def main():
    psFiller = PhotoshopFiller(photoshop_path=r"C:\Users\johna\Desktop\Photoshop scripting test\Test 2\practice.psd", 
                       csv_path=r"C:\Users\johna\Desktop\Photoshop scripting test\Test 2\sample.csv",
                       json_path=r"C:\Users\johna\Desktop\Photoshamatic\Sizes\upper_jersey.json")
    
    psFiller.ps_change_colormode(isRgb=True)
    psFiller.start()


if __name__ == "__main__":
    main()