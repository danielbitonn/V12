import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
import json

from src.util.buttons_action import *
from config_manager import *
from src.util.utilitiesFunctions import *

from threading import Thread
import time


class ProgressBarWindow(tk.Toplevel):
    def __init__(self, master=None, button_num=None):
        super().__init__(master)
        self.title('Processing...')
        self.geometry('300x100')
        self.label = tk.Label(self, text=f"Button {button_num} is running...")
        self.label.pack()
        self.progress = ttk.Progressbar(self, length=200, mode='indeterminate')
        self.progress.pack(expand=True)


# class TextHandler(logging.Handler):
#     def __init__(self, text):
#         logging.Handler.__init__(self)
#         self.text = text
#
#     def emit(self, record):
#         msg = self.format(record)
#         self.text.insert(tk.END, msg + "\n")
#         self.text.see(tk.END)


# def load_json_tk(jsname):
#     with open(jsname, "r") as file:
#         return json.load(file)

#
# class CustomFormatter_tk(logging.Formatter):
#     def format(self, record):
#         record.asctime = self.formatTime(record, self.datefmt)
#         record.message = record.getMessage()
#         record.name = record.name.replace(',', '').replace('"', '""')
#         record.levelname = record.levelname.replace(',', '').replace('"', '""')
#         record.message = record.message.replace(',', '').replace('"', '""')
#         record.location = f"{record.filename}:{record.lineno}"
#         s = '"%(asctime)s", "%(levelname)s", "%(location)s", "%(message)s"' % record.__dict__
#         return s


class TextHandler(logging.Handler):
    def __init__(self, text):
        logging.Handler.__init__(self)
        self.logger_name = f'{fjp()["paths"]["PushExpDataPathRel"]}/{fjp(jsname="log.json")["current_press"]}/{load_json("log.json")["current_press"]}_{datetime.datetime.now().strftime("%Y-%m-%d")}_{load_json("conf.json")["logApp"]["AppLogName"]}'
        self.text = text
        self.handler = logging.FileHandler(f'{self.logger_name}.csv')
        self.handler.setFormatter(CustomFormatter())

    def emit(self, record):
        msg = self.format(record)
        self.text.insert(tk.END, msg)
        # self.text.insert(tk.END, msg + "\n")
        self.text.see(tk.END)
        self.handler.emit(record)


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.process_thread = None      ###
        self.progress_win = None        ###
        self.title("Daily Report V12")
        self.state('zoomed')  # open the window in full screen

        with open('conf.json', 'r') as config_file:
            self.conf = json.load(config_file)

        # Create two frames for the buttons and log widget
        self.frame_buttons = tk.Frame(self)
        self.frame_buttons.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Logger frame definition
        self.frame_log = tk.Frame(self)
        self.frame_log.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.log_widget = tk.Text(self.frame_log)
        self.log_widget.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.log_handler = TextHandler(self.log_widget)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.NOTSET)

        self.press_combo_box = ttk.Combobox(self.frame_buttons,
                                            values=list(self.conf['presses'].keys()),
                                            width=self.conf['widget_sizes']['width'])
        self.press_combo_box.current(list(self.conf['presses'].keys()).index(func_read_log_json()['current_press']))
        self.press_combo_box.bind("<<ComboboxSelected>>", self.press_changed)
        self.press_combo_box.pack(fill=tk.X)

        with open('log.json', 'r') as log_file:
            self.log_app = json.load(log_file)

        self.class_buttons_creator()

    def press_changed(self, event):
        logging.info('Press changed to: ' + self.press_combo_box.get())
        self.log_app['current_press'] = self.press_combo_box.get()
        self.log_app['press_sn'] = socket.getfqdn()
        with open('log.json', 'w') as f:
            json.dump(self.log_app, f)

    def class_buttons_creator(self):
        button1 = tk.Button(self.frame_buttons,
                            text="\nBats files executes\nAzure uploader\n",
                            command=lambda: self.button_clicked(1),
                            width=self.conf['widget_sizes']['width'],
                            height=self.conf['widget_sizes']['height'])
        button1.pack(fill=tk.X)
        button2 = tk.Button(self.frame_buttons,
                            text="\nAzure files downloader\n",
                            command=lambda: self.button_clicked(2),
                            width=self.conf['widget_sizes']['width'],
                            height=self.conf['widget_sizes']['height'])
        button2.pack(fill=tk.X)
        button3 = tk.Button(self.frame_buttons,
                            text="\nDaily Report Beta\n",
                            command=lambda: self.button_clicked(3),
                            width=self.conf['widget_sizes']['width'],
                            height=self.conf['widget_sizes']['height'])
        button3.pack(fill=tk.X)

    def button_clicked(self, button_num):
        self.start_bar(button_num, button_switch_case(button_num))

        label = tk.Label(self.frame_buttons, text=f"Button {button_num} was clicked")
        label.pack()

    def start_bar(self, button_num, func):
        self.progress_win = ProgressBarWindow(self, button_num)
        self.progress_win.progress.start()

        # Start a separate thread to run the long-running process
        self.process_thread = threading.Thread(target=func)
        self.process_thread.start()

        # Check the process status every 100 ms
        self.after(100, self.check_process_status)

    def check_process_status(self):
        if self.process_thread.is_alive():
            # If the process is still running, check the status again after 100 ms
            self.after(100, self.check_process_status)
        else:
            # If the process is done, stop the progress bar and show the "Done" message
            self.progress_win.progress.stop()
            tk.Label(self.progress_win, text="Done!").pack()
            tk.Button(self.progress_win, text="OK", command=self.progress_win.destroy).pack()


def execute_app():
    # pressSN = socket.getfqdn()
    win = MainWindow()
    win.mainloop()
