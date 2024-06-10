import tkinter as tk
from Camera import Camera
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import threading

class Interface:
    cameras = Camera()

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Camera Detection")
        self.root.geometry("1024x768")
        self.root.state("zoomed")
        self.caps = []
        self.main_frame = tk.Frame(self.root, bg="lightgray")
        self.main_frame.pack(fill="both",expand=True)

        self.create_body_frames()
        self.create_bottom_frame()
        self.main_frame.grid_rowconfigure(0, weight=8)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0)
        self.main_frame.grid_columnconfigure(1, weight=4)
        self.main_frame.grid_columnconfigure(2, weight=4)
        self.root.protocol("WM_DELETE_WINDOW", self.on_destroy)
        my_menu = tk.Menu(self.root)
        self.root.config(menu=my_menu)
        file_menu = tk.Menu(my_menu)
        my_menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New File", command=self.test_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # Show the first camera feed in the left frame by default
        self.show_first_camera_in_left_frame()
    def on_destroy(self):
        for cap in self.caps:
            cap.release()  # Release each VideoCapture object
            print("released")
    def test_menu(self):
        print("Clicked")

    def create_body_frames(self):
        self.create_sidebar()
        self.create_left_frame()
        self.create_right_frame()

    def create_bottom_frame(self):
        self.bottom_frame = tk.Label(self.main_frame, text="Third Row", bg="lightcoral", padx=10, pady=10)
        self.bottom_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.main_frame, bg="lightgrey", padx=10, pady=10)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.refresh_sidebar()

    def refresh_sidebar(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        add_camera_button = tk.Button(self.sidebar, text="Add Camera", command=self.add_camera_dialog)
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
            box_label = tk.Label(box_frame, bg="lightblue", width=17, height=8)
            box_label.grid(row=0, column=0, sticky="nsew")
            box_label.bind("<Button-3>", lambda event, menu=camera_menu: self.show_menu(event, menu))

            # Start a thread to update the camera feed
            threading.Thread(target=self.update_camera_feed, args=(box_label, camera_url, box_frame, False)).start()

    def update_camera_feed(self, label, url, container, resize_to_container):
        if url.isdigit():
            url = int(url)

        cap = cv2.VideoCapture(url)
        self.caps.append(cap)

        def update():
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)

                if resize_to_container:
                    # Get the container dimensions
                    container_width = container.winfo_width()
                    container_height = container.winfo_height()
                    # Ensure the container dimensions are valid
                    if container_width > 0 and container_height > 0:
                        img = img.resize((container_width, container_height), resample=Image.LANCZOS)

                imgtk = ImageTk.PhotoImage(image=img)
                label.imgtk = imgtk
                label.config(image=imgtk)
                # Schedule the next update after a delay (e.g., 100 milliseconds)
                self.root.after(100, update)
            else:
                label.config(text="Camera not available", image='', compound='center')

        # Start the update loop
        update()



    def show_menu(self, event, menu):
        menu.post(event.x_root, event.y_root)

    def delete_camera(self, info):
        self.cameras.remove(camera_id=info["id"])
        self.refresh_sidebar()

    def add_camera_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Camera")
        x = (self.root.winfo_screenwidth() - dialog.winfo_reqwidth()) // 2
        y = (self.root.winfo_screenheight() - dialog.winfo_reqheight()) // 2
        ttk.Label(dialog, text="Camera Name:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(dialog, text="Camera URL:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        dialog.geometry("+{}+{}".format(x, y))
        camera_name_entry = ttk.Entry(dialog, width=40)
        camera_name_entry.grid(row=0, column=1, padx=10, pady=5)
        camera_url_entry = ttk.Entry(dialog, width=40)
        camera_url_entry.grid(row=1, column=1, padx=10, pady=5)

        def add_camera():
            camera_name = camera_name_entry.get()
            camera_url = camera_url_entry.get()
            if camera_name and camera_url:
                self.cameras.add(camera_name=camera_name, camera_url=camera_url)
                self.refresh_sidebar()
                dialog.destroy()

        add_button = ttk.Button(dialog, text="Add", command=add_camera)
        add_button.grid(row=2, column=0, columnspan=2, pady=10)

    def create_left_frame(self):
        self.left_frame = tk.Frame(self.main_frame, bg="lightgreen", padx=10, pady=10)
        self.left_frame.grid(row=0, column=1, sticky="nsew")
        self.left_frame.grid_rowconfigure(0, weight=1)  # Ensure the left frame fills the available space
        self.left_frame.grid_columnconfigure(0, weight=1)  # Ensure the left frame fills the available space

        self.camera_label = tk.Label(self.left_frame, text="LEFT FRAME", padx=10, pady=10, width=100, height=100)
        self.camera_label.grid(row=0, column=0, sticky="nsew")


    def create_right_frame(self):
        self.right_frame = tk.Frame(self.main_frame, bg="lightyellow", padx=10, pady=10)
        self.right_frame.grid(row=0, column=2, sticky="nsew")
        self.right_frame_body = tk.Label(self.right_frame, text="Right Frame", padx=10, pady=10)
        self.right_frame_body.grid(row=0, column=0, sticky="nsew")

    def show_first_camera_in_left_frame(self):
        all_cameras = self.cameras.get_all()
        if all_cameras:
            first_camera = all_cameras[0]
            camera_url = first_camera["url"]
            threading.Thread(target=self.update_camera_feed, args=(self.camera_label, camera_url, self.left_frame, True)).start()

    def run(self):
        self.root.mainloop()

