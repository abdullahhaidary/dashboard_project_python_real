import cv2
from PIL import Image, ImageTk
import tkinter.messagebox as messagebox

def show_camera_feed(camera_source, label, stop=False):
    def update_frame():
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture frame.")
            return

        # Calculate the aspect ratio
        height, width, _ = frame.shape
        aspect_ratio = width / height
        # Set the height of the label based on the width and aspect ratio
        label.config(height=int(label.winfo_width() / aspect_ratio))

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb_frame)
        photo = ImageTk.PhotoImage(image=image)
        label.config(image=photo)
        label.image = photo

        label.after(10, update_frame)

    if stop:
        label.config(image=None)  # Clear the image
        return

    if isinstance(camera_source, str) and camera_source.isdigit():
        cap = cv2.VideoCapture(int(camera_source))
    else:
        cap = cv2.VideoCapture(camera_source)
    
    if not cap.isOpened():
        messagebox.showerror("Error", "Unable to open camera feed.")
        return

    update_frame()
