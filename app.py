from gui import WindowFrameManager
from tkinter import messagebox
from utils import Config

def __dir__():
    return " "

def main():
    try:
        Config.load_config()
    except Exception as e:
        messagebox.showerror("Photomatic - settings.json incorrect format", e)
        return
    WindowFrameManager().run()

if __name__ == "__main__":
    main()