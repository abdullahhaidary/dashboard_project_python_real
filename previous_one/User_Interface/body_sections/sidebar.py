import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os
from User_Interface.body_sections.camera_functions import show_camera_feed

CAMERA_DATA_FILE = "camera_data.json"

def load_camera_data():
    if os.path.exists(CAMERA_DATA_FILE):
        with open(CAMERA_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_camera_data(camera_data):
    with open(CAMERA_DATA_FILE, "w") as file:
        json.dump(camera_data, file)

camera_data = load_camera_data()

def create_sidebar(parent_frame, on_camera_change_callback,left_frame):
    print(left_frame)
    sidebar = tk.Frame(parent_frame, bg="lightgrey", padx=10, pady=10)
    sidebar.grid(row=1, column=0, sticky="nsew")

    # Store a flag for each camera to track if it's currently showing or not
    camera_flags = {}

    def refresh_sidebar():
        for widget in sidebar.winfo_children():
            widget.destroy()

        add_camera_button = tk.Button(sidebar, text="Add Camera", command=add_camera)
        add_camera_button.grid(row=0, column=0, padx=10, pady=10)

        for i, (cam, url) in enumerate(camera_data.items(), start=1):
            box_label = tk.Label(sidebar, text=cam, bg="lightblue", padx=10, pady=10, width=17, height=8)
            box_label.grid(row=i, column=0, sticky="nsew")
            box_label.grid_configure(pady=(0, 5))
            box_label.bind("<Button-1>", lambda event, cam=cam, url=url, label=box_label, left_frame=left_frame: toggle_camera(cam, url, label, box_label, left_frame))

            
            box_label.lift()

    def add_camera():
        cam_name = simpledialog.askstring("Input Camera Name", "Enter Camera Name:")
        if not cam_name:
            return
        if cam_name in camera_data:
            messagebox.showerror("Error", "Camera name already exists!")
            return

        url = simpledialog.askstring("Input URL or Webcam Index", f"Enter URL for {cam_name} or enter '0' for the default webcam:")
        if not url:
            return
        if cam_name and url:
            camera_data[cam_name] = url
            save_camera_data(camera_data)
            refresh_sidebar()

    def toggle_camera(cam_name, url, label, box_label, left_frame):
        if cam_name in camera_flags and camera_flags[cam_name]:
            # Stop the camera feed and release it
            show_camera_feed(url, label, stop=True)
            camera_flags[cam_name] = False
            box_label.config(bg="lightblue")  # Reset background color
            # Clear the camera feed from the left frame label
            left_frame.config(image=None)  # Remove image from the left frame
        else:
            # Show the camera feed
            show_camera_feed(url, label)
            camera_flags[cam_name] = True
            box_label.config(bg="lightgreen")  # Change background color to indicate it's active
            # Display the camera feed in the left frame label
            show_camera_feed(url, left_frame)  # Display camera feed in the left frame


    refresh_sidebar()
    return sidebar
