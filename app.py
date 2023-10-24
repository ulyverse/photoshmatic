# dependency modules
from tkinter import messagebox

# custom modules
from configuration import Config
from gui import WindowFrameManager


def __dir__():
    return " "


def main():
    try:
        Config.load_config()
    except Exception as e:
        messagebox.showerror("Photomatic - settings.json incorrect format", str(e))
        return
    WindowFrameManager().run()


if __name__ == "__main__":
    main()
