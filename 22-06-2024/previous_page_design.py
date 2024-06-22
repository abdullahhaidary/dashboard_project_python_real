import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGridLayout, QSizePolicy, QLineEdit, QPushButton
import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
import importlib

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.test_module = importlib.import_module(module)
        self.timer = QTimer(self)
        self.capture = cv2.VideoCapture(0)
        
        self.initUI()
        
        # Bring window to the front once
        self.raise_()
        self.activateWindow()

    def initUI(self):
        # Set window title
        self.setWindowTitle('Script Dashboard')

        # Create the main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Create the menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        # Create exit action
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Create the grid layout for the top section
        top_layout = QGridLayout()

        # First column for cameras
        cameras_label = QLabel('Cameras')
        cameras_label.setStyleSheet("background-color: lightgray;")
        top_layout.addWidget(cameras_label, 0, 0)

        # Second column for left camera
        self.left_camera_label = QLabel('Left Camera')
        self.left_camera_label.setStyleSheet("background-color: lightblue;")
        top_layout.addWidget(self.left_camera_label, 0, 1)
        self.left_camera_label.setScaledContents(True)
        self.left_camera_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Third column for right camera
        self.right_camera_label = QLabel('Right Camera')
        self.right_camera_label.setStyleSheet("background-color: lightgreen;")
        top_layout.addWidget(self.right_camera_label, 0, 2)
        self.right_camera_label.setScaledContents(True)
        self.right_camera_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set column stretch
        top_layout.setColumnStretch(0, 1)
        top_layout.setColumnStretch(1, 5)  # Adjusted stretch factor
        top_layout.setColumnStretch(2, 5)  # Adjusted stretch factor

        # Create the bottom layout for scripts
        bottom_layout = QHBoxLayout()
        scripts_label = QLabel('Scripts')
        scripts_label.setStyleSheet("background-color: lightyellow;")
        bottom_layout.addWidget(scripts_label)
        # Add script name input field
        self.script_name_input = QLineEdit(self)
        bottom_layout.addWidget(self.script_name_input)

        # Add "Add" button
        add_button = QPushButton('Add', self)
        add_button.clicked.connect(self.change_module)
        bottom_layout.addWidget(add_button)

        # Set stretch factors for main layout
        main_layout.addLayout(top_layout)
        main_layout.addStretch(0)  # Stretch to fill remaining space
        main_layout.addLayout(bottom_layout)
        main_layout.setStretch(0, 9)  # Top section (90% height)
        main_layout.setStretch(2, 1)  # Bottom section (10% height)

        # Set main widget as the central widget
        self.setCentralWidget(main_widget)

        # Set window size
        self.resize(800, 600)

        # Show minimized by default
        self.showMaximized()
        self.resizeEvent(None)  # Explicitly call resize event
        
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30 milliseconds (you can adjust this)

    def change_module(self):
        module_name = self.script_name_input.text()
        if module_name:
            self.test_module = importlib.import_module(module_name)

    def resizeEvent(self, event):
        # Call the parent's resize event to handle the resize properly
        super().resizeEvent(event)
        # Update the layout after resizing
        self.left_camera_label.setScaledContents(True)
        self.right_camera_label.setScaledContents(True)

    def update_frame(self):
        if self.capture is not None and self.capture.isOpened():
            left_frame = self.test_module.update_frame(self.capture)
            if left_frame is not None:
                # Check if the frame is RGB or grayscale
                if len(left_frame.shape) == 3:
                    h, w, ch = left_frame.shape
                    img = QImage(left_frame.data, w, h, ch * w, QImage.Format_RGB888)
                else:
                    h, w = left_frame.shape
                    img = QImage(left_frame.data, w, h, w, QImage.Format_Grayscale8)
                
                # Display QImage in QLabel
                pixmap = QPixmap.fromImage(img)
                self.left_camera_label.setPixmap(pixmap)
                self.left_camera_label.setScaledContents(True)

            right_frame = self.test_module.update_frame_original(self.capture)
            if right_frame is not None:
                # Check if the frame is RGB or grayscale
                if len(right_frame.shape) == 3:
                    h, w, ch = right_frame.shape
                    img = QImage(right_frame.data, w, h, ch * w, QImage.Format_RGB888)
                else:
                    h, w = right_frame.shape
                    img = QImage(right_frame.data, w, h, w, QImage.Format_Grayscale8)
                
                # Display QImage in QLabel
                pixmap = QPixmap.fromImage(img)
                self.right_camera_label.setPixmap(pixmap)
                self.right_camera_label.setScaledContents(True)

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    module = str(input("Please Enter the module Name:"))

    main()
