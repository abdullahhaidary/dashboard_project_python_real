import tkinter as tk
from Camera import Camera
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import threading
import multiprocessing
import numpy as np 
from multiprocessing import Event
import subprocess
from scripts import Script
class Interface:
    cameras = Camera()
    capture_process = None
    shared_memory=None
    shape = (920, 760, 3)
    script = Script()
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Camera Detection")
        self.root.geometry("1024x768")
        self.root.state("zoomed")
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both",expand=True)
        self.create_body_frames()
        self.create_bottom_frame()
        self.main_frame.grid_rowconfigure(0, weight=8)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=1)
        # self.init_camera("C:\\Users\\PC\\PycharmProjects\\UserInterface\\dashboard\\video.mp4")
        
        my_menu = tk.Menu(self.root)
        self.root.config(menu=my_menu)
        file_menu = tk.Menu(my_menu)
        my_menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New File", command=self.test_menu)
        file_menu.add_command(label="Exit", command=self.on_closing)
        self.root.bind("<Escape>", lambda e: self.on_closing())
        
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.on_closing())
        # Show the first camera feed in the left frame by default
        # self.show_first_camera_in_left_frame()
    def on_closing(self):
        # if self.capture_process and self.capture_process.is_alive():
        self.stop_event.set()  # Signal the capture process to stop
        # self.capture_process.join(timeout=5)  # Wait for the capture process to terminate
        self.root.destroy()  # Quit the Tkinter application
        self.root.quit() # Exit the Tkinter application
        # Ensure all threads are stopped
        for thread in threading.enumerate():
            if thread is not threading.main_thread():
                thread.join(timeout=1)
    def test_menu():
        print('hello world')
    def create_body_frames(self):
        self.create_sidebar()
        self.create_left_frame()
        self.create_right_frame()
    
    def create_bottom_frame(self):
        self.bottom_frame = tk.Frame(self.main_frame)
        self.bottom_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")

        # Create a Canvas widget for scrolling content
        canvas = tk.Canvas(self.bottom_frame, bg="white", width=200, height=self.bottom_frame.winfo_height()+60, scrollregion=(0, 0, 800, 200))

        # Add a horizontal scrollbar to the Canvas
        scroll_x = tk.Scrollbar(self.bottom_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.config(xscrollcommand=scroll_x.set)

        # Create a frame inside the Canvas to hold your content (example with labels)
        content_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=content_frame, anchor=tk.NW)
        add_button = tk.Button(content_frame, text="Add Script", command = self.script.add_script)
        add_button.grid(row=0, column=0, padx=10, pady=10)
        all_scripts = self.script.fetch_all_scripts()
        print(all_scripts)
        # Add some labels (or other widgets) to the content frame
        for i, script in enumerate(all_scripts, start=1):
            label = tk.Label(content_frame, text=f"Label {i}: {script}", padx=10, pady=10)
            label.grid(row=0, column=i, padx=10, pady=10)
            label.bind("<Button-1>", lambda e, s=script["script_path"]: self.process_the_picture(s))
        # Update scroll region when resizing content
        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    import subprocess

    def process_the_picture(self, script):
        try:
            result = subprocess.run(
                ["python", script],
                capture_output=True,
                text=True,
                check=True  # This will raise an exception if the script fails
            )
            # Get the output from the script
            output = result.stdout.strip()
            print(output)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e.stderr}")
        except FileNotFoundError:
            print(f"The file {script} was not found.")

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.main_frame, bg="lightgrey", padx=10, pady=10)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.refresh_sidebar()

    def init_camera(self, url):
        if self.capture_process and self.capture_process.is_alive():
            self.stop_capture_process()

        self.stop_event = Event()

        # Attempt to capture the first frame
        cap = cv2.VideoCapture(url)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            # If unable to capture frame, display error message
            self.clean_photo()
            # self.camera_label.configure(text="Unable to capture frame. Check your input.")
            self.camera_label = tk.Label(self.left_frame,bg="#E56D53", text="Unable to show camera input", font=("Helevica",18), width=1, height=1)
            self.camera_label.grid(row=0, column=0, sticky="nsew")
            self.camera_label
            # Release resources or handle the error appropriately
            cap.release()
            return

        # If frame captured successfully, proceed with initialization
        self.original_shape = frame.shape
        shared_memory_size = int(np.prod(self.original_shape) * frame.itemsize)
        self.shared_memory = multiprocessing.Array('b', shared_memory_size)

        # Start the camera capture process
        self.capture_process = multiprocessing.Process(target=Camera.capture,
                                                    args=(url, self.shared_memory, self.shape, self.stop_event))
        self.cameras.start_recording()
        self.capture_process.start()

        self.update_ui()


        


    def refresh_sidebar(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        # Create and place the primary styled button
        add_camera_button = tk.Button(self.sidebar, 
                              text="Add Camera", 
                              command=self.add_camera_dialog,
                              background="#007bff",  # Bootstrap primary color
                              foreground="white",    # Text color
                              activebackground="#461DF5",  # Darker shade for active state
                              activeforeground="white",
                              highlightthickness=2,
                              highlightbackground="#007bff",
                              width=13, 
                              height=1,
                              cursor='hand2',
                              font=('Arial', 16, 'bold'))  # Corrected font parameter

        add_camera_button.grid(row=0, column=0, padx=10, pady=10)

        all_cameras = self.cameras.get_all()

        for i, camera_info in enumerate(all_cameras, start=1):
            camera_name = camera_info["camera"]
            camera_url = camera_info["url"]
            box_frame = tk.Frame(self.sidebar, bg="lightblue", padx=10, pady=10,width=10, height=8)
            box_frame.grid(row=i, column=0, sticky="nsew")
            box_frame.grid_configure(pady=(0, 5))

            # Create a menu for the camera box
            camera_menu = tk.Menu(box_frame, tearoff=0)
            camera_menu.add_command(label="Edit", command=lambda info=camera_info: self.edit_camera(info))
            camera_menu.add_command(label="Delete", command=lambda info=camera_info: self.delete_camera(info))

            # Create a label within the frame to show camera feed
            box_label = tk.Label(box_frame, bg="lightblue", width=17, height=8, text=camera_name)
            box_label.grid(row=0, column=0, sticky="nsew")
            box_label.bind("<Button-3>", lambda event, menu=camera_menu: self.show_menu(event, menu))
            box_label.bind("<Button-1>", lambda event, camera_url=camera_url, menu=camera_menu: self.change_camera(camera_url))


            # Start a thread to update the camera feed
            # threading.Thread(target=self.update_camera_feed, args=(box_label, camera_url, box_frame, False)).start()
    def stop_capture_process(self):
            if self.capture_process:
                self.stop_event.set()
                self.capture_process.join()
                self.capture_process = None  # Clear the capture process reference
                self.clean_photo()
            if self.shared_memory:
                self.shared_memory = None  # Clear shared memory when stopping
    def change_camera(self, camera_url):
        self.init_camera(camera_url)
    def clean_photo(self):
        self.photo = None
        self.camera_label.configure(image=None)
        self.camera_label.image = None

    def show_menu(self, event, menu):
        menu.post(event.x_root, event.y_root)

    def delete_camera(self, info):
        self.cameras.remove(camera_id=info["id"])
        self.refresh_sidebar()
    

    def add_camera_dialog(self):
        if hasattr(self, 'dialog') and self.dialog:
        # Dialog is already open, do nothing
            return
        # Create the dialog window
        self.dialog = tk.Toplevel(self.root, width=200, height=500)
        self.dialog.title("Add Camera")
        x = (self.root.winfo_screenwidth() - self.dialog.winfo_reqwidth()) // 2
        y = (self.root.winfo_screenheight() - self.dialog.winfo_reqheight()) // 2
        ttk.Label(self.dialog, text="Camera Name:").grid(row=0, column=0, sticky="w", padx=25, pady=5.)
        ttk.Label(self.dialog, text="Camera URL:").grid(row=1, column=0, sticky="w", padx=25, pady=5)
        self.dialog.geometry("+{}+{}".format(x, y))

        camera_name_entry = ttk.Entry(self.dialog, width=40)
        camera_name_entry.grid(row=0, column=1, padx=10, pady=5)

        camera_name_entry.grid(row=0, column=1, padx=10, pady=(20, 5))
        camera_url_entry = ttk.Entry(self.dialog, width=40)

        camera_url_entry.grid(row=1, column=1, padx=10, pady=5)
        def add_camera():
                camera_name = camera_name_entry.get()
                camera_url = camera_url_entry.get()
                if camera_name and camera_url:
                    self.cameras.add(camera_name=camera_name, camera_url=camera_url)
                    self.refresh_sidebar()
                    self.dialog.destroy()

        add_button = ttk.Button(self.dialog, text="Add", command=add_camera)
        add_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Ensure the dialog is destroyed properly when closed
        self.dialog.protocol("WM_DELETE_WINDOW", self.close_dialog)

        def close_dialog(self):
            # Destroy the dialog and set dialog attribute to None
            if hasattr(self, 'dialog') and self.dialog:
                self.dialog.destroy()
                self.dialog = None

        def add_camera():
            camera_name = camera_name_entry.get()
            camera_url = camera_url_entry.get()
            if camera_name and camera_url:
                self.cameras.add(camera_name=camera_name, camera_url=camera_url)
                self.refresh_sidebar()
                self.dialog.destroy()

        add_button = ttk.Button(self.dialog, text="Add", command=add_camera)
        add_button.grid(row=2, column=0, columnspan=2, pady=10)



    def update_ui(self): 
        # Convert the shared memory buffer to a numpy array
        if self.shared_memory:
            try:
                frame_bytes = self.shared_memory.get_obj()
                frame = np.frombuffer(frame_bytes, dtype=np.uint8).reshape(self.original_shape)

                # Convert frame from BGR to RGB and create the PIL Image and PhotoImage
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                self.camera_label.configure(image = None )
                # img = img.resize((self.left_frame.winfo_width(), self.left_frame.winfo_height()) , resample = Image.LANCZOS )
                self.photo = ImageTk.PhotoImage(image=img)

                # Update the label with the new frame
                self.camera_label.configure(image=self.photo)
                self.camera_label.image = self.photo
            except Exception as e: 
                # self.camera_label.configure(text="Unable To Show Capture, Please Check Your Input")
                print(f"Error updating Camera feed: {e}")
        # Schedule the next UI update
        self.left_frame.after(33, self.update_ui)  # Adjusted to 50ms




    def create_left_frame(self):
        self.left_frame = tk.Frame(self.main_frame, padx=10, pady=10)
        self.left_frame.grid(row=0, column=1, sticky="nsew")
        self.left_frame.grid_rowconfigure(0, weight=1)  # Ensure the left frame fills the available space
        self.left_frame.grid_columnconfigure(0, weight=1)  # Ensure the left frame fills the available space

        self.camera_label = tk.Label(self.left_frame, text="LEFT FRAME", width=1, height=1)
        self.camera_label.grid(row=0, column=0, sticky="nsew")
        # self.init_camera("rtsp://admin:Afghan123@192.168.1.64:554/Stream/Channels")
        for i, camera_info in enumerate(self.cameras.get_all(), start=1):
            self.change_camera(camera_info["url"])
            break;


    def create_right_frame(self):
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=2, sticky="nsew")
        self.right_frame_body = tk.Label(self.right_frame, text="Right Frame", padx=10, pady=10)
        self.right_frame_body.grid(row=0, column=0, sticky="nsew")


    def run(self):
        self.root.mainloop()

