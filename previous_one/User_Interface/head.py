import tkinter as tk

def create_head_frame(parent_frame):
    head_frame = tk.Label(parent_frame, text="First Row", bg="lightblue", padx=10, pady=10)
    head_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")
    return head_frame
