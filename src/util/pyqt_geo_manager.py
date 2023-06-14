from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QPushButton

class MainWindow_basic(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("Basic My PyQt Application")

        # Create a label widget
        self.label = QLabel("Hello, PyQt!")

        # Set the central widget of the window. Every QMainWindow must have a central widget.
        # Other widgets will be placed on top of or around the central widget.
        self.setCentralWidget(self.label)

class MainWindow_grid(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("Grid My PyQt Application")

        # Create a QWidget that will hold our layout
        widget = QWidget()

        # Create a QGridLayout
        layout = QGridLayout()

        # Add widgets to the layout. The addWidget method takes the widget,
        # then the row, then the column where the top-left corner of the widget should be.
        layout.addWidget(QPushButton("Button 1"), 0, 0)
        layout.addWidget(QPushButton("Button 2"), 0, 1)
        layout.addWidget(QPushButton("Button 3"), 1, 0)

        # Set the layout on the QWidget
        widget.setLayout(layout)

        # Set the central widget of the window.
        self.setCentralWidget(widget)


if __name__ == "__main__":
    app = QApplication([])
    win_basic = MainWindow_basic()
    win_basic.show()
    wind_basic = MainWindow_basic()

    win_grid = MainWindow_grid()
    win_grid.show()
    wind_gris = MainWindow_grid()

    app.exec_()
