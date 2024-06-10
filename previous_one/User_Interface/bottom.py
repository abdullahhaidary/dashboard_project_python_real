import tkinter as tk

def create_bottom_frame(parent_frame):
    bottom_frame = tk.Label(parent_frame, text="Third Row", bg="lightcoral", padx=10, pady=10)
    bottom_frame.grid(row=2, column=0, columnspan=3, sticky="nsew")
    return bottom_frame
