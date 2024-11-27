from tkinter import *
from tkinter import ttk

def calculate(*args):
    try:
        value = float(feet.get())
        meters.set(int(0.3048 * value * 10000.0 + 0.5)/10000.0)
        s.configure('TButton', foreground='blue')
    except ValueError:
        pass

def caca(secondFrame):
    s.configure('BB.TButton', background='red', foreground='blue', color='green')
    s.configure('TButton', foreground='red')
    elem = ttk.Button(secondFrame, text="test4", style="BB.TButton")
    elem.grid(column=2, row=2, sticky=(N, W, E, S))
    print(elem['style'])

root = Tk()
root.title("Feet to Meters")

s = ttk.Style()

s.configure('Test.TLabelframe', background='red')

mainframe = ttk.Frame(root)
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

feet = StringVar()
feet_entry = ttk.Entry(mainframe, width=7, textvariable=feet)
feet_entry.grid(column=2, row=1, sticky=(W, E))

meters = StringVar()
ttk.Label(mainframe, textvariable=meters).grid(column=2, row=2, sticky=(W, E))

ttk.Button(mainframe, text="Calculate", command=calculate).grid(column=3, row=3, sticky=W)

ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=W)
ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky=E)
ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)

secondFrame = ttk.Labelframe(mainframe)
secondFrame.grid(column=4, row=4, sticky=(N, W, E, S))

ttk.Button(secondFrame, text="test1").grid(column=1, row=1, sticky=(N, W, E, S))
ttk.Button(secondFrame, text="test2").grid(column=1, row=2, sticky=(N, W, E, S))
ttk.Button(secondFrame, text="test3").grid(column=2, row=1, sticky=(N, W, E, S))

caca(secondFrame)

for child in mainframe.winfo_children(): 
    child.grid_configure(padx=5, pady=5)

feet_entry.focus()
root.bind("<Return>", calculate)

root.mainloop()