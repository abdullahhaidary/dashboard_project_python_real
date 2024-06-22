import sys
import os
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGridLayout, QSizePolicy, QComboBox, QFileDialog, QMessageBox,QFrame,QScrollArea
import cv2
from PyQt5.QtGui import QImage, QPixmap,QIcon
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QTimer, Qt
import json
import importlib

# Determine the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')  # Directory where scripts are stored
CAMERA_DATA_FILE = "camera_data.json"


if not os.path.exists(CAMERA_DATA_FILE):
    with open(filename, 'w') as file:
        json.dump({}, file)


# Create the scripts directory if it doesn't exist
if not os.path.exists(SCRIPTS_DIR):
    os.makedirs(SCRIPTS_DIR)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('ME.jpg'))


        # Add SCRIPTS_DIR to the system path
        sys.path.append(SCRIPTS_DIR)

        # Get the first available script in the scripts directory
        available_scripts = [f[:-3] for f in os.listdir(SCRIPTS_DIR) if f.endswith('.py')]
        if not available_scripts:
            QMessageBox.critical(self, "Error", "No scripts found in the scripts directory.")
            self.test_module = None
        else:
            default_module = available_scripts[0]
            try:
                self.test_module = importlib.import_module(default_module)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load default script '{default_module}': {e}")
                self.test_module = None

        self.timer = QTimer(self)
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            self.capture = None
        
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

        # Create upload action
        upload_action = QAction('Upload Script', self)
        upload_action.triggered.connect(self.upload_script)
        file_menu.addAction(upload_action)

        # Create the grid layout for the top section
        top_layout = QGridLayout()

        # First column for cameras
        cameras_frame = QFrame()
        cameras_frame.setStyleSheet("text-align:center;")
        # cameras_frame.setFixedWidth(300)
        cameras_layout = QVBoxLayout(cameras_frame)

        try:
            with open(CAMERA_DATA_FILE, 'r') as file:
                camera_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            camera_data = []
        
        if camera_data:
            for camera in camera_data:
                camera_label = QLabel(f'{camera["camera"]}', cameras_frame)
                camera_label.setStyleSheet("border: 1px solid black;")
                camera_label.setFixedSize(150, 150)
                camera_label.mousePressEvent = lambda event,name = camera["camera"], url = camera["url"]:self.display_camera_feed(name,url)
                cameras_layout.addWidget(camera_label)
        # else:
        #     for i in range(1, 10):
        #         box_label = QLabel(f'Box{i}', cameras_frame)
        #         box_label.setStyleSheet("background-color: lightblue; border: 1px solid black;")
        #         box_label.setFixedSize(150, 150)
        #         cameras_layout.addWidget(box_label)

        scroll_area = QScrollArea()
        # scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable horizontal scroll bar
        scroll_area.setWidget(cameras_frame)

        top_layout.addWidget(scroll_area, 0, 0, 6, 1)
        cameras_frame.setMinimumWidth(scroll_area.width())

        add_camera_button = QPushButton('Add Camera', self)
        add_camera_button.clicked.connect(self.add_camera_dialog)
        top_layout.addWidget(add_camera_button, 6, 0)

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

        # Add script selection dropdown
        self.script_selector = QComboBox(self)
        self.update_script_list()
        self.script_selector.currentTextChanged.connect(self.change_module)
        bottom_layout.addWidget(self.script_selector)

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



    def closeEvent(self, event):
        if self.capture is not None and self.capture.isOpened():
            self.capture.release()
        event.accept()

    def display_camera_feed(self, camera_name, camera_url):
        if camera_url:
            if camera_url.isdigit():
                camera_url = int(camera_url)
            self.capture = cv2.VideoCapture(camera_url)
        if camera_name == 'Left Camera':
            self.left_camera_label.setText("Capture not available")
            self.left_camera_label.setAlignment(Qt.AlignCenter)
        elif camera_name == 'Right Camera':
            self.right_camera_label.setText("Capture not available")
            self.right_camera_label.setAlignment(Qt.AlignCenter)

    
    def add_camera_dialog(self):
        dialog = AddCameraDialog(self)
        if dialog.exec_():
            camera_name = dialog.camera_name
            camera_url = dialog.camera_url
            if camera_name and camera_url:
                # Call method to add camera to Camera class and JSON file
                self.add(camera_name, camera_url)
                # Optionally update UI or notify user
                QMessageBox.information(self, "Success", f"Camera '{camera_name}' added successfully.")
                self.update_script_list()  # Update script list or UI as needed

    def add(self, camera_name, camera_url):
        # Check if the file exists and read the data
        CAMERA_DATA_FILE = "camera_data.json"

        try:
            if os.path.exists(CAMERA_DATA_FILE):
                with open(CAMERA_DATA_FILE, 'r') as file:
                    camera_data = json.load(file)
            else:
                camera_data = []
        except (FileNotFoundError, json.JSONDecodeError):
            camera_data = []

        # Ensure the data is a list
        if not isinstance(camera_data, list):
            camera_data = []

        # Check if the camera name or URL already exists
        for camera in camera_data:
            if camera["camera"] == camera_name or camera["url"] == camera_url:
                print("Error: Camera name or URL already exists.")
                return

        # Determine the new ID
        if camera_data:
            max_id = max(camera["id"] for camera in camera_data)
            new_id = max_id + 1
        else:
            new_id = 0

        # Add the new camera data
        new_camera = {"id": new_id, "camera": camera_name, "url": camera_url}
        camera_data.append(new_camera)

        # Write the updated data back to the JSON file
        with open(CAMERA_DATA_FILE, "w") as file:
            json.dump(camera_data, file, indent=4)
        print("Camera added successfully.")

                    
    def update_script_list(self):
        self.script_selector.clear()
        for script in os.listdir(SCRIPTS_DIR):
            if script.endswith('.py'):
                module_name = script[:-3]  # Remove '.py' extension
                self.script_selector.addItem(module_name)

    def change_module(self, module_name):
        if module_name:
            try:
                self.test_module = importlib.import_module(module_name)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load script '{module_name}': {e}")
                self.test_module = None

    def resizeEvent(self, event):
        # Call the parent's resize event to handle the resize properly
        super().resizeEvent(event)
        # Update the layout after resizing
        self.left_camera_label.setScaledContents(True)
        self.right_camera_label.setScaledContents(True)

    def update_frame(self):
        if self.capture is None or not self.capture.isOpened():
            self.left_camera_label.setText("Camera not available")
            self.left_camera_label.setAlignment(Qt.AlignCenter)
            self.right_camera_label.setText("Camera not available")
            self.right_camera_label.setAlignment(Qt.AlignCenter)
            return

        if self.test_module is None:
            self.left_camera_label.setText("Script invalid")
            self.left_camera_label.setAlignment(Qt.AlignCenter)
            self.right_camera_label.setText("Script invalid")
            self.right_camera_label.setAlignment(Qt.AlignCenter)
            return

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
        else:
            self.left_camera_label.setText("Cannot capture the camera")
            self.left_camera_label.setAlignment(Qt.AlignCenter)

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
        else:
            self.right_camera_label.setText("Cannot capture the camera")
            self.right_camera_label.setAlignment(Qt.AlignCenter)

    def upload_script(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Upload Script", "", "Python Files (*.py);;All Files (*)", options=options)
        if file_name:
            try:
                script_name = os.path.basename(file_name)
                dest_path = os.path.join(SCRIPTS_DIR, script_name)
                shutil.copy(file_name, dest_path)
                self.update_script_list()
                QMessageBox.information(self, "Success", f"Script {script_name} uploaded successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to upload script: {e}")


from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QDialogButtonBox, QVBoxLayout

class AddCameraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Add Camera')

        self.camera_name = None
        self.camera_url = None

        layout = QVBoxLayout(self)

        self.name_label = QLabel('Camera Name:')
        self.name_input = QLineEdit()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        self.url_label = QLabel('Camera URL:')
        self.url_input = QLineEdit()
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self):
        self.camera_name = self.name_input.text().strip()
        self.camera_url = self.url_input.text().strip()
        if not self.camera_name or not self.camera_url:
            QMessageBox.warning(self, "Error", "Please enter both Camera Name and URL.")
        else:
            super().accept()


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    import sys
    import os
    from PyQt5.QtWidgets import QApplication

    # Check if running as a script or frozen executable
    if getattr(sys, 'frozen', False):
        os.chdir(sys._MEIPASS)
    
    main()
