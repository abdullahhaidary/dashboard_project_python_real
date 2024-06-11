import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import multiprocessing
import numpy as np
from multiprocessing import Event

class Camera:
    @staticmethod
    def capture(url, shared_memory, shape, stop_event):
        cap = cv2.VideoCapture(url)
        while not stop_event.is_set():
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (shape[1], shape[0]))
                shared_memory[:] = frame.flatten()
            else:
                break
        cap.release()

class Interface:
    cameras = [{'name': 'Camera 1', 'url': 'C:\\Users\\PC\\PycharmProjects\\UserInterface\\dashboard\\video.mp4'},
               {'name': 'Camera 2', 'url': 'C:\\Users\\PC\\Downloads\\Video\\Image Classification with Keras, Tensorflow - Cat Vs Dog Prediction - Convolution Neural Networks P1.mp4'},
               {'name':'MIT VIDEO','url':'C:\\Users\PC\\Downloads\\Video\\3.0 MIT 6.S191： Convolutional Neural Networks.mp4'},
               {'name':'Network IP Camera','url':'rtsp://admin:Afghan123@192.168.1.64:554/Stream/Channels'}]
    capture_process = None
    shared_memory = None
    shape = (720, 720, 3)
    photo = None
    camera_label = None

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Camera Detection")
        self.root.geometry("1024x768")
        self.root.state("zoomed")
        self.main_frame = tk.Frame(self.root, bg="lightgray")
        self.main_frame.pack(fill="both", expand=True)

        self.create_body_frames()
        self.create_bottom_frame()

        my_menu = tk.Menu(self.root)
        self.root.config(menu=my_menu)
        file_menu = tk.Menu(my_menu)
        my_menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New File", command=self.test_menu)
        file_menu.add_command(label="Exit", command=self.on_closing)
        self.root.bind("<Escape>", lambda e: self.on_closing())

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.stop_capture_process()
        self.root.destroy()

    def test_menu(self):
        print('hello world')

    def create_body_frames(self):
        self.create_sidebar()
        self.create_left_frame()
        self.create_right_frame()

    def create_bottom_frame(self):
        self.bottom_frame = tk.Label(self.main_frame, text="Third Row", bg="lightcoral", padx=10, pady=10)
        self.bottom_frame.pack(side="bottom", fill="x")

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.main_frame, bg="lightgrey", padx=10, pady=10)
        self.sidebar.pack(side="left", fill="y")
        self.refresh_sidebar()

    def init_camera(self, url):
        if self.capture_process and self.capture_process.is_alive():
            self.stop_capture_process()
            self.shared_memory = None
        cap = cv2.VideoCapture(url)
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to capture frame.")
            cap.release()
            return

        cap.release()

        shared_memory_size = int(np.prod(self.shape) * frame.itemsize)
        self.shared_memory = multiprocessing.Array('b', shared_memory_size)

        # Reset stop_event before starting a new capture process
        self.stop_event = Event()

        self.capture_process = multiprocessing.Process(target=Camera.capture, args=(url, self.shared_memory, self.shape, self.stop_event))
        self.capture_process.start()

        # Start updating the camera feed UI
        self.update_camera_feed()

    def refresh_sidebar(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        add_camera_button = tk.Button(self.sidebar, 
                                      text="Add Camera", 
                                      command=self.add_camera_dialog,
                                      background="#007bff",
                                      foreground="white",
                                      activebackground="#461DF5",
                                      activeforeground="white",
                                      highlightthickness=2,
                                      highlightbackground="#007bff",
                                      width=13, 
                                      height=1,
                                      cursor='hand2',
                                      font=('Arial', 16, 'bold'))
        add_camera_button.pack(pady=(10, 0))

        for i, camera_info in enumerate(self.cameras, start=1):
            camera_name = camera_info["name"]
            camera_url = camera_info["url"]
            box_frame = tk.Frame(self.sidebar, bg="lightblue", padx=10, pady=10, width=10, height=8)
            box_frame.pack(pady=(5, 0))

            box_label = tk.Label(box_frame, bg="lightblue", width=17, height=8, text=camera_name)
            box_label.pack()

            box_label.bind("<Button-1>", lambda event, camera_url=camera_url: self.change_camera(camera_url))

    def stop_capture_process(self):
        if self.capture_process:
            self.stop_event.set()
            self.capture_process.join()
            self.capture_process = None  # Clear the capture process reference
            self.clean_photo()
            print('Capture stopped')
        if self.shared_memory:
            self.shared_memory = None  # Clear shared memory when stopping
            print('Shared memory cleaned ')

    def change_camera(self, camera_url):
        self.init_camera(camera_url)

    def add_camera_dialog(self):
        self.dialog = tk.Toplevel(self.root, width=200, height=500)
        self.dialog.title("Add Camera")
        x = (self.root.winfo_screenwidth() - self.dialog.winfo_reqwidth()) // 2
        y = (self.root.winfo_screenheight() - self.dialog.winfo_reqheight()) // 2
        ttk.Label(self.dialog, text="Camera Name:").grid(row=0, column=0, sticky="w", padx=25, pady=5)
        ttk.Label(self.dialog, text="Camera URL:").grid(row=1, column=0, sticky="w", padx=25, pady=5)
        self.dialog.geometry("+{}+{}".format(x, y))

        camera_name_entry = ttk.Entry(self.dialog, width=40)
        camera_name_entry.grid(row=0, column=1, padx=10, pady=(20, 5))

        camera_url_entry = ttk.Entry(self.dialog, width=40)
        camera_url_entry.grid(row=1, column=1, padx=10, pady=5)

        add_button = ttk.Button(self.dialog, text="Add", command=lambda: self.add_camera(camera_name_entry.get(), camera_url_entry.get()))
        add_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.dialog.protocol("WM_DELETE_WINDOW", self.close_dialog)

    def close_dialog(self):
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.destroy()

    def add_camera(self, camera_name, camera_url):
        if camera_name and camera_url:
            self.cameras.append({'name': camera_name, 'url': camera_url})
            self.refresh_sidebar()
            self.close_dialog()

    def update_camera_feed(self):
        if self.shared_memory:
            try:
                frame_bytes = np.frombuffer(self.shared_memory.get_obj(), dtype=np.uint8)
                frame = frame_bytes.reshape(self.shape)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                img = Image.fromarray(frame)
                # img = img.resize((self.left_frame.winfo_width(), self.left_frame.winfo_height()), resample=Image.LANCZOS)
                self.camera_label.configure(image = None )
                self.photo = ImageTk.PhotoImage(image=img)
                # print(self.photo , )
                self.camera_label.configure(image=self.photo ,width=self.left_frame.winfo_width(), height=self.left_frame.winfo_height())
                self.camera_label.image = self.photo
                print('height ',self.left_frame.winfo_height(),' ,width',self.left_frame.winfo_width())
            except Exception as e:
                print(f"Error updating camera feed: {e}")
        else: 
            print("No camera feed found")
        
        self.root.after(50, self.update_camera_feed)

    def clean_photo(self):
        if self.photo:
            self.photo = None
            self.camera_label.configure(image=None)
            self.camera_label.image = None

    def create_left_frame(self):
        self.left_frame = tk.Frame(self.main_frame, padx=10, pady=10)
        self.left_frame.pack(side="left", fill="both", expand=True)

        self.camera_label = tk.Label(self.left_frame, text="Camera Feed", padx=10, pady=10, width=100, height=100)
        self.camera_label.pack(fill="both", expand=True)

    def create_right_frame(self):
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side="right", fill="y")

        self.right_frame_body = tk.Label(self.right_frame, text="Right Frame", padx=10, pady=10)
        self.right_frame_body.pack(fill="both", expand=True)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Interface()
    app.run()
