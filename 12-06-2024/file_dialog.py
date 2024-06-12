from tkinter import * 
from tkinter import filedialog 


window = Tk()

def openFile(): 
    filepath = filedialog.askopenfilename()
    print(filepath)
button = Button(text="open", command = openFile) 


button.pack()
window.mainloop()