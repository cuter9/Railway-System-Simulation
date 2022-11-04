import numpy as np
import os
import ipywidgets as widgets
from IPython.display import display
from tkinter import *
import fnmatch
import matplotlib.pyplot as plt
import datetime
import System

import pandas as pd
import openpyxl
import UI_Main_v2 as ui
import datetime
import time

import tkinter
from tkinter.constants import *
from PIL import Image, ImageTk


class ResizingCanvas(Canvas):
    def __init__(self, master, **kwargs):
        Canvas.__init__(self, master, **kwargs)
        self.master = master
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        # self.height = self.winfo_height()
        # self.width = self.winfo_width()
        self.wscale = master.winfo_width() / self.width
        self.hscale = master.winfo_height() / self.height
        # self.img = self.img.resize((int(self.img.width * self.wscale), int(self.img.height*self.hscale)), Image.ANTIALIAS)
        # self.img = self.img.resize((int(self.img.width, int(self.img.height*self.hscale)), Image.ANTIALIAS)

    def on_resize(self, event):
        # determine the ratio of old width/height to new width/height
        # self.wscale = float(self.master.winfo_width())/self.width
        # self.hscale = float(self.master.winfo_height())/self.height
        self.wscale = float(event.width) / self.width
        self.hscale = float(event.height) / self.height
        self.width = self.width
        self.height = self.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        # self.scale("all", 0, 0, self.wscale, self.hscale)


def main():
    root = Tk()
    myframe = Frame(root)
    myframe.pack(fill=BOTH, expand=YES)

    img_w = 850
    img_h = 400
    # img2 = ImageTk.PhotoImage(img)
    mycanvas = ResizingCanvas(myframe, width=img_w, height=img_h, bg="light blue1")  # , highlightthickness=0)
    mycanvas.pack(fill=BOTH, expand=YES)

    img = Image.open('car_depot.jpg')
    img = img.resize((img_w, img_h), Image.ANTIALIAS)
    # add some widgets to the canvas
    # mycanvas.create_line(0, 0, 200, 100)
    # mycanvas.create_line(0, 100, 200, 0, fill="red", dash=(4, 4))
    # mycanvas.create_rectangle(50, 25, 150, 75, fill="blue")

    img = img.resize((int(img_w * mycanvas.wscale), int(img_h * mycanvas.hscale)), Image.ANTIALIAS)
    img2 = ImageTk.PhotoImage(img)
    mycanvas.create_image(0, 0, anchor=NW, image=img2)

    # tag all of the drawn widgets
    root.mainloop()


if __name__ == "__main__":
    main()
