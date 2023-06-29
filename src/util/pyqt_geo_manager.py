from PyQt5.QtWidgets import QWidget, QFileDialog, QApplication, QMainWindow, QLabel, \
    QGridLayout, QVBoxLayout, QWidget, \
    QPushButton, QMdiArea, QMdiSubWindow, QMessageBox

from PyQt5.QtGui import QIcon
from src.util.buttons_action import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set window title
        self.setWindowTitle("Daily Report V12")
        self.resize(1200,
                    600)  # self.setFixedSize(800, 600) #  fix the size of the window and prevent the user resizing

        # Set window icon
        self.setWindowIcon(QIcon('src/ref/media/v12.ico'))

        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)

        # Create a QWidget that will hold our layout
        self.widget = QWidget()
        # Create a QGridLayout or QVBoxLayout
        self.layout = QGridLayout()
        # Set the layout on the QWidget
        self.widget.setLayout(self.layout)

        # Add the label to the layout
        self.add_widget(QLabel, "Report Functionality", 0, 0)

        self.class_buttons_creator()

    def class_buttons_creator(self):
        # TODO: Create an automation
        self.add_widget(QPushButton, "\nBats files executes\nAzure uploader\n", 1, 0, lambda: self.button_clicked(1))
        self.add_widget(QPushButton, "\nAzure files downloader\n", 2, 0, lambda: self.button_clicked(2))
        self.add_widget(QPushButton, "\nStreaming Azure to DFs\n", 3, 0, lambda: self.button_clicked(3))
        self.add_widget(QPushButton, "\nDirect CMD commands exporter\n", 4, 0, lambda: self.button_clicked(4))
        self.add_widget(QPushButton, "\nfunc_azure_uploader\n", 5, 0, lambda: self.button_clicked(5))
        self.add_widget(QPushButton, "\nFree CMD command\n", 6, 0, lambda: self.button_clicked(6))
        self.add_widget(QPushButton, "\nNone\n", 7, 0, lambda: self.button_clicked(7))

        # create subwindow object
        subwindow = QMdiSubWindow()
        # initialize widget
        subwindow.setWidget(self.widget)
        # Insert the subwindow
        self.mdi.addSubWindow(subwindow)

    def button_clicked(self, button_num):
        button_switch_case(button_num)
        label = QLabel(f"Button {button_num} was clicked")

        # create subwindow object
        subwindow = QMdiSubWindow()
        # initialize widget
        subwindow.setWidget(label)
        # Insert the subwindow to the MainWindow
        self.mdi.addSubWindow(subwindow)
        subwindow.show()

    def add_widget(self, widget_type, widget_name, row, col, action=None):
        """Adds a widget to the layout at the specified position."""
        widget = widget_type(widget_name)
        self.layout.addWidget(widget, row, col)
        # If the widget is a QPushButton and an action is defined, connect the action to the button's clicked signal
        if isinstance(widget, QPushButton) and action is not None:
            widget.clicked.connect(action)


def execute_app():
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec_()
