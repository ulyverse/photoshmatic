import setup
from gui import Window


def main():
    if setup.setup():
        Window().run()
        return
    
    while True:
        if setup.enter_license_code():
            Window().run()
            break
        else:
            print("Incorrect Key")


if __name__ == "__main__":
    main()