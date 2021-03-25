import webbrowser
from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog

from closest_location_take2 import getLongLat, closest_location
from create_DB import create_DB
from query import query

ariel14bold = 'Ariel 14 bold'
ariel10 = 'Ariel 10'


def callback(event):
    webbrowser.open_new(event.widget.cget("text"))


def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()


root = tk.Tk()

f1 = Frame(root)
f2 = Frame(root)
f3 = Frame(root)
f4 = Frame(root)

for frame in (f1, f2, f3, f4):
    frame.grid(row=0, column=0, sticky='news')

style = ttk.Style(root)
style.theme_use("clam")

ttk.Label(f1,
          text="Welcome to 'WhereWasI?'", font=ariel14bold).grid(row=0, columnspan=3, pady=20, padx=80)
tk.Label(f1,
         text="An application for finding landmarks in Delft!", font=ariel10).grid(row=1, columnspan=3, pady=4)
tk.Label(f1,
         text="Choose one of the actions below:", font=ariel10).grid(row=2, columnspan=3, pady=4)

# Default coordinates
coord = [51.9, 4.36]

landmark = "NOT IDENTIFIED"
res_landmark = 'NOT IDENTIFIED'


def file_explorer():
    global landmark
    filename = filedialog.askopenfilenames(
        filetypes=[
            ("MP4", "*.mp4"),
            ("AVI", "*.avi"),
            ("3GP", "*.3gp"),
            ("JPG", ".jpg"),
            ("All files", "*")])[0]

    # DO THE COMPUTATIONS AND STORE THE RESULTS FOR LANDMARK, COORDX AND COORDY

    try:
        print(filename)

        create_DB("./dbImages/")
        (long, lat) = getLongLat(filename)

        print(long, lat)

        if (long, lat) != (0, 0):
            landmark = closest_location(lat, long)

        print(landmark)

        res_landmark = query('db/MMA.db', filename)

        locations = {
            "Nieuwe Kerk": [52.012468, 4.360922],
            "Stadhuis": [52.011548, 4.358495],
            "Oude Jan": [52.012707, 4.355859],
            "NOT IDENTIFIED": [38.8714674, -77.0552931]
        }

        print(res_landmark)

        lbl = tk.Label(f2, text="http://www.google.com/maps/place/" + str(locations[res_landmark][0]) + "," + str(
            locations[res_landmark][1]), fg="blue",
                       font='Ariel 12', pady=2)

        lbl.grid(row=5, columnspan=2)
        lbl.bind("<Button-1>", callback)

        lbd = tk.Label(f2, text=res_landmark, font=ariel14bold)
        lbd.grid(row=3, columnspan=2)

        lbs = tk.Label(f2, text=landmark, font=ariel14bold)
        lbs.grid(row=1, columnspan=2)
        f2.tkraise()

    except IndexError:
        print("No file selected")


ttk.Button(f1, text="Select a video",
           command=file_explorer).grid(row=3,
                                       column=0, padx=4, pady=10, sticky='ew')

ttk.Button(f1, text="About",
           command=lambda: f4.tkraise()).grid(row=3,
                                              column=1, padx=4, pady=10, sticky='ew')
ttk.Button(f1,
           text='Quit',
           command=root.destroy).grid(row=3,
                                      column=2,
                                      sticky='ew',
                                      padx=4,
                                      pady=10)

lb1 = tk.Label(f2, text="According to our magic juice, you are next to:", pady=2)
lb1.grid(row=0, columnspan=2)

lb1 = tk.Label(f2, text="The video that you've submitted contains: ", pady=2)
lb1.grid(row=2, columnspan=2)

lb2 = tk.Label(f2, text="Find the exact location of the monument in the picture at this link:", pady=2)
lb2.grid(row=4, columnspan=2)

print(coord)

but = ttk.Button(f2, text="Back to the start page!",
                 command=lambda: f1.tkraise())

but.grid(row=6)

ttk.Button(f4, text="Back to the main page",
           command=lambda: f1.tkraise()).pack()
tk.Label(f4, text="Idk man something something")
tk.Label(f4, text="something something").pack()

center(root)
f1.tkraise()

root.mainloop()
