from tkinter import Tk, Button, Label, Toplevel, Frame
from src.util.buttons_action import *


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Report V12")
        self.root.geometry("1200x600")
        self.root.iconbitmap('src/_ref_/media/v12.ico')

        # Frame to hold other widgets
        self.frame = Frame(root)
        self.frame.pack(padx=10, pady=10)

        # Add label
        self.add_widget(Label, "Report Functionality", 0)

        # Add buttons
        self.add_widget(Button, "Data Collector (Press-Only) & Push", 1, lambda: self.button_clicked(1))
        self.add_widget(Button, "Import Data from cloud", 2, lambda: self.button_clicked(2))
        self.add_widget(Button, "States Analysis", 3, lambda: self.button_clicked(3))
        self.add_widget(Button, "Button 4", 4, lambda: self.button_clicked(4))
        self.add_widget(Button, "Button 5", 5, lambda: self.button_clicked(5))
        self.add_widget(Button, "Button 6", 6, lambda: self.button_clicked(6))
        self.add_widget(Button, "Button 7", 7, lambda: self.button_clicked(7))

    def button_clicked(self, button_num):
        button_switch_case(button_num)
        new_window = Toplevel(self.root)
        new_window.title(f"Window {button_num}")
        label = Label(new_window, text=f"Button {button_num} was clicked")
        label.pack()

    def add_widget(self, widget_type, widget_name, row, action=None):
        """Adds a widget to the layout at the specified position."""
        widget = widget_type(self.frame, text=widget_name)
        widget.grid(row=row, column=0, sticky="w", padx=10, pady=10)
        # If the widget is a Button and an action is defined, connect the action to the button's clicked signal
        if isinstance(widget, Button) and action is not None:
            widget.config(command=action)

def execute_app():
    root = Tk()
    win = MainWindow(root)
    root.mainloop()
