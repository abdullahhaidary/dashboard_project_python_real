import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget,QHBoxLayout,QSizePolicy, QSplitter
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt, QPoint
import importlib
# import multithreading

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abdullah Video Player")
        self.setGeometry(100, 100, 1024, 800)
        
        # Create QLabel widget to display video
        self.left_window = QLabel()
        self.right_window = QLabel()
        
        # Set borders and size policies for QLabel widgets
        self.left_window.setStyleSheet("border: 1px solid black;")
        self.right_window.setStyleSheet("border: 1px solid black;")
        self.left_window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.right_window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Create a QSplitter to ensure equal width
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.left_window)
        splitter.addWidget(self.right_window)
        splitter.setSizes([self.width()//2, self.width()//2])
        
        # Set the central widget with QSplitter
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(splitter)
        self.setCentralWidget(central_widget)
        # Initialize video capture (removed for now)
        # self.capture = cv2.VideoCapture()
        
        # Setup timer to trigger update
        self.timer = QTimer(self)
        
        # Import test module
        module = str(input("Please Enter the module Name"))
        self.test_module = importlib.import_module(module)

        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30 milliseconds (you can adjust this)
        self.capture = cv2.VideoCapture(0)

        # Enable drag and drop
        self.setAcceptDrops(True)

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
                self.left_window.setPixmap(pixmap)
                self.left_window.setScaledContents(True)

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
                self.right_window.setPixmap(pixmap)
                self.right_window.setScaledContents(True)


    def play_video(self, filename):
        # Initialize video capture here
        self.capture = cv2.VideoCapture(filename)
        if not self.capture.isOpened():
            print("Error: Couldn't open video.")
            return
        
        # Start the timer to update frames
        self.timer.start(30)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith(('.mp4', '.avi', '.mkv')):
                self.play_video(path)
                break

    def closeEvent(self, event):
        if hasattr(self, 'capture') and self.capture.isOpened():
            self.capture.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
