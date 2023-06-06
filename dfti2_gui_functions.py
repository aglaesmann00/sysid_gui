#%%
"""
Author: Adam Glaesmann
Date: 6/4/2023
"""

### GUI STRUCTURE HIERARCHY:
### 1) Root Window - main window containing all internal components 
###     i) "root.mainloop()" as last line of the file
### 2) Frames - breaks up the root window into sections
### 3) Widgets - furnishes the root window or frames with interactive/non-interactive items
###     i) buttons, labels, tables ...etc

import copy
from tkinter import *
import threading
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import tkinter.font as tkFont
from tkcalendar import DateEntry
from tkinter.filedialog import asksaveasfile

### Root Window
root = Tk() # Generates the window
root.wm_title("DFTI2 Interactive") # Title in the top left of the application
root.config(background = "#FFFFFF") # Background Color of root window

### Frame Structure
# Frame 1: Dynamic Modes
frame_mode = Frame(root, width=350, height = 350)
frame_mode.grid(row=0, column=0, padx=5, pady=5, columnspan = 3)



### LAST LINE
root.mainloop()


# %%
