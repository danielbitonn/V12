from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QVBoxLayout, QWidget, QPushButton
from src.util.buttons_action import *
from PyQt5.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set window title
        self.setWindowTitle("Grid My PyQt Application")
        self.resize(800, 600)
        # self.setFixedSize(800, 600) #  fix the size of the window and prevent the user from resizing
        
        # Set window icon
        self.setWindowIcon(QIcon('src/ref/media/v12.ico'))

        # Create a QWidget that will hold our layout
        self.widget = QWidget()

        # Create a QGridLayout or QVBoxLayout
        self.layout = QGridLayout()

        # Set the layout on the QWidget
        self.widget.setLayout(self.layout)

        # Add the label to the layout
        self.add_widget(QLabel, "Hello, PyQt!", 0, 0)

        # Add the buttons to the layout using the add_widget method
        self.add_widget(QPushButton, "Button 1", 1, 0, lambda: self.button_clicked(1))
        self.add_widget(QPushButton, "Button 2", 2, 0, lambda: self.button_clicked(2))
        self.add_widget(QPushButton, "Button 3", 3, 0, lambda: self.button_clicked(3))

        # Set the central widget of the window.
        self.setCentralWidget(self.widget)

    def button_clicked(self, button_num):
        """button_num is a natural number (N)"""
        button_action(button_num)


    def add_widget(self, widget_type, widget_name, row, col, action=None):
        """Adds a widget to the layout at the specified position."""
        widget = widget_type(widget_name)
        self.layout.addWidget(widget, row, col)

        # If the widget is a QPushButton and an action is defined, connect the action to the button's clicked signal
        if isinstance(widget, QPushButton) and action is not None:
            widget.clicked.connect(action)


def excecute_app():
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec_()
