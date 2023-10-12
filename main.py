import setup
from gui import Window
from requests import ConnectionError

def __dir__():
    return " "

def main():
    try:
        if not setup.validate_version():
            print("This version of the app isn't supported anymore, please update your app to the latest version.")
            return
        
        if setup.setup() or setup.validate_registered_device():
            Window().run()
            return
    
        while True:
            key = input("Enter your license key:")
            if setup.enter_license_code(key):
                Window().run()
                break
            else:
                print("Incorrect Key")
    except ConnectionError as e:
        print("Cannot access the server, please check your internet connection.")
    except Exception as e:
        print(repr(e))

if __name__ == "__main__":
    main()