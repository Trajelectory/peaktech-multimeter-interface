import tkinter as tk
from tkinter import font
from peaktech_gui import PeakTechApp

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)

    root = tk.Tk()
    try:
        font.nametofont("Digital-7")
    except:
        logging.warning("You need to install the 'Digital-7' font for best results.")

    app = PeakTechApp(root)
    root.mainloop()