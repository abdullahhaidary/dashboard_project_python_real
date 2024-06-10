import tkinter as tk

def create_right_frame(parent_frame):
    right_frame = tk.Frame(parent_frame, bg="lightyellow", padx=10, pady=10, name='right_frame')
    right_frame.grid(row=1, column=2, sticky="nsew")

    body_right = tk.Label(right_frame, text="Right Frame", padx=10, pady=10)
    body_right.grid(row=0, column=0, sticky="nsew")

    right_frame.body_right = body_right

    return right_frame
