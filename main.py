import setup
from gui import Window

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
            if setup.enter_license_code():
                Window().run()
                break
            else:
                print("Incorrect Key")
    except Exception as e:
        print("Cannot access the server, please check your internet connection.")
        print(e)
        return

if __name__ == "__main__":
    main()