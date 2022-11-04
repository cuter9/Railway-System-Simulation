import numpy as np
import matplotlib

# matplotlib.use("TkAgg")
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import *
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pickle
import datetime
import math


def plot_data(*data):  # in_data:  2 dim np array; x axis data:in_data[0]; y axis data:in_data[1]
    in_data = data[0]
    if len(data) > 1:
        frame_data = data[1]
        title = frame_data['title']
        y_label = frame_data['y_label']
        x_label = frame_data['x_label']
        xtick_label = frame_data['xtick_label']
        xtick_loc = frame_data['xtick_loc']
        ytick_label = frame_data['ytick_label']
        ytick_loc = frame_data['ytick_loc']

    else:
        title = 'data'
        y_label = 'y'
        x_label = 'x'
        xtick_label = []
        xtick_loc = []
        ytick_label = []
        ytick_loc = []

    plt.close('all')
    f = plt.figure(figsize=(11.5, 5.5))  # witdth:heigth = 16 : 10; 14 : 6
    f.set_tight_layout(True)
    # plt.tight_layout()
    for d in in_data:  # plot each figure in in_data
        plt.plot(d[0], d[1])

    font_title = {'fontsize': 14, 'fontweight': 'bold'}
    plt.title(title, loc='center', **font_title)

    font_axis = {'fontsize': 12, 'fontweight': 'bold'}
    font_axis_t = {'fontsize': 10, 'fontweight': 'normal'}
    plt.ylabel(y_label, loc='center', **font_axis)
    if len(ytick_loc) != 0:
        plt.yticks(ytick_loc, ytick_label, **font_axis_t)

    plt.xlabel(x_label, loc='center', **font_axis)
    if len(xtick_loc) != 0:
        plt.xticks(xtick_loc, xtick_label, **font_axis_t)

    plt.grid()
    # plt.show()
    # plt.savefig('Training Convergence ' + self.train_method + '.pdf', format='pdf')
    return f


def plot_data_tk(*data):
    f = plot_data(data)
    plt.show()
    # root = Tk()
    # root.geometry('1100x800')
    # canvas = FigureCanvasTkAgg(f, master=root)
    # canvas.draw()
    # canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

    # toolbar = NavigationToolbar2Tk(canvas, root)
    # toolbar.pack(side=BOTTOM, fill=BOTH, expand=1, anchor='w')
    # toolbar.update()


def save_sim_data(sim_data, sys_mata):
    achieve_name = sys_mata
    with open(achieve_name, 'wb') as achieve_sim_data:
        pickle.dump(sim_data, achieve_sim_data)


def load_sim_data(sys_mata):
    achieve_name = sys_mata
    with open(achieve_name, 'rb') as achieve_sim_data:
        sim_data = pickle.load(achieve_sim_data)
    return sim_data


class TableFrm(Frame):
    def __init__(self, master, d_array, **attr):  # d_array : data array to be displayed in table
        Frame.__init__(self, master, width=1000, height=80)
        self.pack(side=TOP)
        self.d_array = d_array
        self.attr = attr
        # attr = ['row_label',  'label_font', 'lab_width', 'row_width', 'data_type', 'data_font', 'editable']
        self.ent_list = []  # store the list of entry of the table
        self.vent_list = []  # store the list of entry of the table

        self.lab_frm = Frame(self, bg='blue')  # frame for place the label of each row
        self.lab_frm.pack(side=LEFT)

        self.tbl_canvas = Canvas(self, width=700, height=100,
                                 scrollregion=(0, 0, 520, 520))  # the canvas for place the table frame
        self.tbl_canvas.pack(side=LEFT)
        # tbl_canvas.place(x=150, y=1)

        hbar = Scrollbar(self.tbl_canvas, orient=HORIZONTAL, command=self.tbl_canvas.xview)
        hbar.pack(side=BOTTOM, ipadx=450, ipady=25)
        self.tbl_canvas.config(xscrollcommand=hbar.set)

        self.tbl_frm = Frame(self.tbl_canvas)  # the frame inside the canvas for place the table
        self.tbl_frm.pack(side=LEFT)

        self.tbl_frm.bind("<Configure>", lambda e: self.tbl_canvas.configure(scrollregion=self.tbl_canvas.bbox("all")))
        self.tbl_canvas.create_window((0, 0), window=self.tbl_frm, anchor='nw')  # create_window

        self.frm_ed = Frame(self, bg='blue')
        self.frm_ed.pack(side=RIGHT, anchor=E)
        # bt_add = Button(self.frm_ed, text='Add', command=self.add)
        # bt_add.grid(row=0, column=0)
        # bt_add.pack(side=TOP, ipadx=1, ipady=1)
        bt_insert = Button(self.frm_ed, text='Insert', command=self.insert)
        bt_insert.grid(row=1, column=0)
        # bt_insert.pack(side=TOP, ipadx=1, ipady=1)
        bt_del = Button(self.frm_ed, text='Delete', command=self.delete)
        bt_del.grid(row=2, column=0)
        # bt_del.pack(side=TOP, ipadx=1, ipady=1)

        self._show()
        if self.attr['editable'] == 0:
            self.frm_ed.pack_forget()

    def _show(self):
        try:
            for c in self.tbl_frm.winfo_children():
                c.destroy()
        except AttributeError:
            pass
        fr = self.attr['row_label']  # label of table rows field
        tbl_data = self.d_array  # the table data
        self.rno = len(tbl_data)  # row no of table
        self.cno = len(tbl_data[0])  # column no of table
        vent_list = []
        ent_list = []
        nr = 0  # no of row
        for r, td in zip(fr, tbl_data):
            r_lab = Label(self.lab_frm, text=r, width=self.attr['lab_width'][nr])  # the label name of the row
            r_lab.grid(row=nr, column=0, sticky=N)
            nc = 0  # no of data only column
            vent_list_r = []
            ent_list_r = []
            for d in td:
                if self.attr['data_type'][nr] == 'num':
                    var_f = DoubleVar(self.master)
                elif self.attr['data_type'][nr] == 'str':
                    var_f = StringVar(self.master)
                elif self.attr['data_type'][nr] == 'int':
                    var_f = IntVar(self.master)
                var_f.set(d)
                ent_f = Entry(self.tbl_frm, textvariable=var_f, width=self.attr['row_width'][nr])
                ent_f.winfo_name = 'ent' + str(nr) + str(nc)
                ent_f.grid(row=nr, column=nc, padx=2, pady=2)
                # ent_f.bind('<Enter>', self.chg_mark)
                ent_f.bind('<Button-1>', self.mark_focus)
                vent_list_r.append(var_f)  # joint the variable of entry with the array of the key
                ent_list_r.append(ent_f)  # joint the variable of entry with the array of the key
                nc = nc + 1
            vent_list.append(vent_list_r)
            ent_list.append(ent_list_r)
            nr = nr + 1

        self.vent_list = vent_list
        self.ent_list = ent_list

    def mark_focus(self, event):
        for ent in event.widget.master.winfo_children():
            ent.config(bg='white', fg='black')
        event.widget.config(bg='blue', fg='white')
        ents = event.widget.master.winfo_children()
        self.idx_ent_on = next(i for (i, ent) in enumerate(ents) if ent.winfo_name == event.widget.winfo_name)
        self.tbl_idx_on = [int(math.floor(self.idx_ent_on / self.cno)), int(self.idx_ent_on % self.cno)]
        # print(self.idx_ent_on, self.tbl_idx_on)

    def add(self):
        for r in range(len(self.d_array)):
            if self.attr['data_type'][r] == 'str':
                self.d_array[r].insert(self.tbl_idx_on[1] + 1, '')
            elif self.attr['data_type'][r] == 'int' or self.attr['data_type'][r] == 'num':
                self.d_array[r].insert(self.tbl_idx_on[1] + 1, 0)
        # print(self.d_array)
        self._show()

    def insert(self):
        for r in range(len(self.d_array)):
            if self.attr['data_type'][r] == 'str':
                self.d_array[r].insert(self.tbl_idx_on[1], '')
            elif self.attr['data_type'][r] == 'int':
                self.d_array[r].insert(self.tbl_idx_on[1], 0)
            elif self.attr['data_type'][r] == 'num':
                self.d_array[r].insert(self.tbl_idx_on[1], 0.0)
        # print(self.d_array)
        self._show()

    def delete(self):
        for r in range(len(self.d_array)):
            del self.d_array[r][self.tbl_idx_on[1]]
        # print(self.d_array)
        self._show()


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

    def on_resize(self, event):
        # determine the ratio of old width/height to new width/height
        # self.wscale = float(self.master.winfo_width())/self.width
        # self.hscale = float(self.master.winfo_height())/self.height
        self.wscale = float(event.width) / self.width
        self.hscale = float(event.height) / self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all", 0, 0, self.wscale, self.hscale)
