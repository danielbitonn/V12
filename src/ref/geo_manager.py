import tkinter as tk

class PackWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Pack Layout")
        self.geometry("300x200")

        tk.Label(self, text="Label 1").pack()
        tk.Label(self, text="Label 2").pack()
        tk.Label(self, text="Label 3").pack()


class GridWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Grid Layout")
        self.geometry("300x200")

        tk.Label(self, text="Label 1").grid(row=0, column=0)
        tk.Label(self, text="Label 2").grid(row=0, column=1)
        tk.Label(self, text="Label 3").grid(row=1, column=0)


class PlaceWindow(tk.Tk):
    """
    x and y indicating the position from the top-left corner of the window.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Place Layout")
        self.geometry("300x200")

        tk.Label(self, text="Label 1").place(x=50, y=50)
        tk.Label(self, text="Label 2").place(x=100, y=100)
        tk.Label(self, text="Label 3").place(x=150, y=150)
