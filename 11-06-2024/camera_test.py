from Camera import Camera
import numpy as np
import multiprocessing
import cv2
import tkinter as tk
from PIL import Image, ImageTk

def update_ui(shared_memory, shape, label, root): 
    # Convert the shared memory buffer to a numpy array
    frame_bytes = shared_memory.get_obj()
    frame = np.frombuffer(frame_bytes, dtype=np.uint8).reshape(shape)

    # Convert frame from BGR to RGB and create the PIL Image and PhotoImage
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    photo = ImageTk.PhotoImage(image=img)

    # Update the label with the new frame
    label.configure(image=photo)
    label.image = photo

    # Schedule the next UI update
    root.after(200, update_ui, shared_memory, shape, label, root)  # Adjusted to 50ms

def on_closing(root, capture_process, stop_event):
    if capture_process.is_alive():
        stop_event.set()
        capture_process.join()
    root.quit()

def main(camera_url):
    # Open the video capture
    if camera_url.isdigit():
        camera_url = int(camera_url)
    cap = cv2.VideoCapture(camera_url)
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to capture frame.")
        cap.release()
        exit()
    cap.release()

    # Define the shape for the shared memory
    shape = (320, 320, 3)
    shared_memory_size = int(np.prod(shape) * frame.itemsize)
    shared_memory = multiprocessing.Array('b', shared_memory_size)

    # Start the camera capture process
    stop_event = multiprocessing.Event()
    capture_process = multiprocessing.Process(target=Camera.capture, args=(camera_url, shared_memory, shape, stop_event))
    capture_process.start()

    # Initialize Tkinter window
    root = tk.Tk()
    root.title("Live Camera Feed")

    # Create a label to display the video feed
    label = tk.Label(root)
    label.pack()

    # Start the UI update loop
    update_ui(shared_memory, shape, label, root)

    # Set the protocol for closing the window
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, capture_process, stop_event))
    root.mainloop()

if __name__ == "__main__":
    camera_url = "C:\\Users\\PC\\PycharmProjects\\UserInterface\\dashboard\\video.mp4"
    main(camera_url)
