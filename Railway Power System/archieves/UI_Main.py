import fnmatch
import os
import sys
from tkinter import *
from tkinter import scrolledtext, filedialog
from tkinter import ttk, messagebox
import matplotlib
from matplotlib.figure import Figure

import numpy as np
import pickle
import copy
import time
import Train
import Profiles
import Utilities as ut
from PIL import Image, ImageTk
import System

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


def go():
    def on_resize(event):
        img_w = root.winfo_width()
        img_h = root.winfo_height()
        imgrs = img.resize((img_w, img_h), Image.Resampling.LANCZOS)
        img2 = ImageTk.PhotoImage(imgrs)
        bg_canvas.create_image(0, 0, anchor=NW, image=img2)

    root = Tk()
    root.geometry('1200x800')
    root.title("Railway System Simulation")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    # root.bind("<Configure>", on_resize)

    # img_w = root.winfo_width()
    # img_h = root.winfo_height()
    img = Image.open('car_depot.jpg')
    # imgrs = img.resize((1300, 800), Image.Resampling.HAMMING)
    imgrs = img.resize((1300, 800), Image.Resampling.LANCZOS)
    img2 = ImageTk.PhotoImage(imgrs)
    # bg_canvas = ut.ResizingCanvas(root, width=1000, height=800)
    # bg_canvas = ut.ResizingCanvas(root, width=img2.width(), height=img2.height())
    # bg_canvas = Canvas(root, width=int(img.size[0]*0.5), height=int(img.size[1]*0.5))
    bg_canvas = Canvas(root)
    # bg_canvas.columnconfigure(0, weight=1)
    # bg_canvas.rowconfigure(0, weight=1)
    bg_canvas.pack(side=TOP, fill=BOTH, expand=1)
    # bg_canvas.grid(row=0, column=0, sticky=N + S + E + W)
    bg_canvas.create_image(0, 0, anchor=NW, image=img2)

    frm = Frame(bg_canvas)
    frm.rowconfigure(0, weight=1)
    frm.columnconfigure(0, weight=1)
    # frm.grid(row=0, column=0, sticky=N + S + E + W)
    frm.pack(side=TOP, fill=BOTH, expand=1, anchor=NW)

    hbar = Scrollbar(frm, orient=HORIZONTAL)
    hbar.pack(side=BOTTOM, fill=X)
    hbar.config(command=bg_canvas.xview)
    vbar = Scrollbar(frm, orient=VERTICAL)
    vbar.pack(side=RIGHT, fill=Y)
    vbar.config(command=bg_canvas.yview)
    bg_canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

    bg_canvas.create_window(5, 5, anchor=NW, window=frm)
    rail_sys = RailSystemMenu(frm)
    root.config(menu=rail_sys)

    root.mainloop()


class RailSystemMenu(Menu):
    def __init__(self, master=None):

        self.master = master
        Menu.__init__(self, master)
        # self.master.config(menu=self)

        self.main_frm = Frame(master)
        self.main_frm.pack(side=TOP, fill=BOTH, expand=1, padx=5, pady=5)

        self.sys_menu = Menu(self)
        self.add_cascade(label="System", menu=self.sys_menu)
        self.sys_menu.add_command(label="Load", command=self._load_sys)
        self.sys_menu.add_command(label="New", command=self._new_sys)
        # self.sys_menu.add_command(label="Import", command=self._import_sys)
        self.sys_menu.add_separator()
        self.sys_menu.add_command(label="Save", command=self._save_sys)
        self.sys_menu.add_command(label="Save as", command=self._save_sys_as)
        self.sys_menu.add_separator()
        self.sys_menu.add_command(label="Exit", command=self._quit_mm)

        self.param_menu = Menu(self)
        self.add_cascade(label="Data", menu=self.param_menu)
        self.param_menu.add_command(label="System", command=self._show_sys_params)
        self.param_menu.add_command(label="Network", command=self._show_net_params)
        self.param_menu.add_command(label="PowerSystem", command=self._show_power_params)
        self.param_menu.add_command(label="Train", command=self._show_train_params)
        self.param_menu.add_command(label="Operation", command=self._show_op_params)

        self.sim_menu = Menu(self)
        self.add_cascade(label="Simulation", menu=self.sim_menu)
        self.sim_menu.add_command(label="Load Case", command=self._load_sim_case)
        # self.sim_menu.add_command(label="New Case", command=sim)

        self.prof_menu = Menu(self)
        self.add_cascade(label="Profiles", menu=self.prof_menu)
        self.prof_menu.add_command(label="Train Profiles", command=self._plot_profile)
        self.prof_menu.add_separator()
        self.prof_menu.add_command(label="Train Resistance", command=self._train_res)
        self.prof_menu.add_command(label="Traction Char", command=self._tract_char)

        self.setting_menu = Menu(self)
        self.add_cascade(label="Settings", menu=self.setting_menu)
        self.setting_menu.add_command(label="Default System", command=self._set_default)
        # self.setting_menu.add_command(label="Manage Profiles", command=plot_profile)

        self.def_settings = {'def_sys_file': ''}
        self._load_default()

    def _quit_mm(self):
        sys_ws = 'system.work_space'
        files_list = fnmatch.filter(os.listdir('.'), sys_ws)
        for f in files_list:
            os.remove(f)
        self.quit()

    def _train_res(self):
        try:
            for w in self.main_frm.winfo_children():
                w.destroy()
            self.edp_frm.destroy()
        except AttributeError:
            pass

        tr_frm = Frame(self.main_frm)
        tr_frm.pack(side=TOP, fill=BOTH, expand=1)

        tr_params = self.system.tr_params_4sim
        idx_tr = next(
            (i for (i, tr) in enumerate(tr_params['trains']) if tr['train_type'] == tr_params['df_train_type']), None)

        train_m = Train.Train(**tr_params['trains'][idx_tr])
        tr_res = train_m.train_resistance()
        frame_data = {'title': 'Train Resistance Profile (' + train_m.model['train_name'] + ')',
                      'x_label': 'Train Speed, m/s',
                      'y_label': 'Rolling Resistance, kN',
                      'xtick_label': [], 'xtick_loc': [],
                      'ytick_label': [], 'ytick_loc': []
                      }

        fig_res = ut.plot_data(tr_res, frame_data)

        tr_canvas = FigureCanvasTkAgg(fig_res, master=tr_frm)
        tr_canvas.draw()
        tr_toolbar = NavigationToolbar2Tk(tr_canvas, tr_frm)
        tr_toolbar.update()
        tr_toolbar.pack(side=BOTTOM, fill=BOTH, expand=1)
        tr_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

    def _tract_char(self):
        try:
            for w in self.main_frm.winfo_children():
                w.destroy()
            self.edp_frm.destroy()
        except AttributeError:
            pass

        tr_frm = Frame(self.main_frm)
        tr_frm.pack(side=TOP, fill=BOTH, expand=1)

        tr_params = self.system.tr_params_4sim
        idx_tr = next(
            (i for (i, tr) in enumerate(tr_params['trains']) if tr['train_type'] == tr_params['df_train_type']), None)
        train_m = Train.Train(**tr_params['trains'][idx_tr])
        train_m.state['acc_rate'] = train_m.model['acc_rate_max']
        train_m.__char_tract__()

        frame_tarct = {'title': 'Tractive Effort (' + train_m.model['train_name'] + ')',
                       'x_label': 'Train Speed, m/s',
                       'y_label': 'Tarctve Effort, kN.',
                       'xtick_label': '', 'xtick_loc': [],
                       'ytick_label': '', 'ytick_loc': []}
        frame_tarct_c = {'title': 'Tractive Current (' + train_m.model['train_name'] + ')',
                         'x_label': 'Train Speed, m/s',
                         'y_label': 'Current, kA.',
                         'xtick_label': '', 'xtick_loc': [],
                         'ytick_label': '', 'ytick_loc': []}
        frame_brk = {'title': 'Braking Effort (' + train_m.model['train_name'] + ')',
                     'x_label': 'Train Speed, m/s',
                     'y_label': 'Braking Effort, kN.',
                     'xtick_label': '', 'xtick_loc': [],
                     'ytick_label': '', 'ytick_loc': []}
        frame_brk_c = {'title': 'Regeneration Current (' + train_m.model['train_name'] + ')',
                       'x_label': 'Train Speed, m/s',
                       'y_label': 'Current, kA.',
                       'xtick_label': '', 'xtick_loc': [],
                       'ytick_label': '', 'ytick_loc': []}

        # fig, axs = plt.subplots(2, 2)
        f1 = ut.plot_data(train_m.model['char_tract_w']['brake_effort'], frame_brk)
        f2 = ut.plot_data(train_m.model['char_tract_w']['brake_current'], frame_brk_c)
        f3 = ut.plot_data(train_m.model['char_tract_w']['tract_effort'], frame_tarct)
        f4 = ut.plot_data(train_m.model['char_tract_w']['tract_current'], frame_tarct_c)
        fig_tract = [f3, f4, f1, f2]
        lab_tract = ['Tractive Effort', 'Traction Current', 'Brake Effort', 'Brake Current']
        tr_ntbk = ttk.Notebook(tr_frm)
        tr_ntbk.pack(side=TOP, fill=BOTH, expand=1)
        for f, l in zip(fig_tract, lab_tract):
            frm = Frame(tr_ntbk)
            frm.pack(side=TOP, fill=BOTH, expand=1)
            tr_ntbk.add(frm, text=l)
            tr_canvas = FigureCanvasTkAgg(f, master=frm)
            tr_canvas.draw()
            tr_toolbar = NavigationToolbar2Tk(tr_canvas, frm)
            tr_toolbar.update()
            tr_toolbar.pack(side=BOTTOM, fill=BOTH, expand=1)
            tr_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        # plt.show()

    def _plot_profile(self):
        try:
            for w in self.main_frm.winfo_children():
                w.destroy()
            self.edp_frm.destroy()
        except AttributeError:
            pass

        profile = Profiles.Profile(self.system, self.main_frm)
        if profile.prof_list == []:
            self.param_menu.invoke(1)
        else:
            profile.plot()

    def _show_sys_params(self):
        try:
            for w in self.main_frm.winfo_children():
                w.destroy()
            self.edp_frm.destroy()

        except AttributeError:
            pass

        self.app = SysParamsView(self.main_frm, self.system)
        self.app.show_params()
        self._edit_params(self.app)

    def _show_net_params(self):
        try:
            for w in self.main_frm.winfo_children():
                w.destroy()
            self.edp_frm.destroy()
        except AttributeError:
            pass

        self.app = NetParamsFrm(self.main_frm, self.system)
        self.app.show_params()
        self._edit_params(self.app)

    def _show_train_params(self):
        try:
            for w in self.main_frm.winfo_children():
                w.destroy()
            self.edp_frm.destroy()

        except AttributeError:
            pass

        self.app = TrainParamsFrm(self.main_frm, self.system)
        self.app.show_params()
        self._edit_params(self.app)

    def _show_power_params(self):
        try:
            for w in self.main_frm.winfo_children():
                w.destroy()
            self.edp_frm.destroy()

        except AttributeError:
            pass

        self.app = PwrSysParamsFrm(self.main_frm, self.system)
        self.app.show_params()
        self._edit_params(self.app)

    def _show_op_params(self):
        try:
            for w in self.main_frm.winfo_children():
                w.destroy()
            self.edp_frm.destroy()

        except AttributeError:
            pass

        self.app = OpParamsFrm(self.main_frm, self.system)
        self.app.show_params()
        self._edit_params(self.app)

    def _edit_params(self, app):
        def _show_params():
            app.show_params()

        def _clear():
            app.clear_params()

        def _save():
            self._save_sys()

        def _add():
            self._add_new()

        def _del():
            self._del_params()

        def _quit():
            # app.close_frm()
            # self.edp_frm.destroy()
            for w in self.main_frm.winfo_children():
                w.destroy()
            self.main_frm.destroy()
            self.main_frm = Frame(self.master)
            self.main_frm.pack(side=TOP, fill=BOTH, expand=1, padx=5, pady=5)

        self.edp_frm = Frame(self.main_frm)
        self.edp_frm.pack(side=TOP, padx=5, pady=5)
        self.r_b1 = Button(self.edp_frm, text='Refresh', command=_show_params, width=15, bg='brown', fg='white')
        self.r_b1.pack(side=LEFT, padx=5, pady=5)
        self.r_b2 = Button(self.edp_frm, text='Save', command=_save, width=15, bg='brown', fg='white')
        self.r_b2.pack(side=LEFT, padx=5, pady=5)
        self.r_b3 = Button(self.edp_frm, text='Add New', command=_add, width=15, bg='brown', fg='white')
        self.r_b3.pack(side=LEFT, padx=5, pady=5)
        self.r_b4 = Button(self.edp_frm, text='Clear', command=_clear, width=15, bg='brown', fg='white')
        self.r_b4.pack(side=LEFT, padx=5, pady=5)
        self.r_b5 = Button(self.edp_frm, text='Delete', command=_del, width=15, bg='brown', fg='white')
        self.r_b5.pack(side=LEFT, padx=5, pady=5)
        self.r_b6 = Button(self.edp_frm, text='Exit', command=_quit, width=15, bg='brown', fg='white')
        self.r_b6.pack(side=LEFT, padx=5, pady=5)
        # self.subfrms.append(fm_3)
        # self.edp_frm = edp_frm

    def _add_new(self):
        self.app.add_new_params()
        self.app.show_params()

    def _del_params(self):
        self.app.del_params()
        self.app.show_params()

    def _save_sys(self):
        msg = messagebox.askokcancel('Modify the existing system parameters!',
                                     'Do you want to modify the existing system parameters?')
        if msg == True:
            self.app.save_params()
            self.app.show_params()
        else:
            return

    def _save_sys_as(self):

        f_name = filedialog.asksaveasfilename(filetypes=[('System File', '.system_config')],
                                              defaultextension='.system_config',
                                              initialfile='tainan_system_new')
        if f_name is None:
            return
        else:
            self.app.save_params_as(f_name)

    def _load_sim_case(self):
        try:
            for w in self.main_frm.winfo_children():
                w.destroy()
            self.edp_frm.destroy()

        except AttributeError:
            pass

        def _c_sim():
            for w in self.main_frm.winfo_children():
                w.destroy()
            self.main_frm.destroy()
            self.main_frm = Frame(self.master)
            self.main_frm.pack(side=TOP, fill=BOTH, expand=1, padx=5, pady=5)

        def run_sim():
            self.sim_app.save_params()
            self.app.save_params()

            self.sim_app = SimParamsFrm(self.app.p_selfrm, self.system)
            self.sim_app.show_params()
            self.sim_app.pack_configure(side=LEFT)

            self.system.op_params['df_case_id'] = self.app.df_case_id

            self.system.gen4sim()  # generate the system for simulation
            c = self.system.run_simulation(self.msgtxt)
            if c == 'Completed':
                self.prof_menu.invoke(1)

        self.app = OpParamsFrm(self.main_frm, self.system)
        self.app.show_params()
        self.sim_app = SimParamsFrm(self.app.p_selfrm, self.system)
        self.sim_app.show_params()
        self.sim_app.pack_configure(side=LEFT)

        self.rs_frm = Frame(self.main_frm)
        self.rs_frm.pack(side=TOP, padx=5, pady=5, fill=X)
        self.r_bt = Button(self.rs_frm, text='Run', width=15, command=run_sim, bg='brown', fg='white')
        self.r_bt.pack(side=LEFT, padx=5, pady=5)
        self.c_bt = Button(self.rs_frm, text='Cancel', width=15, command=_c_sim, bg='brown', fg='white')
        self.c_bt.pack(side=LEFT, padx=5, pady=5)

        self.msg_frm = Frame(self.main_frm)
        self.msg_frm.pack(side=BOTTOM, fill=X, padx=10, pady=5)
        self.msgtxt = scrolledtext.ScrolledText(master=self.msg_frm, wrap=None, font=('Times New Roman', 12), height=10)
        self.msgtxt.pack(side=TOP, fill=X, expand=True)
        # run_sim()

    def _load_sys(self):
        try:
            # for w in self.main_frm:
            #    w.destroy()
            self.app.destroy()
            self.edp_frm.destroy()
        except AttributeError:
            pass

        wrkdir = os.getcwd()
        f_name = filedialog.askopenfilename(initialdir=wrkdir, title='Open System file',
                                            filetypes=(('System files', '*.system_config'), ('All files', '*.*')))
        if not f_name:
            return

        else:
            with open(f_name, 'rb') as system_data:
                system_temp = pickle.load(system_data)

            sys_ws = 'system.work_space'
            with open(sys_ws, 'wb') as system_work_space:
                pickle.dump(system_temp, system_work_space)

            self.system = load_ws()
            self.param_menu.invoke(1)  # activate the system parameters view

    def _new_sys(self):
        system_temp = System.SysTemplate()
        system = System.System(system_temp)

        f_name = filedialog.asksaveasfilename(filetypes=[('System File', '.system_config')],
                                              defaultextension='.system_config',
                                              initialfile='tainan_system_new')
        if f_name is None:
            return
        else:
            system.filename = f_name
            with open(f_name, 'wb') as system_data:
                pickle.dump(system, system_data)
            system_data.close()

    def _import_sys(self):
        print()

    def _set_default(self):
        pattern = "*.system_config"
        files_list = fnmatch.filter(os.listdir('.'), pattern)

        self.root1 = Tk()
        self.root1.title('Chose an existing system for default load :')
        self.root1.geometry('500x150')

        self.var_sys = StringVar(self.root1)
        self.var_sys.set(files_list[0])

        def _save_def():
            try:
                self.app.destroy()
                self.edp_frm.destroy()
            except AttributeError:
                pass

            f_name = self.var_sys.get()
            self.def_settings['def_sys_file'] = f_name
            def_set_file = 'system.default_set'
            with open(def_set_file, 'wb') as def_set:
                pickle.dump(self.def_settings, def_set)
            self.root1.destroy()
            self._load_default()

        def _clear_def():
            self.def_settings['def_sys_file'] = ''
            def_set_file = 'system.default_set'
            with open(def_set_file, 'wb') as def_set:
                pickle.dump(self.def_settings, def_set)
            self.root1.destroy()

        frm_1 = Frame(self.root1, padx=5, pady=10)
        frm_1.pack(side=TOP)
        lab = Label(frm_1, text='System File')
        lab.pack(side=LEFT, padx=5, pady=10)
        sys_list = ttk.Combobox(frm_1, textvariable=self.var_sys, values=files_list, width=30)
        sys_list.pack(side=LEFT, padx=20, pady=10)

        frm_2 = Frame(self.root1)
        frm_2.pack(side=TOP, padx=5, pady=10)
        bt_save = Button(frm_2, text='OK', command=_save_def, bg='brown', fg='white', width=10)
        bt_save.pack(side=LEFT, padx=5)
        bt_clear = Button(frm_2, text='Clear', command=_clear_def, bg='brown', fg='white', width=10)
        bt_clear.pack(side=LEFT, padx=5)

        self.root1.mainloop()

    def _load_default(self):
        def_set_file = 'system.default_set'
        if fnmatch.filter(os.listdir('.'), def_set_file):
            with open(def_set_file, 'rb') as def_set:
                self.def_settings = pickle.load(def_set)

            sys_file = self.def_settings['def_sys_file']
            if fnmatch.filter(os.listdir('.'), sys_file):
                with open(sys_file, 'rb') as def_sys_file:
                    def_system = pickle.load(def_sys_file)

                sys_ws = 'system.work_space'
                with open(sys_ws, 'wb') as system_work_space:
                    pickle.dump(def_system, system_work_space)

                self.system = load_ws()
                self.param_menu.invoke(1)  # activate the system parameters view

        else:
            return messagebox.showinfo('No Default System !', 'Load Existing System!')


def assign_id(existing_id):
    exid = [int(i) for i in existing_id]
    id_list = []
    [id_list.append(x) for x in range(1000) if x not in exid and x != 0]
    return min(id_list)


def load_ws():
    sys_ws = 'system.work_space'
    if fnmatch.filter(os.listdir('.'), sys_ws):
        with open(sys_ws, 'rb') as system_data:
            system = pickle.load(system_data)
    else:
        print('Load Existing system before selecting simulation case')

    return system


def save_system(system, file_name):
    # f_name = file_name + '.system_config'
    # f_name = file_name
    with open(file_name, 'wb') as system_data:
        pickle.dump(system, system_data)


class SysParamsView(ttk.Notebook):  # d[0]: master of this frame, d[1]: system
    def __init__(self, *d):
        self.master = d[0]
        self.system = d[1]
        ttk.Notebook.__init__(self, self.master, padding=[5, 5, 5, 5])
        self.bind('<<NotebookTabChanged>>', self.refresh)
        self.pack(side=TOP)
        self.p_subfrms = []

    def refresh(self, event):
        tab_sel = self.index(self.select())
        if tab_sel == 0:
            self.np_frm.show_params()
        elif tab_sel == 1:
            self.tp_frm.show_params()
        elif tab_sel == 2:
            self.pwr_frm.show_params()
        elif tab_sel == 3:
            self.op_frm.show_params()

    def show_params(self):
        try:
            for w in self.winfo_children():
                w.destroy()
            # for frm in self.p_subfrms:
            #    frm.destroy()
        except AttributeError:
            pass

        frm_1 = Frame(self, bg='blue')
        frm_1.pack(fill=BOTH)
        self.add(frm_1, text='Network Parameters', padding=[2, 2, 2, 2])
        self.np_frm = NetParamsFrm(frm_1, self.system)
        self.np_frm.show_params()

        frm_2 = Frame(self, bg='blue')
        frm_2.pack(fill=BOTH)
        self.add(frm_2, text='Train Parameters', padding=[2, 2, 2, 2])
        self.tp_frm = TrainParamsFrm(frm_2, self.system)
        self.tp_frm.show_params()

        frm_3 = Frame(self, bg='blue')
        frm_3.pack(fill=BOTH)
        self.add(frm_3, text='Power System', padding=[2, 2, 2, 2])
        self.pwr_frm = PwrSysParamsFrm(frm_3, self.system)
        self.pwr_frm.show_params()

        frm_4 = Frame(self, bg='blue')
        frm_4.pack(fill=BOTH)
        self.add(frm_4, text='Operation', padding=[2, 2, 2, 2])
        self.op_frm = OpParamsFrm(frm_4, self.system)
        self.op_frm.show_params()

        self.p_subfrms = [frm_1, frm_2, frm_3, frm_4]
        self.apps = [self.np_frm, self.tp_frm, self.pwr_frm, self.op_frm]

    def clear_params(self):
        for app in self.apps:
            app.clear_params()

    def close_frm(self):
        self.destroy()

    def save_params_as(self, f_name):
        for app in self.apps:
            app.save_params_as(f_name)

    def save_params(self):
        for app in self.apps:
            app.save_params()


class PwrSysParamsFrm(Frame):

    def __init__(self, *d):
        self.system = d[1]
        self.pwr_params = self.system.pwr_params
        self.op_params = self.system.op_params
        self.master = d[0]
        Frame.__init__(self, self.master)
        self.pack(side=TOP, fill=X, padx=5, pady=5)
        self.p_subfrms = []
        idx_c = next((i for (i, c) in enumerate(self.op_params['op_cases']) if
                      c['case_id'] == self.op_params['df_case_id']), None)
        self.df_case = self.op_params['op_cases'][idx_c]

        self.df_rdop_id = self.df_case['rd_ops'][0]
        # df_rdop_id = [rdop_id1, rdop_id2, rdop_id3, ...]; rdop: route_id, direction, op_parameters

        idx_rd = []
        for rd in self.df_rdop_id:
            idx_rd.append(
                next((i for (i, rop) in enumerate(self.op_params['route_ops']) if rop['rdop_id'] == rd), None))

        idx_rd = list(set(idx_rd))
        self.df_rd_ops = []
        for i in idx_rd:
            self.df_rd_ops.append(self.op_params['route_ops'][i])

        # self.df_pwrnet_id = self.df_rd_ops[0]['pwrnet_id']
        self.df_pwrnet_id = self.df_case['pwrnet_id']
        self.set_df_pwr_net()

        self.pni_list = []
        self.list_pni()  # train type list
        self.list_pwr_nets()

    def list_pni(self):  # power net list
        pni_list = [[p['pwrnet_name'], p['pwrnet_id']] for p in self.system.pwr_params['pwr_nets']]
        self.pni_list = np.transpose(pni_list)

    def set_df_pwr_net(self):
        self.idx_df = next(
            (n for (n, pn) in enumerate(self.pwr_params['pwr_nets']) if pn['pwrnet_id'] == self.df_pwrnet_id),
            None)
        self.df_pwr_net = self.pwr_params['pwr_nets'][self.idx_df]

    def show_params(self):
        try:
            self.p_frm.destroy()
        except AttributeError:
            pass

        sheet_p1 = [0, ['Power Net ID', 'pwrnet_id', 'int', 5],
                    ['Power Net Config', 'pwrnet_name', 'str', 20]]
        sheet_p2 = [0, ['No of BSS', 'no_BSS', 'int', 5],
                    ['BSS Feed Voltage, kV', 'volt_BSS', 'num', 10]]
        sheet_p3 = [10, 'Bulk Sub-Stations, BSS', 'BSS', ['Location, kph', '', 'num', 10],
                    # ['Boundary', '', 'num', 10],
                    ['Capacity', '', 'num', 10]]
        sheet_p4 = [0, ['No of TSS', 'no_TSS', 'int', 5],
                    ['TSS Feed Voltage, V', 'volt_TSS', 'int', 10]]  # single field
        sheet_p5 = [10, 'Traction Sub-Stations, TSS', 'TSS', ['Location, kph', '', 'num', 10],
                    # ['Boundary', '', 'num', 10],
                    ['Capacity', '', 'num', 10]]
        sheet_p6 = [0, ['3rd Rail Resistance,' + '\n' + '  Ohm/km', 'R_3rail', 'num', 10],
                    ['DC Feeder Resistance,' + '\n' + '  Ohm/km, ', 'R_TSS_line', 'num', 10],
                    ['Running Rail Resistance,' + '\n' + '  Ohm/km, ', 'R_rail', 'num', 10]]
        sheet_p7 = [30, ['Power Regeneration', 'pwr_reg', 'int', 10]]

        self.layout = [sheet_p1, sheet_p2, sheet_p3, sheet_p4, sheet_p5, sheet_p6, sheet_p7]
        self.p_frm = ParamsFrm(self, self.df_pwr_net, self.layout)

    def clear_params(self):
        self.p_frm._clear()

    def close_frm(self):
        self.destroy()

    def del_params(self):
        if len(self.pwr_params['pwr_nets']) == 1:
            del_msg = messagebox.showinfo('Delete the Last Power Net Parameter!',
                                          'The last Parameters Can Not be Deleted!')
            return
        else:
            del_msg = messagebox.askokcancel('Delete Power Net Parameter!', 'The Parameters Will be Deleted!')
            if del_msg == False:
                return

        idx_pwr = next((i for (i, p) in enumerate(self.pwr_params['pwr_nets']) if p['pwrnet_id'] == self.df_pwrnet_id),
                       None)
        # idx_tr.sort(reverse=True)
        del self.pwr_params['pwr_nets'][idx_pwr]
        self.pwr_params['df_pwrnet_id'] = self.pwr_params['pwr_nets'][0]['pwrnet_id']
        self.system.pwr_params = self.pwr_params
        save_system(self.system, self.system.filename)

        self.df_pwrnet_id = self.pwr_params['df_pwrnet_id']
        self.set_df_pwr_net()

        self.list_pni()  # # gen train type name name and train type id pair
        self.list_pwr_nets()

    def add_new_params(self):
        self.p_frm._save_temp()
        params_temp = self.p_frm.params_temp

        params_temp['pwrnet_id'] = assign_id(self.pni_list[1])
        self.pwr_params['pwr_nets'].append(params_temp)
        self.df_pwr_net = params_temp

        self.pwr_params['df_pwrnet_id'] = self.df_pwr_net['pwrnet_id']
        self.system.pwr_params = self.pwr_params
        save_system(self.system, self.system.filename)

        self.df_pwrnet_id = self.pwr_params['df_pwrnet_id']
        self.set_df_pwr_net()
        self.list_pni()  # # gen train type name name and train type id pair
        self.list_pwr_nets()

    def save_params_as(self, f_name):
        self.p_frm._save_temp()
        self.df_pwr_net = self.p_frm.params_temp
        self.pwr_params['pwr_nets'][self.idx_df] = self.df_pwr_net
        self.system.pwr_params = self.pwr_params
        save_system(self.system, f_name)

        self.list_pni()  # # gen train type name name and train type id pair
        self.list_pwr_nets()

    def save_params(self):
        self.p_frm._save_temp()
        self.df_pwr_net.update(self.p_frm.params_temp)
        self.pwr_params['pwr_nets'][self.idx_df] = self.df_pwr_net
        self.system.pwr_params = self.pwr_params
        save_system(self.system, self.system.filename)

        self.list_pni()  # # gen train type name name and train type id pair
        self.list_pwr_nets()

    def list_pwr_nets(self):
        try:
            self.p_selfrm.destroy()
        except AttributeError:
            pass

        def _list_pwr_nets(event):
            self.idx_comb = self.pn_comb.current()
            self.df_pwrnet_id = int(self.pni_list[1][self.idx_comb])
            self.set_df_pwr_net()
            self.show_params()

        self.p_selfrm = Frame(self)
        self.p_selfrm.pack(side=TOP, fill=X)

        self.pn_text = Label(self.p_selfrm, text='Power Nets')  # train type label
        self.pn_text.pack(side=LEFT, padx=5, pady=10)

        self.idx_comb = next((n for (n, lst) in enumerate(list(self.pni_list[1])) if int(lst) == self.df_pwrnet_id),
                             None)
        self.var_rlst = StringVar(self.master)
        # self.var_rlst.set(self.df_pwr_net['pwrnet_name'])
        self.pn_comb = ttk.Combobox(self.p_selfrm, textvariable=self.var_rlst,
                                    values=list(self.pni_list[0]), state='readonly')  # power nets list
        self.pn_comb.pack(side=LEFT, padx=5, pady=10)
        self.pn_comb.current(self.idx_comb)
        self.pn_comb.bind('<<ComboboxSelected>>', _list_pwr_nets)


class TrainParamsFrm(Frame):

    def __init__(self, *d):  # d[0]: root, d[1]: system

        self.df_train_type = None
        self.system = d[1]
        self.tr_params = self.system.tr_params
        self.op_params = self.system.op_params
        self.master = d[0]
        Frame.__init__(self, self.master)
        self.pack(side=TOP, fill=X, padx=5, pady=5)
        self.p_subfrms = []

        self.tno = len(self.tr_params['trains'])

        idx_c = next(
            (i for (i, c) in enumerate(self.op_params['op_cases']) if
             c['case_id'] == self.op_params['df_case_id']), None)
        self.df_case = self.op_params['op_cases'][idx_c]
        self.df_rdop_id = self.df_case['rd_ops'][0]
        # df_rdop_id = [rdop_id1, rdop_id2, rdop_id3, ...]; rdop: route_id, direction, op_parameters

        idx_rd = []
        for rd in self.df_rdop_id:
            idx_rd.append(
                next((i for (i, rop) in enumerate(self.op_params['route_ops']) if rop['rdop_id'] == rd), None))

        idx_rd = list(set(idx_rd))
        self.df_rd_ops = []
        for i in idx_rd:
            self.df_rd_ops.append(self.op_params['route_ops'][i])

        # self.df_train_type = self.df_rd_ops[0]['train_type']
        self.tr_params['df_train_type'] = self.df_case['train_type']
        self.df_train_type = self.df_case['train_type']
        self.set_df_train()

        self.tti_list = []
        self.list_tti()  # # gen train type name name and train type id pair
        self.list_train_type()

    def list_tti(self):
        tti_list = [[r['train_name'], r['train_type']] for r in self.system.tr_params['trains']]
        self.tti_list = np.transpose(tti_list)

    def set_df_train(self):
        self.idx_df = next(
            (n for (n, tr) in enumerate(self.tr_params['trains']) if tr['train_type'] == self.df_train_type),
            None)
        self.df_train = self.tr_params['trains'][self.idx_df]

    def show_params(self):

        try:
            for frm in self.p_subfrms:
                frm.destroy()
            self.p_frm.destroy()

        except AttributeError:
            pass

        sheet_t1 = [0, ['Train Type', 'train_type', 'int', 10],
                    ['Train Name', 'train_name', 'str', 20]]
        sheet_t2 = [0, ['Train Length, km', 'len', 'num', 10],
                    ['Fleet Cars', 'no_fleet', 'int', 10],
                    ['Front Area', 'area_f', 'num', 10],
                    ['Axle No/train', 'no_axle', 'int', 10]]  # single field
        sheet_t3 = [0, ['Tare Train Weight,' + '\n' + '  ton', 'w_t', 'num', 10],
                    ['Train Inertial, %, ', 'inertial', 'num', 10],
                    ['Person Weight,' + '\n' + '  kg/p', 'w_person', 'num', 10]]
        sheet_t4 = [20, 'Train Load,' + '\n' + ' p/train', 'p_load', ['', '', 'int', 10]]
        sheet_t5 = [0, ['Motor No/Train', 'no_tract_motor', 'int', 10],
                    ['Motor Power, kW', 'motor_pwr', 'num', 10],
                    ['Motor Efficiency, %', 'motor_eff', 'num', 10],
                    ['Auxiliary Power,' + '\n' + ' kW', 'aux_power', 'num', 10]]
        sheet_t6 = [20, 'Line Voltage, volt', 'line_volt', ['', '', 'num', 10]]
        sheet_t7 = [0, ['Max. Acc. Rate,' + '\n' + '  m/s^2', 'acc_rate_max', 'num', 10],
                    ['Max. Brake Rate,' + '\n' + ' m/s^2', 'brake_rate_max', 'num', 10],
                    ['Jerk Rate, m/s^3', 'jerk', 'num', 10]]
        sheet_t8 = [0, ['Max. Operation Speed,' + '\n' + '  m/s', 'max_speed', 'num', 10],
                    ['Max. Train Speed w/o ' + '\n' + ' Voltage Constraint,' + '\n' + '  kph', 'max_speed_lv', 'num',
                     10],
                    ['Min. Train Speed for ' + '\n' + 'Regeneration Brake, ' + '\n' + 'kph', 'min_speed_rb', 'num', 10]]

        self.layout = [sheet_t1, sheet_t2, sheet_t3, sheet_t4, sheet_t5, sheet_t6, sheet_t7, sheet_t8]
        self.p_frm = ParamsFrm(self, self.df_train, self.layout)
        self.p_subfrms = self.p_frm.subfrms
        # self.p_frm._edit_params()
        # self.subfrms.append(self.p_frm.ctlfrm)

    def clear_params(self):
        self.p_frm._clear()

    def close_frm(self):
        self.destroy()

    def del_params(self):
        if len(self.tr_params['trains']) == 1:
            del_msg = messagebox.showinfo('Delete the Last Train Parameter!',
                                          'The last Parameters Can Not be Deleted!')
            return
        else:
            del_msg = messagebox.askokcancel('Delete Train Parameter!', 'The Parameters Will be Deleted!')
            if del_msg == False:
                return

        idx_tr = next((i for (i, t) in enumerate(self.tr_params['trains']) if t['train_type'] == self.df_train_type),
                      None)
        # idx_tr.sort(reverse=True)
        del self.tr_params['trains'][idx_tr]
        self.tr_params['df_train_type'] = self.tr_params['trains'][0]['train_type']
        self.system.tr_params = self.tr_params
        save_system(self.system, self.system.filename)

        self.df_train_type = self.tr_params['df_train_type']
        self.set_df_train()

        self.tti_list = []
        self.list_tti()  # # gen train type name name and train type id pair
        self.list_train_type()

    def add_new_params(self):
        self.p_frm._save_temp()
        params_temp = self.p_frm.params_temp

        params_temp['train_type'] = assign_id(self.tti_list[1])
        self.tr_params['trains'].append(params_temp)
        self.df_train = params_temp

        self.tr_params['df_train_type'] = self.df_train['train_type']
        self.system.tr_params = self.tr_params
        save_system(self.system, self.system.filename)

        self.df_train_type = self.tr_params['df_train_type']
        self.set_df_train()
        self.list_tti()  # # gen train type name name and train type id pair
        self.list_train_type()

    def save_params_as(self, f_name):
        self.p_frm._save_temp()
        self.df_train = self.p_frm.params_temp
        self.tr_params['trains'][self.idx_df] = self.df_train
        self.system.tr_params = self.tr_params
        save_system(self.system, f_name)

        self.list_tti()  # # gen train type name name and train type id pair
        self.list_train_type()

    def save_params(self):
        self.p_frm._save_temp()
        self.df_train.update(self.p_frm.params_temp)
        self.tr_params['trains'][self.idx_df] = self.df_train
        self.system.tr_params = self.tr_params
        save_system(self.system, self.system.filename)

        self.list_tti()  # # gen train type name name and train type id pair
        self.list_train_type()

    def list_train_type(self):
        try:
            self.p_selfrm.destroy()
        except AttributeError:
            pass

        def _list_train_type(event):
            self.idx_comb = self.tt_list.current()
            self.df_train_type = int(self.tti_list[1][self.idx_comb])
            self.set_df_train()
            self.show_params()

        self.p_selfrm = Frame(self)
        self.p_selfrm.pack(side=TOP, fill=X)

        self.tt_text = Label(self.p_selfrm, text='Train Type Name')  # train type label
        self.tt_text.pack(side=LEFT, padx=5, pady=10)

        self.idx_comb = next((n for (n, lst) in enumerate(list(self.tti_list[1])) if int(lst) == self.df_train_type),
                             None)
        self.var_rlst = StringVar(self.master)
        # self.var_rlst.set(self.df_train['train_name'])
        self.tt_list = ttk.Combobox(self.p_selfrm, textvariable=self.var_rlst,
                                    values=list(self.tti_list[0]), state='readonly')  # train type list
        self.tt_list.pack(side=LEFT, padx=5, pady=10)
        self.tt_list.current(self.idx_comb)
        self.tt_list.bind('<<ComboboxSelected>>', _list_train_type)


class NetParamsFrm(Frame):

    def __init__(self, *d):  # d[0]: root, d[1]: system
        self.df_route = None
        self.system = d[1]
        self.network = self.system.net_params
        self.op_params = self.system.op_params
        self.master = d[0]
        Frame.__init__(self, self.master)
        self.pack(side=TOP, fill=X, padx=5, pady=5)
        self.p_subfrms = []

        self.rno = len(self.network['routes'])
        idx_c = next(
            (i for (i, c) in enumerate(self.op_params['op_cases']) if c['case_id'] == self.op_params['df_case_id']),
            None)
        self.df_case = self.op_params['op_cases'][idx_c]
        self.df_rdop_id = self.df_case['rd_ops'][0]
        # df_rdop_id = [rdop_id1, rdop_id2, rdop_id3, ...]; rdop: route_id, direction, op_parameters

        idx_rd = []
        for rd in self.df_rdop_id:
            idx_rd.append(
                next((i for (i, rop) in enumerate(self.op_params['route_ops']) if rop['rdop_id'] == rd), None))

        idx_rd = list(set(idx_rd))
        self.df_rd_ops = []
        for i in idx_rd:
            self.df_rd_ops.append(self.op_params['route_ops'][i])

        self.df_route_id = self.df_rd_ops[0]['route_id']
        # self.df_route_id = self.df_case['route_id']
        self.df_route_dir = self.df_rd_ops[0]['direction']  # 1: upward; 2: downward
        self.set_df_route()

        self.rni_list = []
        self.list_rni()  # generate route name and route id pair
        self.list_route()

        self.params_temp = {}

    def list_rni(self):
        list = [[r['route_name'], r['route_id']] for r in self.system.net_params['routes']]
        rni_list = []
        [rni_list.append(x) for x in list if x not in rni_list]
        self.rni_list = np.transpose(rni_list)

    def set_df_route(self):
        self.idx_df = next(
            (n for (n, net) in enumerate(self.network['routes'])
             if net['route_id'] == self.df_route_id and net['direction'] == self.df_route_dir), None)
        self.df_route = self.network['routes'][self.idx_df]

    def show_params(self):
        try:
            # for w in self.winfo_children():
            #    w.destroy()
            for w in self.p_subfrms:
                w.destroy()
            self.p_frm.destroy()

        except AttributeError:
            pass

        sheet_r1 = [0, ['Route ID', 'route_id', 'int', 5], ['Route Name', 'route_name', 'str', 20],
                    ['Length, km', 'len', 'num', 5], ['No of Stations', 'no_station', 'int', 5]]  # single field
        sheet_r6 = [31, 'Direction', 'direction', ['Upward', '0', 'int', 10],
                    ['Downward', '1', 'int', 10]]
        sheet_r2 = [10, 'Stations', 'stations', ['Location, km', '', 'num', 7], ['Name', '', 'str', 7]]
        sheet_r3 = [10, 'Civil Speed Limit', 'speed_limit_c', ['Change Point, km', '', 'num', 7],
                    ['Speed Limit, kph', '', 'num', 7]]
        sheet_r4 = [10, 'Track Gradient', 'grad_c', ['Change Point, km', '', 'num', 7], ['Gradient, %', '', 'num', 7]]
        sheet_r5 = [10, 'Track Curvature', 'cur_c', ['Change Point, km', '', 'num', 7], ['Radius, m', '', 'num', 7]]
        self.layout = [sheet_r1, sheet_r6, sheet_r2, sheet_r3, sheet_r4, sheet_r5]
        # self.layout = [sheet_r1, sheet_r2, sheet_r3, sheet_r4, sheet_r5]

        # self.frm_params = Frame(self)
        self.p_frm = ParamsFrm(self, self.df_route, self.layout)
        self.p_subfrms = self.p_frm.subfrms

    def clear_params(self):
        self.p_frm._clear()

    def close_frm(self):
        self.destroy()

    def del_params(self):
        if len(self.network['routes']) == 1:
            del_msg = messagebox.showinfo('Delete the Last Route Parameter!',
                                          'The last Parameters Can Not be Deleted!')
            return
        else:
            del_msg = messagebox.askokcancel('Delete Route Parameter!', 'The Parameters Will be Deleted!')
            if del_msg == False:
                return

        # idx_net = next((i for (i, t) in enumerate(self.network['routes']) if t['route_id'] == self.df_route_id),
        #               None)
        idx_net = next((i for (i, net) in enumerate(self.network['routes'])
                        if net['route_id'] == self.df_route_id and net['direction'] == self.df_route_dir), None)
        # idx_net.sort(reverse=True)
        # for i in idx_net:
        del self.network['routes'][idx_net]
        self.df_route_id = self.network['routes'][0]['route_id']
        self.df_route_dir = self.network['routes'][0]['direction']
        self.set_df_route()

        self.network['df_route_id'] = self.df_route_id
        self.system.net_params = self.network
        save_system(self.system, self.system.filename)

        self.rni_list = []
        self.list_rni()  # generate route name and route id pair
        self.list_route()

    def save_params_as_1(self, f_name):
        self.p_frm._save_temp()
        params_temp = self.p_frm.params_temp
        if params_temp['direction'] == 1:
            idx_r = next((i for (i, r) in enumerate(self.system.net_params['routes'])
                          if r['route_id'] == params_temp and r['direction'] == 1), None)
            if idx_r is None:
                msg = messagebox.askokcancel('Revert Route', 'Create a Reverse Direction of the route ?')
                if msg == 'ok':
                    self.df_route = self.p_frm.params_temp
                    self.revert_route()
                else:
                    return

        self.network['routes'][self.idx_df] = self.df_route
        self.system.net_params = self.network
        save_system(self.system, f_name)

    def gen_reverse_route(self):
        self.p_frm._save_temp()
        reverse_route_temp = self.p_frm.params_temp
        reverse_route_temp['direction'] = self.df_route_dir

        for n in range(len(reverse_route_temp['stations'])):
            if n == 0:
                d = len(reverse_route_temp['stations'][n])
                reverse_route_temp['stations'][n].reverse()
                temp = np.max(reverse_route_temp['stations'][n]) * np.ones(d) - reverse_route_temp['stations'][n]
                reverse_route_temp['stations'][n] = list(np.round(temp, 3))
            else:
                reverse_route_temp['stations'][n].reverse()

        for n in range(len(reverse_route_temp['speed_limit_c'])):
            if n == 0:
                d = len(reverse_route_temp['speed_limit_c'][n])
                reverse_route_temp['speed_limit_c'][n].reverse()
                temp = np.max(reverse_route_temp['speed_limit_c'][n]) * np.ones(d) - \
                       reverse_route_temp['speed_limit_c'][n]
                reverse_route_temp['speed_limit_c'][n] = list(np.round(temp, 3))
            else:
                reverse_route_temp['speed_limit_c'][n].reverse()
                lst1 = reverse_route_temp['speed_limit_c'][n]
                reverse_route_temp['speed_limit_c'][n] = [lst1[(i + 1) % len(lst1)]
                                                          for i, x in enumerate(lst1)]

        for n in range(len(reverse_route_temp['grad_c'])):
            if n == 0:
                d = len(reverse_route_temp['grad_c'][n])
                reverse_route_temp['grad_c'][n].reverse()
                temp = np.max(reverse_route_temp['grad_c'][n]) * np.ones(d) - reverse_route_temp['grad_c'][n]
                reverse_route_temp['grad_c'][n] = list(np.round(temp, 3))
            else:
                reverse_route_temp['grad_c'][n].reverse()
                lst2 = reverse_route_temp['grad_c'][n]
                reverse_route_temp['grad_c'][n] = [lst2[(i + 1) % len(lst2)]
                                                   for i, x in enumerate(lst2)]

        for n in range(len(reverse_route_temp['cur_c'])):
            if n == 0:
                d = len(reverse_route_temp['cur_c'][n])
                reverse_route_temp['cur_c'][n].reverse()
                temp = np.max(reverse_route_temp['cur_c'][n]) * np.ones(d) - reverse_route_temp['cur_c'][n]
                reverse_route_temp['cur_c'][n] = list(np.round(temp, 3))
            else:
                reverse_route_temp['cur_c'][n].reverse()
                lst3 = reverse_route_temp['cur_c'][n]
                reverse_route_temp['cur_c'][n] = [lst3[(i + 1) % len(lst3)]
                                                  for i, x in enumerate(lst3)]

        self.network['routes'].append(reverse_route_temp)
        self.system.net_params = self.network
        save_system(self.system, self.system.filename)

    def add_new_params(self):
        self.p_frm._save_temp()
        new_route = self.p_frm.params_temp
        new_route['route_id'] = assign_id(self.rni_list[1])
        self.network['routes'].append(new_route)
        self.df_route_id = new_route['route_id']
        self.df_route_dir = new_route['direction']
        self.set_df_route()
        self.network['df_route'] = self.df_route['route_id']

        self.system.net_params = self.network
        save_system(self.system, self.system.filename)

        self.list_rni()  # generate route name and route id pair
        self.list_route()

    def save_params_as(self, f_name):
        self.p_frm._save_temp()
        self.df_route = self.p_frm.params_temp
        self.network['routes'][self.idx_df] = self.df_route
        self.system.net_params = self.network
        save_system(self.system, f_name)

        self.list_rni()
        self.list_route()

    def save_params(self):
        for w in self.p_frm.winfo_children():
            w.update()
        self.p_frm._save_temp()
        self.df_route.update(self.p_frm.params_temp)
        self.network['routes'][self.idx_df].update(self.df_route)
        route_name = self.df_route['route_name']
        net = [n for (i, n) in enumerate(self.network['routes']) if n['route_id'] == self.df_route['route_id']]
        for n in net:
            n['route_name'] = route_name
        self.system.net_params = self.network
        save_system(self.system, self.system.filename)

        self.list_rni()
        self.list_route()

    def list_route(self):
        try:
            self.p_selfrm.destroy()
        except AttributeError:
            pass

        def _list_route_e(event):
            _list_route()

        def _list_route():
            self.idx_comb = self.r_list.current()
            self.df_route_id = int(self.rni_list[1][self.idx_comb])
            self.df_route_dir = self.var_rdir.get()
            idx_df = next((n for (n, net) in enumerate(self.network['routes'])
                           if net['route_id'] == self.df_route_id and net['direction'] == self.df_route_dir), None)
            if idx_df is None:
                msg = messagebox.askokcancel('No Reverse direction',
                                             'Create the reverse direction of the route with forward one?')
                if msg is True:
                    self.gen_reverse_route()
                else:
                    if self.var_rdir.get() == 0:
                        self.df_route_dir = 1
                        self.var_rdir.set(1)
                    else:
                        self.df_route_dir = 0
                        self.var_rdir.set(0)
                    return

            self.set_df_route()
            self.show_params()

        self.p_selfrm = Frame(self)
        self.p_selfrm.pack(side=TOP, fill=X)

        self.r_text = Label(self.p_selfrm, text='Route No')
        self.r_text.pack(side=LEFT, padx=5, pady=10)

        self.idx_comb = next((n for (n, lst) in enumerate(list(self.rni_list[1]))
                              if int(lst) == self.df_route_id), None)
        self.var_rlst = StringVar(self.master)
        # self.var_rlst.set(self.df_route['route_name'])
        self.r_list = ttk.Combobox(self.p_selfrm, textvariable=self.var_rlst, values=list(self.rni_list[0]),
                                   state='readonly')
        self.r_list.pack(side=LEFT, padx=5, pady=10)
        self.r_list.current(self.idx_comb)
        self.r_list.bind('<<ComboboxSelected>>', _list_route_e)

        self.var_rdir = IntVar(self.master)
        self.var_rdir.set(self.df_route['direction'])
        self.rb_updir = Radiobutton(self.p_selfrm, text='Upward Direction', variable=self.var_rdir, value=0,
                                    command=_list_route)
        self.rb_updir.pack(side=LEFT, padx=5, pady=10)
        self.rb_dndir = Radiobutton(self.p_selfrm, text='Downward Direction', variable=self.var_rdir, value=1,
                                    command=_list_route)
        self.rb_dndir.pack(side=LEFT, padx=5, pady=10)
        # self.rb_updir.bind('<Button-1>', _list_route)


class OpParamsFrm(Frame):

    def __init__(self, *d):  # d[0]: root, d[1]: system
        self.system = d[1]
        self.network = self.system.net_params
        self.op_params = self.system.op_params
        self.master = d[0]
        Frame.__init__(self, self.master)
        self.pack(side=TOP, fill=X, padx=5, pady=5)
        self.p_frm = Frame(self)
        self.p_subfrm = []
        self.df_case_id = self.op_params['df_case_id']
        self.set_df_case()

        self.csni_list = []
        self.list_csni()
        self.list_case()

        self.tti_list = []
        self.list_tti()

        self.pni_list = []
        self.list_pni()

        self.rni_list = []
        self.list_rni()

    def list_rni(self):
        list = [[r['route_name'], r['route_id']] for r in self.system.net_params['routes']]
        rni_list = []
        [rni_list.append(x) for x in list if x not in rni_list]
        self.rni_list = np.transpose(rni_list)

    def list_tti(self):
        tti_list = [[r['train_name'], r['train_type']] for r in self.system.tr_params['trains']]
        self.tti_list = np.transpose(tti_list)

    def list_pni(self):  # power net list
        pni_list = [[p['pwrnet_name'], p['pwrnet_id']] for p in self.system.pwr_params['pwr_nets']]
        self.pni_list = np.transpose(pni_list)

    def list_csni(self):
        list = [[c['case_name'], c['case_id']] for c in self.system.op_params['op_cases']]
        # csni_list = list(set(csni_list))
        csni_list = []
        [csni_list.append(x) for x in list if x not in csni_list]
        self.csni_list = np.transpose(csni_list)

        self.rdop_id_list = []
        [self.rdop_id_list.append(r['rdop_id']) for r in self.system.op_params['route_ops']]

    def set_df_case(self):
        self.idx_dfc = next((i for (i, c) in enumerate(self.op_params['op_cases']) if c['case_id'] == self.df_case_id),
                            None)
        self.df_case = self.op_params['op_cases'][self.idx_dfc]
        self.df_rdop_id = self.df_case['rd_ops']
        # df_rdop_id = [rdop_id1, rdop_id2, rdop_id3, ...]; rdop: route_id, direction, op_parameters

        self.idx_rd = []
        for r in self.df_rdop_id:  # for each route in the default case
            for rd in r:  # for each rdop_id in route
                self.idx_rd.append(
                    next((i for (i, rop) in enumerate(self.op_params['route_ops']) if rop['rdop_id'] == rd), None))

        self.idx_rd = list(set(self.idx_rd))  # all the index of the rd_ops in the default case
        self.df_rd_ops = []
        for i in self.idx_rd:  # collect all the re operations parameters in the default case
            self.df_rd_ops.append(self.op_params['route_ops'][i])

    def refresh(self, event):
        # print(self.df_case['route_id'], self.df_case['rd_ops'])
        if self.p_ntbk_r.index('current') == 0:
            r_id = int(self.p_ntbk_r.tab(self.p_ntbk_r_sel)['text'].split()[-1])
            idx = next((i for (i, r) in enumerate(self.df_case['route_id']) if r == r_id), None)
            del self.df_case['route_id'][idx]
            del self.df_case['rd_ops'][idx]
            self.p_ntbk_r_sel = 1
        else:
            self.p_ntbk_r_sel = self.p_ntbk_r.index('current')

        # self.p_ntbk_r.select(self.p_ntbk_r_sel)
        # self.show_params()
        for r in self.rfrm:
            r[0]._refresh()

        for p in self.rdopfrm:
            p[0]._refresh()

    def show_params(self):
        try:
            # for w in self.p_frm.winfo_children():
            #   w.destroy()
            for psf in self.p_subfrm:
                psf.destroy()
            self.p_frm.destroy()

        except AttributeError:
            pass

        self.p_subfrm = []
        self.p_frm = Frame(self)
        self.p_frm.pack(side=TOP, fill=X, expand=1)
        p_frm1 = Frame(self.p_frm)
        p_frm1.pack(side=TOP, fill=X, expand=1)
        # sheet_c1 = [0, ['Case ID', 'case_id', 'int', 10], ['Case Name', 'case_name', 'str', 10]]
        # sheet_c1 = [0, ['Case Name', 'case_name', 'str', 10]]
        sheet_c1 = [0, ['Case Name', 'case_name', 'str', 10]]
        frm_c1 = ParamsFrm(p_frm1, self.df_case, [sheet_c1])
        frm_c1.pack_configure(side=LEFT)
        self.p_subfrm.append(frm_c1)
        # cn_frm = ParamsFrm(self.p_selfrm, self.df_case, [sheet_c1])
        # cn_frm.pack_configure(side=LEFT)
        # self.p_subfrm.append(cn_frm)

        sheet_c3 = [31, 'Travel Direction', 'op_mode', ['Upward', '0', 'int', 10],
                    ['Downward', '1', 'int', 10], ['Cycling', '2', 'int', 10]]
        frm_c3 = ParamsFrm(p_frm1, self.df_case, [sheet_c3])
        frm_c3.pack_configure(side=LEFT, fill=X, expand=1)
        self.p_subfrm.append(frm_c3)
        # self.p_subfrm.append(ParamsFrm(p_frm1, self.df_case, [sheet_c3]))

        sheet_c2 = [0, ['Route ID', 'route_id', 'int', 10]]
        sheet_c21 = [0, ['Train Type', 'train_type', 'int', 10], ['Power Net ID', 'pwrnet_id', 'int', 10]]

        # self.p_subfrm.append(ParamsFrm(self.p_frm, self.df_case, [sheet_c3]))

        # sheet_c3 = [31, 'Route Direction', 'direction', ['Upward', '0', 'int', 10],
        #             ['Downward', '1', 'int', 10]]
        sheet_c4 = [0, ['Performance Level, %.', 'pl_df', 'num', 10],
                    ['Service Acc. Rate, %', 'serv_acc_df', 'num', 10],
                    ['Service Braking Rate, %', 'serv_brk_df', 'num', 10]]
        sheet_c5 = [20, 'Coasting Vector, ' + '\n' + '[km, kph]', 'coast_vec_df', ['', '', 'num', 7]]
        sheet_c6 = [0, ['Dwell Time, sec.', 'dwell_time', 'int', 10],
                    ['Start Time : ', 'start_time', 'str', 10], ['Departure Offset :', 'depart_offset', 'int', 10]]
        sheet_c7 = [10, 'Time Table', 'time_tbl', ['Duration, min.', '', 'int', 10],
                    ['Headway, sec.', '', 'int', 10]]

        sheet_c8 = [50, 'Route 1', '', sheet_c5, sheet_c6, sheet_c7]  # the sheets frame for placing sheets
        sheet_c9 = [51, 'Routes OP Mode', '', sheet_c8]  # the notebook to place the sheets frames

        # self.layout = [sheet_c1, sheet_c10]
        # self.layout = [sheet_c1, sheet_c2, sheet_c3, sheet_c4, sheet_c9]
        # self.layout = [sheet_c1, sheet_c2, sheet_c3, sheet_c4, sheet_c8]
        # self.layout = [sheet_c1, sheet_c2, sheet_c3, sheet_c4, sheet_c5, sheet_c6, sheet_c7]

        self.p_ntbk_r = ttk.Notebook(self.p_frm, padding=[5, 5, 5, 5])
        self.p_ntbk_r.pack(side=TOP, fill=X, expand=1)
        self.del_frm = Frame(self.p_ntbk_r)
        self.del_frm.pack(side=TOP)
        self.p_ntbk_r.add(self.del_frm, text='-')
        self.rfrm = []
        self.rdopfrm = []
        for r in self.df_case['route_id']:
            # self.rfrm_ids = [c]       # [route1, rdop_id11, rdop_id12, route2, rdop_id21, rdop_id22, ....
            p_frm_r = Frame(self.p_ntbk_r)
            p_frm_r.pack(side=TOP, fill=X, expand=1)
            self.p_ntbk_r.add(p_frm_r, text='Route ' + str(r))
            p_frm_r2 = ParamsFrm(p_frm_r, self.df_case, [sheet_c21])
            # var_rent = IntVar()
            # r_eny = Entry(p_frm_r, textvariable=var_rent)
            # r_eny.pack(side=LEFT)
            # var_rent.set(r)
            # r_eny.pack_forget()
            # p_frm_r2.pack_configure(side=TOP, fill=X, expand=1)
            self.p_subfrm.append(p_frm_r)
            self.p_subfrm.append(p_frm_r2)
            self.rfrm.append([p_frm_r2, r])
            self.p_ntbk_d = ttk.Notebook(p_frm_r, padding=[5, 5, 5, 5])
            self.p_ntbk_d.pack(side=TOP, fill=X)
            for rd, idx_rd in zip(self.df_rd_ops, self.idx_rd):
                if rd['route_id'] == r:
                    if rd['direction'] == 0:
                        strDir = ' Upward'
                    elif rd['direction'] == 1:
                        strDir = ' Downward'
                    p_frm_rd = ParamsFrm(self.p_ntbk_d, rd, [sheet_c4, sheet_c5, sheet_c6, sheet_c7])
                    self.p_ntbk_d.add(p_frm_rd, text='Route ' + str(rd['route_id']) + strDir)
                    self.p_subfrm.append(p_frm_rd)
                    self.rdopfrm.append([p_frm_rd, rd, idx_rd, r])
            self.p_ntbk_d.select(0)
            self.p_ntbk_d_sel = self.p_ntbk_d.select()
            self.p_ntbk_d.bind('<<NotebookTabChanged>>', self.refresh)

        self.add_frm = Frame(self.p_ntbk_r)
        self.add_frm.pack(side=TOP)
        self.p_ntbk_r.insert('end', self.add_frm, text='+')
        self.p_ntbk_r.select(1)
        self.p_ntbk_r_sel = self.p_ntbk_r.select()
        self.p_ntbk_r.bind('<<NotebookTabChanged>>', self.refresh)

    def clear_params(self):
        for f in self.p_subfrm:
            try:
                f._clear()
            except AttributeError:
                pass
            # self.p_frm._clear()

    def close_frm(self):
        self.destroy()

    def del_params(self):
        if len(self.op_params['op_cases']) == 1:
            del_msg = messagebox.showinfo('Delete the Last Operation Parameter!',
                                          'The last Parameters Can Not be Deleted!')
            return
        else:
            del_msg = messagebox.askokcancel('Delete Operation Parameter!', 'The Parameters Will be Deleted!')
            if del_msg == False:
                return

        del self.op_params['op_cases'][self.idx_dfc]
        idx_rd = self.idx_rd
        idx_rd.sort(reverse=True)
        for i in idx_rd:
            del self.op_params['route_ops'][i]
        self.op_params['df_case_id'] = self.op_params['op_cases'][0]['case_id']
        self.system.op_params = self.op_params
        save_system(self.system, self.system.filename)

        self.df_case_id = self.op_params['df_case_id']
        self.set_df_case()

        self.csni_list = []
        self.list_csni()
        self.list_case()

        self.tti_list = []
        self.list_tti()

        self.pni_list = []
        self.list_pni()

        self.rni_list = []
        self.list_rni()

    def add_new_params(self):
        self.p_subfrm[0]._save_temp()
        self.p_subfrm[1]._save_temp()

        for f in self.rfrm:
            f[0]._save_temp()

        for f in self.rdopfrm:
            f[0]._save_temp()

        dfc = copy.deepcopy(self.df_case)
        dfc.update(self.p_subfrm[0].params_temp)
        dfc.update(self.p_subfrm[1].params_temp)
        dfc['case_id'] = assign_id(list(self.csni_list[1]))
        dfc['simulated'] = 0
        dfc['p_filename'] = ''
        # dfc['op_mode'] = self.var_rdir.get()
        dfc['route_id'] = []
        dfc['rd_ops'] = []
        for r in self.rfrm:
            dfc['route_id'].append(r[1])
            rds = [ri for ri in self.rdopfrm if ri[3] == r[1]]  # process the rdop of the route_id of the df_case
            dfc['train_type'] = r[0].params_temp['train_type']
            dfc['pwrnet_id'] = r[0].params_temp['pwrnet_id']
            rdop_id_r = []
            for rd in rds:
                rd[1].update(rd[0].params_temp)
                rdop = copy.deepcopy(rd[1])
                rdop_id = assign_id(list(self.rdop_id_list))
                rdop['rdop_id'] = rdop_id
                # rdop['route_id'] = r[1]
                # rdop['direction'] =
                self.op_params['route_ops'].append(rdop)
                self.list_csni()
                rdop_id_r.append(rdop_id)
            dfc['rd_ops'].append(rdop_id_r)

        self.op_params['op_cases'].append(dfc)
        self.op_params['df_case_id'] = dfc['case_id']
        self.df_case_id = self.op_params['df_case_id']
        self.set_df_case()
        self.system.op_params = self.op_params
        save_system(self.system, self.system.filename)

        self.list_csni()
        self.list_case()
        self.show_params()

    def save_params_as(self, f_name):
        self.save_params()
        save_system(self.system, f_name)

        # self.list_csni()
        # self.list_case()

    def save_params(self):
        self.p_subfrm[0]._save_temp()
        self.df_case.update(self.p_subfrm[0].params_temp)
        self.df_case.update(self.p_subfrm[1].params_temp)

        # self.df_case['case_name'] = self.var_clst.get()
        if self.df_case['simulated'] == 1:
            msg = messagebox.askyesno('The simulation results existed',
                                      'Do you want to discard the existing simulation result? ')
            if msg == 'yes':
                self.df_case['simulated'] = 0
                self.df_case['p_filename'] = ''

        self.df_case['rd_ops'] = []
        del_idx = []
        for r in self.rfrm:
            r[0]._save_temp()
            rds = [ri for ri in self.rdopfrm if ri[3] == r[1]]  # process the rdop of the route_id of the df_case
            if self.df_case['op_mode'] == 2:
                if len(rds) == 2:
                    opid = []
                    for rd in rds:
                        rd[0]._save_temp()
                        rd[1].update(rd[0].params_temp)
                        self.op_params['route_ops'][rd[2]].update(rd[1])
                        opid.append(rd[1]['rdop_id'])
                    self.df_case['rd_ops'].append(opid)
                else:
                    for rd in rds:
                        rd[0]._save_temp()
                        rd[1].update(rd[0].params_temp)
                        self.op_params['route_ops'][rd[2]].update(rd[1])
                        rdop = copy.deepcopy(rd[1])
                        rdop_id = assign_id(list(self.rdop_id_list))
                        rdop['rdop_id'] = rdop_id
                        if rd[1]['direction'] == 0:
                            rdop['direction'] = 1
                        else:
                            rdop['direction'] = 0
                        self.op_params['route_ops'].append(rdop)
                        self.df_case['rd_ops'].append([rd[1]['rdop_id'], rdop['rdop_id']])
                        self.list_csni()
            else:
                if len(rds) == 1:
                    for rd in rds:
                        rd[0]._save_temp()
                        rd[1].update(rd[0].params_temp)
                        rd[1]['direction'] = self.df_case['op_mode']
                        self.op_params['route_ops'][rd[2]].update(rd[1])
                        self.df_case['rd_ops'].append([rd[1]['rdop_id']])
                else:
                    for rd in rds:
                        if rd[1]['direction'] == self.df_case['op_mode']:
                            rd[0]._save_temp()
                            rd[1].update(rd[0].params_temp)
                            self.op_params['route_ops'][rd[2]].update(rd[1])
                            self.df_case['rd_ops'].append([rd[1]['rdop_id']])
                        else:
                            del_idx.append(rd[2])
        del_idx.sort(reverse=True)
        for idx in del_idx:
            del self.op_params['route_ops'][idx]

        self.op_params['op_cases'][self.idx_dfc].update(self.df_case)
        self.set_df_case()
        self.system.op_params = self.op_params
        save_system(self.system, self.system.filename)

        self.list_csni()
        self.list_case()
        self.show_params()

    def list_case(self):
        try:
            self.p_selfrm.destroy()
        except AttributeError:
            pass

        def _list_case(event):
            # idx = next((c_idx for (c_idx, cni) in enumerate(self.csni_list[0])
            #            if cni == self.var_clst.get()), None)
            self.idx_comb = self.c_list.current()
            self.var_cid_text.set('Case ID : ' + str(self.csni_list[1][self.idx_comb]))
            self.df_case_id = int(self.csni_list[1][self.idx_comb])
            self.set_df_case()
            # self.var_rdir.set(self.df_case['op_mode'])
            self.show_params()

        def _list_rdop():
            rdop = self.var_rdir.get()
            # self.show_params()

        self.p_selfrm = Frame(self)
        self.p_selfrm.pack(side=TOP, fill=X)

        self.idx_comb = next((n for (n, lst) in enumerate(list(self.csni_list[1])) if int(lst) == self.df_case_id),
                             None)
        self.var_cid_text = StringVar()
        self.var_cid_text.set('Case ID : ' + str(self.csni_list[1][self.idx_comb]))
        self.cid_text = Label(self.p_selfrm, textvariable=self.var_cid_text, bg='LightGreen')
        self.cid_text.pack(side=LEFT, padx=5, pady=10)
        self.c_text2 = Label(self.p_selfrm, text='Case Name')
        self.c_text2.pack(side=LEFT, padx=5, pady=10)
        # self.r_text.grid(row=0, column=0, sticky=N + W)

        self.var_clst = StringVar(self.master)
        # self.var_clst.set(self.df_case['case_name'])
        self.c_list = ttk.Combobox(self.p_selfrm, textvariable=self.var_clst, values=list(self.csni_list[0]),
                                   state='readonly')
        self.c_list.current(self.idx_comb)
        self.c_list.pack(side=LEFT, padx=5, pady=10)
        self.c_list.bind('<<ComboboxSelected>>', _list_case)


class SimParamsFrm(Frame):

    def __init__(self, *d):
        self.system = d[1]
        self.sim_params = self.system.sim_params
        self.op_params = self.system.op_params
        self.master = d[0]
        Frame.__init__(self, self.master)
        self.pack(side=TOP, fill=X, padx=5, pady=5)
        self.p_subfrms = []

    def show_params(self):
        try:
            for w in self.p_subfrms:
                w.destroy()
            self.p_frm.destroy()
        except AttributeError:
            pass

        self.p_frm = Frame(self)
        self.p_frm.pack(side=LEFT)
        sheet_s1 = [0, ['Simulation Time Step, sec.', 'ts', 'num', 5]]
        sheet_s2 = [30, ['Dwell Disturbance', 'dwell_disturb', 'int', 10],
                    ['Acc. Disturbance', 'acc_disturb', 'int', 10]]

        frm1 = ParamsFrm(self.p_frm, self.sim_params, [sheet_s1])
        frm1.pack(side=LEFT, padx=10)
        frm2 = ParamsFrm(self.p_frm, self.sim_params, [sheet_s2])
        frm2.pack(side=LEFT)
        self.p_subfrms = [frm1, frm2]

    def clear_params(self):
        for f in self.p_subfrms:
            f._clear()

    def close_frm(self):
        self.destroy()

    def save_params(self):
        for f in self.p_subfrms:
            f._save_temp()
            self.sim_params.update(f.params_temp)

        self.system.sim_params = self.sim_params
        save_system(self.system, self.system.filename)


class ParamsFrm(Frame):

    def __init__(self, *d):  # d[0]: root, d[1]: parameter data; d[2]: layout sheet of parameter
        self.params_data = d[1]
        self.layout = d[2]
        self.master = d[0]
        # self.op_code = d[3]
        Frame.__init__(self, self.master, width=100, height=100)
        self.pack(side=TOP, fill=BOTH)
        self.lab_w = 20
        self.key_ent = {}
        self.key_tbl = {}
        self.subfrms = []
        # self.subfrms = Frame(self)
        # self.subfrms.pack(side=TOP)
        self.ctlfrm = []
        self.params_tkent = {}
        self.params_temp = {}

        self._show()
        # if self.op_code == 'edit':
        #     self._edit_params()

    def _quit(self):
        for frm in self.subfrms.winfo_children():
            frm.destroy()

    def _clear(self):
        self._update_tbl()
        ptk = self.key_ent
        for v in list(ptk.values()):
            if type(v) == list:
                for v1 in v:
                    if type(v1) == list:
                        for v2 in v1:
                            v2.set('')
                    else:
                        v1.set('')
            else:
                if type(v) == BooleanVar:
                    e0 = v.set(False)
                else:
                    e0 = v.set('')

    def _show(self):
        try:
            for frm in self.subfrms:
                frm.destroy()
        except AttributeError:
            pass

        # self.layout_up(self, self.layout)
        self.layout_up(self, self.layout)

    def _refresh(self):
        for f in self.winfo_children():
            f.update()

    def _edit(self):
        frm_3 = Frame(self.master)
        frm_3.pack(side=BOTTOM, padx=5, pady=5)
        self.r_b1 = Button(frm_3, text='Refresh', command=self._show, width=15, bg='brown', fg='white')
        self.r_b1.pack(side=LEFT, padx=5, pady=5)
        self.r_b2 = Button(frm_3, text='Save', command=self._save, width=15, bg='brown', fg='white')
        self.r_b2.pack(side=LEFT, padx=5, pady=5)
        self.r_b3 = Button(frm_3, text='Clear', command=self._clear, width=15, bg='brown', fg='white')
        self.r_b3.pack(side=LEFT, padx=5, pady=5)
        self.r_b4 = Button(frm_3, text='Exit', command=self._quit, width=15, bg='brown', fg='white')
        self.r_b4.pack(side=LEFT, padx=5, pady=5)
        # self.subfrms.append(fm_3)
        self.ctlfrm = frm_3

    def place_sheets_frm(self, frm_plc, rlo):
        frm = LabelFrame(frm_plc, text=rlo[1])
        frm.pack(side=TOP, fill=X)
        sht_frms = rlo[3:len(rlo)]
        self.layout_up(frm, sht_frms)

    def place_sheets_ntbk(self, frm_plc, rlo):
        ntbk = ttk.Notebook(frm_plc, padding=[5, 5, 5, 5])
        ntbk.pack(side=TOP, fill=BOTH)
        sht_frms = rlo[3:len(rlo)]
        for sf in sht_frms:
            frm = Frame(frm_plc)
            frm.pack(side=TOP, fill=BOTH)
            ntbk.add(frm, text=sf[1], padding=[2, 2, 2, 2])
            shts = sf[3:len(sf)]
            self.layout_up(frm, shts)

    def place_row_fields(self, frm_plc,
                         rlo):  # rla :  a row layout; frm_plc: the frame within root to place the rows field
        frm = Frame(frm_plc)
        frm.pack(side=TOP, fill=X, expand=1, padx=5, pady=2)
        fl = rlo[1:len(rlo)]
        for f in fl:
            lab = Label(frm, text=f[0], width=self.lab_w)
            lab.pack(side=LEFT, padx=5, pady=5)
            if f[2] == 'num':
                var_f = DoubleVar(self.master)
            elif f[2] == 'str':
                var_f = StringVar(self.master)
            elif f[2] == 'int':
                var_f = IntVar(self.master)
            var_f.set(self.params_data[f[1]])  # f[1] key of data dict
            ent_f = Entry(frm, textvariable=var_f, width=f[-1])
            ent_f.pack(side=LEFT, padx=5, pady=5)
            self.key_ent[f[1]] = var_f  # f[1]: key
            # self.subfrms.append(frm)

    def place_chkbox_fields(self, frm_plc, rlo):  # rla :  a row layout
        frm = Frame(frm_plc)
        frm.pack(side=TOP, fill=X, padx=5, pady=2)
        fl = rlo[1:len(rlo)]
        for f in fl:
            # lab = Label(frm, text=f[0], width=self.lab_w)
            # lab.pack(side=LEFT, padx=5, pady=5)
            var_f = BooleanVar(self.master)
            var_f.set(self.params_data[f[1]])  # f[1] key of data dict
            ent_f = Checkbutton(frm, text=f[0], var=var_f)
            ent_f.pack(side=LEFT, padx=5, pady=5)
            self.key_ent[f[1]] = var_f  # f[1]: key

    def place_rbox_fields(self, frm_plc, rlo):  # rla :  a row layout
        fl = rlo[1:len(rlo)]
        frm = LabelFrame(frm_plc, text=fl[0])
        frm.pack(side=TOP, fill=X, padx=5, pady=2)
        var_f = IntVar(self.master)
        var_f.set(self.params_data[fl[1]])  # f[1] key of data dict
        fr = rlo[3: len(rlo)]
        for f in fr:
            ent_f = Radiobutton(frm, text=f[0], variable=var_f, value=int(f[1]))  # f[1] the value of the button
            ent_f.pack(side=LEFT, padx=5, pady=5)
        self.key_ent[fl[1]] = var_f  # f[1]: key

    def place_table_fields(self, frm_plc, rlo):  # a row layout
        frm = LabelFrame(frm_plc, text=rlo[1])
        frm.pack(side=TOP, fill=X, padx=5, pady=5)
        tbl_data = self.params_data[rlo[2]]
        fr = rlo[3: len(rlo)]  # take out each rows attributes
        # attr = ['row_label',  'label_font', 'lab_width', 'row_width', 'data_type', 'data_font', 'editable']
        attr = {'row_label': [rb[0] for rb in fr], 'lab_width': [15, 15], 'row_width': [7, 7],
                'data_type': [rb[2] for rb in fr], 'editable': 1}
        tbl_frm = ut.TableFrm(frm, tbl_data, **attr)
        self.key_tbl[rlo[2]] = tbl_frm
        # self.key_ent[rlo[2]] = tbl_frm.vent_list

    def place_list_fields(self, frm_plc, rlo):  # rlo :  a row layout
        frm = Frame(frm_plc)
        frm.pack(side=TOP, fill=X, padx=5, pady=5)
        lst_data = self.params_data[rlo[2]]
        # attr = ['row_label',  'label_font', 'lab_width', 'row_width', 'data_type', 'data_font', 'editable']
        # all dic value must be in list form
        attr = {'row_label': [rlo[1]], 'lab_width': [15], 'row_width': [7],
                'data_type': [rlo[3][2]], 'editable': 1}
        tbl_frm = ut.TableFrm(frm, lst_data, **attr)
        self.key_tbl[rlo[2]] = tbl_frm
        # self.key_ent[rlo[2]] = tbl_frm.vent_list

    def _update_tbl(self):  # update table entry layout and key-entry pairs
        for k, tbl in zip(list(self.key_tbl.keys()), list(self.key_tbl.values())):
            self.key_ent[k] = tbl.vent_list

    def _save_temp(self):
        self.params_temp = {}
        self._update_tbl()
        ptk = self.key_ent
        for k, v in zip(list(ptk.keys()), list(ptk.values())):
            if type(v) == list:
                e0 = []
                for v1 in v:
                    if type(v1) == list:
                        e1 = []
                        for v2 in v1:
                            e1.append(v2.get())
                        e0.append(e1)
                    else:
                        e0.append(v1.get())
            else:
                e0 = v.get()

            self.params_temp[k] = e0
        print(self.params_temp)

    def layout_up(self, frm_plc, sht_lo):
        for rlo in sht_lo:  # rla :  a row layout
            # for rlo in self.layout:  # rla :  a row layout
            # root = Tk()
            lab_w = 20
            # net = system.net_params['routes'][0]
            if rlo[0] == 0:
                self.place_row_fields(frm_plc, rlo)

            elif rlo[0] == 10:
                self.place_table_fields(frm_plc, rlo)

            elif rlo[0] == 20:
                self.place_list_fields(frm_plc, rlo)

            elif rlo[0] == 30:
                self.place_chkbox_fields(frm_plc, rlo)

            elif rlo[0] == 31:
                self.place_rbox_fields(frm_plc, rlo)

            elif rlo[0] == 50:
                self.place_sheets_frm(frm_plc, rlo)

            elif rlo[0] == 51:
                self.place_sheets_ntbk(frm_plc, rlo)


if __name__ == '__main__':
    go()
