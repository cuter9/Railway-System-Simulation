import matplotlib
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

matplotlib.use("TkAgg")

from tkinter import *
from tkinter import messagebox, ttk

root = Tk()
var = DoubleVar(root)
ent =Entry(root, textvariable=var)
ent.pack()

root.mainloop()