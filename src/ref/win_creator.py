from src.util.buttons import *

# imports
import tkinter as tk



def createWin():
    """
        You can add various types of widgets to your window,
        such as labels, buttons, text fields, etc.
        :return: XXX
    """
    win = tk.Tk()
    win.title("My-App")
    win.geometry("1000x600")

    frame = tk.Frame(win, bg='red', bd=2)
    frame.pack(fill=tk.BOTH, expand=True)
    frame.pack_propagate(False)

    label = tk.Label(win, text="Hello, World!")
    label.pack()

    but1 = tk.Button(frame, text="Button 1", command=but1_clicked)
    but1.pack(side=tk.LEFT, padx=10)

    but2 = tk.Button(frame, text="Button 2", command=but2_clicked)
    but2.pack(side=tk.LEFT, padx=10)

    win.mainloop()

