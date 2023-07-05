import logging
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import \
    QWidget, QFileDialog, QApplication, QMainWindow, QLabel, QGridLayout, QVBoxLayout, \
    QPushButton, QMdiArea, QMdiSubWindow, QMessageBox, QPlainTextEdit, QComboBox
from PyQt5.QtGui import QIcon
from src.util.buttons_action import *
from config_manager import *
import json


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Daily Report V12")
        self.resize(1200,
                    600)  # self.setFixedSize(800, 600) #  fix the size of the window and prevent the user resizing

        # Set window icon
        self.setWindowIcon(QIcon('src/_ref_/media/v12.ico'))

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

        '''
        ##################################################
        ##################################################
        ##################################################
        '''
        # Create QPlainTextEdit for logs and add it to layout
        self.log_widget = QPlainTextEdit()
        self.log_widget.setReadOnly(True)
        self.layout.addWidget(self.log_widget, 30, 0)

        # Create a handler for logging
        self.log_handler = QTextEditLogger(self.log_widget)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.DEBUG)

        with open('conf.json', 'r') as config_file:
            self.conf_press = json.load(config_file)

        # Create QComboBox for press selection and add it to layout
        self.press_combo_box = QComboBox()
        self.press_combo_box.addItems(self.conf_press['presses'])
        self.press_combo_box.setCurrentText(func_read_log_json()['current_press'])
        self.press_combo_box.currentTextChanged.connect(self.press_changed)
        self.layout.addWidget(self.press_combo_box, 10, 0)

        with open('log.json', 'r') as log_file:
            self.log_app = json.load(log_file)

    @pyqtSlot(str)
    def press_changed(self, text):
        logging.info('Press changed to: ' + text)
        self.log_app['current_press'] = text
        self.log_app['press_sn'] = socket.getfqdn()
        with open('log.json', 'w') as f:
            json.dump(self.log_app, f)

    '''
    ##################################################
    ##################################################
    ##################################################
    '''

    def class_buttons_creator(self):
        # TODO: Create an automation
        self.add_widget(QPushButton, "\nBats files executes\nAzure uploader\n", 1, 0, lambda: self.button_clicked(1))
        self.add_widget(QPushButton, "\nAzure files downloader\n", 2, 0, lambda: self.button_clicked(2))
        # self.add_widget(QPushButton, "\nStreaming Azure to DFs\n", 3, 0, lambda: self.button_clicked(3))
        # self.add_widget(QPushButton, "\nDirect CMD commands exporter\n", 4, 0, lambda: self.button_clicked(4))
        # self.add_widget(QPushButton, "\nfunc_azure_uploader\n", 5, 0, lambda: self.button_clicked(5))
        # self.add_widget(QPushButton, "\nFree CMD command\n", 6, 0, lambda: self.button_clicked(6))
        # self.add_widget(QPushButton, "\nSandBox_Timeline_Report\n", 7, 0, lambda: self.button_clicked(7))
        # self.add_widget(QPushButton, "\nSandBox\n", 8, 0, lambda: self.button_clicked(8))

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


class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = parent

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


def execute_app():
    # pressSN = socket.getfqdn()
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec_()
