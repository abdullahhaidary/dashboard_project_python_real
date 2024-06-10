import tkinter as tk
from User_Interface import head
from User_Interface import body
from User_Interface import bottom

def create_interface():
    root = tk.Tk()
    root.title("Layout Example")
    width= root.winfo_screenwidth() 
    height= root.winfo_screenheight()
    root.geometry("%dx%d" % (width, height))
    root.state("zoomed")
    main_frame = tk.Frame(root, bg="lightgray")
    main_frame.pack(fill="both", expand=True)

    head.create_head_frame(main_frame)
    body.create_body_frames(main_frame)
    bottom.create_bottom_frame(main_frame)

    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_rowconfigure(1, weight=8)
    main_frame.grid_columnconfigure(0, weight=2)
    main_frame.grid_columnconfigure(1, weight=4)
    main_frame.grid_columnconfigure(2, weight=4)

    root.bind("<Escape>", lambda e: root.destroy())

    return root

if __name__ == "__main__":
    root = create_interface()
    root.mainloop()
