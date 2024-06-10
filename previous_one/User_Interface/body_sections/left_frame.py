import tkinter as tk

def create_left_frame(parent_frame):
    left_frame = tk.Frame(parent_frame, bg="lightgreen", padx=10, pady=10)
    left_frame.grid(row=1, column=1, sticky="nsew")
    
    # Adjust the label's width and height to match the sidebar labels
    label = tk.Label(left_frame, text="LEFT FRAME", padx=10, pady=10)
    label.grid(row=0, column=0, sticky="nsew")
    left_frame.camera_label = label
    
    return left_frame
