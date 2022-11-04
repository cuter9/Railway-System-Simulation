import fnmatch
import os
import sys
import tkinter.ttk
from tkinter import *
from tkinter import scrolledtext
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

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

import System


def go():
    root = Tk()
    root.geometry('1200x600')
    root.title("Railway System Simulation")
    rail_sys = RailSystemMenu(root)
    root.mainloop()


def sim():
    sys_temp = System.SysTemplate()
    system = System.System(sys_temp, 'New')
    idx_def = next((index for (index, d) in enumerate(system.op_params['op_cases']) if
                    d['case_id'] == system.op_params['df_case']), None)
    no_case = len(system.op_params['op_cases'])

    def save_params():
        if app.var_opm.get() == 1:  # single period operation
            op_case = copy.deepcopy(system.op_params['op_cases'][1])
            for f, e in zip(app.fields, app.entries):
                op_case[f] = [int(e[1].get())]
            # system.op_params = params
            op_case['op_mode'] = 1
        elif app.var_opm.get() == 0:  # whole day operation
            op_case = copy.deepcopy(system.op_params['op_cases'][0])  # ref to the whole day operation parameters
            op_case['op_mode'] = 0

        rn = app.var_rn.get()  # get route name selected
        idx = next((index for (index, d) in enumerate(system.net_params['routes']) if d['route_name'] == rn), None)
        op_case['route_id'] = [system.net_params['routes'][idx]['route_id']]
        # system.op_params['route_id'] = system.net_params['routes'][idx]['route_id']
        # op_params['start_time_sec'] = op_params['start_time'][0] * 3600
        #                                                + op_params['start_time'][1] * 60 \
        #                                                + op_params['start_time'][2]
        op_case['case_id'] = no_case + 1
        try:
            system.op_params['op_cases'][no_case] = op_case
        except IndexError:
            system.op_params['op_cases'].append(op_case)

        #        system.op_params['op_cases'][no_case]['case_id'] = no_case+1
        system.op_params['case_df'] = no_case + 1

    def run_sim():
        save_params()
        system.__run_simulation__()

    root = Tk()
    root.title("Set the parameters to run simulation")
    app = SimCaseFrm(root, system)
    app.var_opm.set(1)  # 1 : default = single operation; 0: whole day operation
    rn_list = app.rni_list
    app.rid_dfc = [1]  # default route id  = 1
    # app.var_rn.set(app.rni_list[0][0])
    app.var_op_df[0].set(120)
    app.var_op_df[1].set(20)
    app.var_op_df[2].set(60)
    app.var_op_df[3].set(6)
    app.__data_frm__()

    frm_2 = Frame(root)
    frm_2.pack(side=BOTTOM, padx=5, pady=10)
    b1 = Button(frm_2, text='Go!', command=run_sim)
    b1.pack(side=LEFT, padx=5, pady=5)
    b2 = Button(frm_2, text='Save', command=save_params)
    b2.pack(side=LEFT, padx=5, pady=5)
    b3 = Button(frm_2, text='Exit', command=root.destroy)
    b3.pack(side=LEFT, padx=5, pady=5)

    # labelframe1 = LabelFrame(root)
    # labelframe1.pack(side=BOTTOM, text=X, padx=5, pady=5)
    root.mainloop()


class SimCaseFrm(Frame):
    def __init__(self, *d):  # d[0]: root, d[1]: system
        Frame.__init__(self, d[0])
        self.system = d[1]
        self.master = d[0]
        self.var_rn = StringVar(d[0])
        self.var_opm = IntVar(d[0])
        self.var_op_df = [StringVar(d[0]), StringVar(d[0]), StringVar(d[0]), StringVar(d[0])]
        self.rni_list = [[r['route_name'], r['route_id']] for r in self.system.net_params['routes']]
        self.rni_list = np.transpose(self.rni_list)
        self.case_df = self.system.op_params['df_case']
        # idx = next((index for (index, d) in enumerate(self.system.net_params['routes']) if d['route_id'] == ), None)
        # self.rn_dfc = [r['route_name'] if r['route_id'] == self.rid_dfc else None for r in self.system.net_params['routes']]
        # self.rn_dfc = self.system.net_params['routes'][idx]['route_name']
        idx = next(
            (index for (index, d) in enumerate(self.system.op_params['op_cases']) if d['case_id'] == self.case_df),
            None)
        self.rid_dfc = self.system.op_params['op_cases'][idx]['route_id']

    def __data_frm__(self):
        def turn_fs_off():
            self.fs.forget()
            # var_rb.set(1)

        def turn_fs_on():
            self.fs.pack(side=TOP)
            # var_rb.set(2)

        self.frm_1 = LabelFrame(master=self.master, text='Choose the scheduling type fot simulation')
        self.frm_1.pack(fill=X, padx=5, pady=10)
        # var_opm = IntVar(root)
        cb1 = Radiobutton(self.frm_1, text='whole day operation', variable=self.var_opm, value=0, command=turn_fs_off)
        cb1.pack(side=LEFT, padx=10, pady=10)
        cb2 = Radiobutton(self.frm_1, text='single operation period', variable=self.var_opm, value=1,
                          command=turn_fs_on)
        cb2.pack(side=LEFT, padx=10, pady=10)
        # var_opm.set(1)  # default = single operation period

        self.frm_3 = LabelFrame(master=self.master, text='Choose the route for simulation')
        self.frm_3.pack(padx=5, pady=10, fill=X)
        lab_r = Label(self.frm_3, text='Route No.')
        lab_r.pack(side=LEFT, padx=10, pady=10)

        # var_rn = StringVar(root)
        # self.var_rn.set(self.rni_list[0][0])
        idx = next(
            (index for (index, d) in enumerate(self.system.net_params['routes']) if d['route_id'] == self.rid_dfc[0]),
            None)
        # self.rn_dfc = [r['route_name'] if r['route_id'] == self.rid_dfc else None for r in self.system.net_params['routes']]
        self.rn_dfc = self.system.net_params['routes'][idx]['route_name']
        self.var_rn.set(self.rn_dfc)
        r_list = OptionMenu(self.frm_3, self.var_rn, *self.rni_list[0])
        r_list.pack(side=LEFT, padx=15, pady=5)

        self.fs = LabelFrame(self.master, text='parameters for time table generation')
        self.fs.pack(side=TOP, fill=X, padx=5, pady=10)

        self.fields = ['headway', 'dwell_time', 'duration', 'start_time']
        f_name = ['Headway', 'Dwell Time', 'Duration', 'Start Time']
        unit = ['(sec.)', '(sec.)', '(min.)', '(hour)']
        f_default_data = [fdata.get() for fdata in self.var_op_df]

        self.entries = []
        rn = 0
        for fn, u, fd in zip(f_name, unit, f_default_data):
            lab1 = Label(self.fs, width=15, padx=5, pady=10, text=fn, anchor='w')
            lab1.grid(row=rn, column=0)
            lab2 = Label(self.fs, width=15, padx=5, pady=10, text=u, anchor='w')
            lab2.grid(row=rn, column=1)
            ent = Entry(self.fs, width=50)
            # fs.pack(side=TOP, fill=X, padx=5, pady=5)

            ent.grid(row=rn, column=2)
            ent.insert(0, fd)
            self.entries.append((fn, ent))
            rn = rn + 1

    def __clear_frm__(self):
        try:
            self.frm_1.destroy()
            self.frm_3.destroy()
            self.fs.destroy()
        except AttributeError:
            pass


class RailSystemMenu(Menu):
    def __init__(self, master=None):

        self.master = master

        Menu.__init__(self, master)

        # main_menu = Menu(root)
        self.master.config(menu=self)
        self.main_frm = Frame(master)
        self.main_frm.pack(side=TOP, fill=BOTH, padx=5, pady=5)

        self.sys_menu = Menu(self)
        self.add_cascade(label="System", menu=self.sys_menu)
        self.sys_menu.add_command(label="Load", command=self._load_sys)
        self.sys_menu.add_command(label="New", command=self._new_sys)
        self.sys_menu.add_command(label="Import", command=self._import_sys)
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
        self.sim_menu.add_command(label="New Case", command=sim)

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
        tr_params = self.system.tr_params_4sim
        idx_tr = next(
            (i for (i, tr) in enumerate(tr_params['trains']) if tr['train_type'] == tr_params['df_train_type']), None)

        train_m = Train.Train(**tr_params['trains'][idx_tr])
        train_m.train_resistance()

    def _tract_char(self):
        tr_params = self.system.tr_params_4sim
        idx_tr = next(
            (i for (i, tr) in enumerate(tr_params['trains']) if tr['train_type'] == tr_params['df_train_type']), None)
        train_m = Train.Train(**tr_params['trains'][idx_tr])
        train_m.state['acc_rate'] = train_m.model['acc_rate_max']
        train_m.__char_tract__()

        frame_tarct = {'title': 'Tractive Effort',
                       'x_label': 'Train Speed, m/s',
                       'y_label': 'Tarctve Effort, kN.',
                       'xtick_label': '', 'xtick_loc': [],
                       'ytick_label': '', 'ytick_loc': []}
        frame_tarct_c = {'title': 'Tractive Current',
                         'x_label': 'Train Speed, m/s',
                         'y_label': 'Current, kA.',
                         'xtick_label': '', 'xtick_loc': [],
                         'ytick_label': '', 'ytick_loc': []}
        frame_brk = {'title': 'Braking Effort',
                     'x_label': 'Train Speed, m/s',
                     'y_label': 'Braking Effort, kN.',
                     'xtick_label': '', 'xtick_loc': [],
                     'ytick_label': '', 'ytick_loc': []}
        frame_brk_c = {'title': 'Regeneration Current',
                       'x_label': 'Train Speed, m/s',
                       'y_label': 'Current, kA.',
                       'xtick_label': '', 'xtick_loc': [],
                       'ytick_label': '', 'ytick_loc': []}

        # fig, axs = plt.subplots(2, 2)
        f1 = ut.plot_data(train_m.model['char_tract_w']['brake_effort'], frame_brk)
        f2 = ut.plot_data(train_m.model['char_tract_w']['brake_current'], frame_brk_c)
        f3 = ut.plot_data(train_m.model['char_tract_w']['tract_effort'], frame_tarct)
        f4 = ut.plot_data(train_m.model['char_tract_w']['tract_current'], frame_tarct_c)
        plt.show()

    def _plot_profile(self):
        try:
            for w in self.main_frm.winfo_children():
                w.destroy()
            self.edp_frm.destroy()
        except AttributeError:
            pass

        profile = Profiles.Profile(self.system, self.system.op_params['df_case'], self.main_frm)
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

        def _quit():
            app.close_frm()
            self.edp_frm.destroy()

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
        self.r_b5 = Button(self.edp_frm, text='Exit', command=_quit, width=15, bg='brown', fg='white')
        self.r_b5.pack(side=LEFT, padx=5, pady=5)
        # self.subfrms.append(fm_3)
        # self.edp_frm = edp_frm

    def _add_new(self):
        self.app.add_new_params()
        self.app.show_params()

    def _save_sys(self):
        self.fn_box = Tk()
        self.fn_box.geometry('400x100')

        def _ret():
            _quit()
            self.app.save_params()
            self.app.show_params()

        def _quit():
            self.fn_box.destroy()

        frm_1 = Frame(self.fn_box)
        frm_1.pack(side=TOP, padx=5, pady=10)
        lab = Label(frm_1, text='Update the existing system file ?')
        lab.pack(side=LEFT, padx=5, pady=10)
        bt_no = Button(frm_1, text='No', command=_quit, bg='brown', fg='white', width=10)
        bt_no.pack(side=LEFT, padx=5, pady=10)
        bt_yes = Button(frm_1, text='Yes', command=_ret, bg='brown', fg='white', width=10)
        bt_yes.pack(side=LEFT, padx=5, pady=10)

    def _save_sys_as(self):
        self.fn_box = Tk()
        self.fn_box.geometry('400x100')

        def _f_name():
            frm_1.destroy()
            frm_2 = LabelFrame(self.fn_box, text='enter the file name')
            frm_2.pack(side=TOP, padx=5, pady=10)
            f_ent = Entry(frm_2)
            f_ent.insert(END, 'new_system')
            f_ent.pack(side=LEFT, padx=5, pady=10)
            bt_confirm = Button(frm_2, text='OK', command=lambda: _ret_fn(f_ent), bg='brown', fg='white',
                                width=10)
            bt_confirm.pack(side=LEFT, padx=5, pady=10)
            bt_cancel = Button(frm_2, text='Cancel', command=_quit, bg='brown', fg='white', width=10)
            bt_cancel.pack(side=LEFT, padx=5, pady=10)

        def _ret_fn(v):
            f_name = v.get()
            self.app.save_params_as(f_name)
            _quit()
            return

        def _quit():
            self.fn_box.destroy()

        frm_1 = Frame(self.fn_box)
        frm_1.pack(side=TOP, padx=5, pady=10)
        lab = Label(frm_1, text='Save as a new system ?')
        lab.pack(side=LEFT, padx=5, pady=10)
        bt_no = Button(frm_1, text='No', command=_quit, bg='brown', fg='white', width=10)
        bt_no.pack(side=LEFT, padx=5, pady=10)
        bt_yes = Button(frm_1, text='Yes', command=_f_name, bg='brown', fg='white', width=10)
        bt_yes.pack(side=LEFT, padx=5, pady=10)

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

        def run_sim():
            self.app.save_params()
            c_idx = next(
                (i for (i, c) in enumerate(self.system.op_params['op_cases']) if
                 c['case_name'] == self.app.var_clst.get()), None)
            self.system.op_params['df_case'] = self.system.op_params['op_cases'][c_idx]['case_id']
            # self.app.p_frm._save_temp()
            # self.system.op_params['op_cases'][c_idx] = self.app.p_frm.params_temp
            # self.system = System.System(self.system, 'New')       # 'New' for generate the system file for simulation
            self.system.gen4sim()
            # c = self.system.run_simulation()
            c = self.system.run_simulation(self.msgtxt)
            if c == 'Completed':
                self.prof_menu.invoke(1)

        self.app = OpParamsFrm(self.main_frm, self.system)
        self.app.show_params()

        self.rs_frm = Frame(self.main_frm)
        self.rs_frm.pack(side=TOP, padx=5, pady=5, fill=X)
        self.r_bt = Button(self.rs_frm, text='Run', width=15, command=run_sim, bg='brown', fg='white')
        self.r_bt.pack(side=LEFT, padx=5, pady=5)
        self.c_bt = Button(self.rs_frm, text='Cancel', width=15, command=_c_sim, bg='brown', fg='white')
        self.c_bt.pack(side=LEFT, padx=5, pady=5)
        # self.c_bt.after(100)

        self.msg_frm = Frame(self.main_frm)
        self.msg_frm.pack(side=BOTTOM, fill=X, padx=10, pady=5)
        self.msgtxt = scrolledtext.ScrolledText(master=self.msg_frm, wrap=None, font=('Times New Roman', 12))
        self.msgtxt.pack(side=TOP, fill=X, expand=True)
        # run_sim()

    def _load_sys(self):
        pattern = "*.system_config"
        files_list = fnmatch.filter(os.listdir('.'), pattern)

        self.root1 = Tk()
        self.root1.title('Load an existing system:')
        self.root1.geometry()

        self.var_sys = StringVar(self.root1)
        self.var_sys.set(files_list[0])

        def _load():
            try:
                # for w in self.main_frm:
                #    w.destroy()
                self.app.destroy()
                self.edp_frm.destroy()
            except AttributeError:
                pass

            f_name = self.var_sys.get()
            with open(f_name, 'rb') as system_data:
                system_temp = pickle.load(system_data)

            sys_ws = 'system.work_space'
            with open(sys_ws, 'wb') as system_work_space:
                pickle.dump(system_temp, system_work_space)

            self.system = load_ws()
            self.param_menu.invoke(1)  # activate the system parameters view
            self.root1.destroy()

        frm_1 = Frame(self.root1, padx=5, pady=10)
        frm_1.pack(side=TOP)
        lab = Label(frm_1, text='System File')
        lab.pack(side=LEFT, padx=5, pady=10)
        sys_list = ttk.Combobox(frm_1, textvariable=self.var_sys, values=files_list, width=30)
        sys_list.pack(side=LEFT, padx=20, pady=10)

        frm_2 = Frame(self.root1)
        frm_2.pack(side=TOP, padx=5, pady=10)
        bt = Button(frm_2, text='Load', command=_load, bg='brown', fg='white', width=10)
        bt.pack(side=TOP)
        self.root1.mainloop()

    def _new_sys(self):
        system_temp = System.SysTemplate()
        system = System.System(system_temp)

        root = Tk()
        root.title('Input a name for the new system:')
        SysParamsView(root, system)

        def _save_new_sys():
            system.filename = self.ent_nf.get()
            save_system(system, system.filename)
            root.destroy()

        frm_1 = Frame(root)
        frm_1.pack(side=BOTTOM)
        lab = Label(frm_1, text='New System Name')
        lab.pack(side=LEFT, padx=5, pady=10)
        var_ent = StringVar(root)
        var_ent.set('tainan_system_new')
        self.ent_nf = Entry(frm_1, textvariable=var_ent)
        self.ent_nf.pack(side=LEFT, padx=5, pady=10)
        self.bt_nf = Button(frm_1, text='Save', command=_save_new_sys, bg='brown', fg='white', width=10)
        self.bt_nf.pack(side=LEFT, padx=20, pady=10)

        root.mainloop()

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


def load_ws():
    sys_ws = 'system.work_space'
    if fnmatch.filter(os.listdir('.'), sys_ws):
        with open(sys_ws, 'rb') as system_data:
            system = pickle.load(system_data)
    else:
        print('Load Existing system before selecting simulation case')

    return system


def load_sim_case():
    system = load_ws()
    root = Tk()
    case_list = [c['case_id'] for c in system.op_params['op_cases']]
    df_case = system.op_params['df_case']
    frm_1 = Frame(root)
    frm_1.pack(fill=X, padx=5, pady=10)
    lab = Label(frm_1, text='Case:')
    lab.pack(side=LEFT, padx=5, pady=10)
    var_lst = StringVar(root)
    var_lst.set(df_case)
    lst_case = OptionMenu(frm_1, var_lst, *case_list)
    lst_case.pack(side=LEFT, padx=5, pady=10)

    def show_case():
        idx = next(
            (index for (index, c) in enumerate(system.op_params['op_cases']) if c['case_id'] == int(var_lst.get())),
            None)
        case = system.op_params['op_cases'][idx]
        app = SimCaseFrm(root, system)
        app.destroy()
        app.var_opm.set(case['op_mode'])  # default = single operation
        r_id = case['route_id']
        app.var_rn.set(app.rni_list[0][0])
        app.var_op_df[0].set(case['headway'])
        app.var_op_df[1].set(case['dwell_time'])
        app.var_op_df[2].set(case['duration'])
        app.var_op_df[3].set(case['start_time'])
        app.__data_frm__()
        # frm_2.forget()

    # frm_2 = Frame(root)
    # frm_2.pack(side=BOTTOM, padx=5, pady=10)
    bt = Button(frm_1, text='OK', width=10, bg='red', fg='white', command=show_case)
    bt.pack(side=LEFT, padx=10, pady=10)


def new_sys():
    system = System.SysTemplate()
    # system = System.System(sys_temp, 'New')

    root = Tk()
    root.title('Input a name for the new system:')
    SysParamsView(root, system)

    def _save_new_sys():
        system.filename = ent.get()
        save_system(system, ent.get())
        root.destroy()

    frm_1 = Frame(root)
    frm_1.pack(side=BOTTOM)
    lab = Label(frm_1, text='New System Name')
    lab.pack(side=LEFT, padx=5, pady=10)
    var_ent = StringVar(root)
    var_ent.set('tainan_system_new')
    ent = Entry(frm_1, textvariable=var_ent)
    ent.pack(side=LEFT, padx=5, pady=10)
    bt = Button(frm_1, text='Save', command=_save_new_sys, bg='brown', fg='white', width=10)
    bt.pack(side=LEFT, padx=20, pady=10)
    root.mainloop()


def save_system(system, file_name):
    f_name = file_name + '.system_config'
    with open(f_name, 'wb') as system_data:
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
                      c['case_id'] == self.op_params['df_case']), None)
        self.df_case = self.op_params['op_cases'][idx_c]
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
        sheet_p3 = [10, 'Bulk Sub-Stations, BSS', 'BSS', ['Location, kph', '', 'num', 10], ['Capacity', '', 'num', 10]]
        sheet_p4 = [0, ['No of TSS', 'no_TSS', 'int', 5],
                    ['TSS Feed Voltage, V', 'volt_TSS', 'int', 10]]  # single field
        sheet_p5 = [10, 'Traction Sub-Stations, BSS', 'TSS', ['Location, kph', '', 'num', 10],
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

    def save_params_as(self, f_name):
        self.p_frm._save_temp()
        self.df_pwr_net = self.p_frm.params_temp
        self.pwr_params['pwr_nets'][self.idx_df] = self.df_pwr_net
        self.system.pwr_params = self.pwr_params
        save_system(self.system, f_name)

    def save_params(self):
        self.p_frm._save_temp()
        self.df_pwr_net = self.p_frm.params_temp
        self.pwr_params['pwr_nets'][self.idx_df] = self.df_pwr_net
        self.system.pwr_params = self.pwr_params
        save_system(self.system, self.system.filename)

    def list_pwr_nets(self):
        try:
            self.p_selfrm.destroy()
        except AttributeError:
            pass

        def _list_pwr_nets(event):
            self.show_params()

        self.p_selfrm = Frame(self)
        self.p_selfrm.pack(side=TOP, fill=X)

        self.pn_text = Label(self.p_selfrm, text='Power Nets')  # train type label
        self.pn_text.pack(side=LEFT, padx=5, pady=10)

        self.var_rlst = StringVar(self.master)
        self.var_rlst.set(self.df_pwr_net['pwrnet_name'])
        self.pn_list = ttk.Combobox(self.p_selfrm, textvariable=self.var_rlst,
                                    values=list(self.pni_list[0]))  # power nets list
        self.pn_list.pack(side=LEFT, padx=5, pady=10)
        self.pn_list.bind('<<ComboboxSelected>>', _list_pwr_nets)


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
             c['case_id'] == self.op_params['df_case']), None)
        self.df_case = self.op_params['op_cases'][idx_c]
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

    def save_params_as(self, f_name):
        self.p_frm._save_temp()
        self.df_train = self.p_frm.params_temp
        self.tr_params['trains'][self.idx_df] = self.df_train
        self.system.tr_params = self.tr_params
        save_system(self.system, f_name)

    def save_params(self):
        self.p_frm._save_temp()
        self.df_train_type = self.p_frm.params_temp
        self.tr_params['trains'][self.idx_df] = self.df_train
        self.system.tr_params = self.tr_params
        save_system(self.system, self.system.filename)

    def list_train_type(self):
        try:
            self.p_selfrm.destroy()
        except AttributeError:
            pass

        def _list_train_type(event):
            self.show_params()

        self.p_selfrm = Frame(self)
        self.p_selfrm.pack(side=TOP, fill=X)

        self.tt_text = Label(self.p_selfrm, text='Train Type')  # train type label
        self.tt_text.pack(side=LEFT, padx=5, pady=10)

        self.var_rlst = StringVar(self.master)
        self.var_rlst.set(self.df_train['train_name'])
        self.tt_list = ttk.Combobox(self.p_selfrm, textvariable=self.var_rlst,
                                    values=list(self.tti_list[0]))  # train type list
        self.tt_list.pack(side=LEFT, padx=5, pady=10)
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
            (i for (i, c) in enumerate(self.op_params['op_cases']) if c['case_id'] == self.op_params['df_case']), None)
        self.df_case = self.op_params['op_cases'][idx_c]
        self.df_route_id = self.df_case['route_id']
        self.df_route_dir = 1  # 1: upward; 2: downward
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
        sheet_r6 = [31, 'Direction', 'direction', ['Upward', '1', 'int', 10],
                    ['Downward', '2', 'int', 10]]
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

    def save_params_as_1(self, f_name):
        self.p_frm._save_temp()
        params_temp = self.p_frm.params_temp
        if params_temp['direction'] == 2:
            idx_r = next((i for (i, r) in enumerate(self.system.net_params['routes'])
                          if r['route_id'] == params_temp and r['direction'] == 2), None)
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
        params_temp = self.p_frm.params_temp

        idx_dup = next((i for (i, net) in enumerate(self.network['routes'])
                        if net['route_id'] == params_temp['route_id'] and net['direction'] == params_temp['direction']),
                       None)

        if idx_dup is not None:  # duplicated route id and direction
            msg_box = messagebox.askokcancel('Duplicate Route ID Duplicate', 'Override the existing route parameters?')
            if msg_box == True:
                self.df_route = params_temp
                self.network['routes'][idx_dup] = self.df_route
            else:
                return
        else:
            self.df_route = params_temp
            self.network['routes'].append(self.df_route)

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
        self.df_route = self.p_frm.params_temp
        self.network['routes'][self.idx_df] = self.df_route
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
            idx_rid = next((r_idx for (r_idx, rni) in enumerate(self.rni_list[0])
                            if rni == self.var_rlst.get()), None)
            self.df_route_id = int(self.rni_list[1][idx_rid])
            self.df_route_dir = self.var_rdir.get()
            idx_df = next((n for (n, net) in enumerate(self.network['routes'])
                           if net['route_id'] == self.df_route_id and net['direction'] == self.df_route_dir), None)
            if idx_df == None:
                msg = messagebox.askokcancel('No Reverse direction',
                                             'Create the reverse direction of the route with forward one?')
                if msg == True:
                    self.gen_reverse_route()
                else:
                    return
            self.set_df_route()
            self.show_params()

        self.p_selfrm = Frame(self)
        self.p_selfrm.pack(side=TOP, fill=X)

        self.r_text = Label(self.p_selfrm, text='Route No')
        self.r_text.pack(side=LEFT, padx=5, pady=10)

        self.var_rlst = StringVar(self.master)
        self.var_rlst.set(self.df_route['route_name'])
        self.r_list = ttk.Combobox(self.p_selfrm, textvariable=self.var_rlst, values=list(self.rni_list[0]),
                                   state='readonly')
        self.r_list.pack(side=LEFT, padx=5, pady=10)
        self.r_list.bind('<<ComboboxSelected>>', _list_route_e)

        self.var_rdir = IntVar(self.master)
        self.var_rdir.set(self.df_route['direction'])
        self.rb_updir = Radiobutton(self.p_selfrm, text='Upward Direction', variable=self.var_rdir, value=1,
                                    command=_list_route)
        self.rb_updir.pack(side=LEFT, padx=5, pady=10)
        self.rb_dndir = Radiobutton(self.p_selfrm, text='Downward Direction', variable=self.var_rdir, value=2,
                                    command=_list_route)
        self.rb_dndir.pack(side=LEFT, padx=5, pady=10)
        # self.rb_updir.bind('<Button-1>', _list_route)


class OpParamsFrm(Frame):

    def __init__(self, *d):  # d[0]: root, d[1]: system
        self.df_case = None
        self.system = d[1]
        self.network = self.system.net_params
        self.op_params = self.system.op_params
        self.master = d[0]
        Frame.__init__(self, self.master)
        self.pack(side=TOP, fill=X, padx=5, pady=5)
        self.p_frm = []
        self.p_subfrm = []
        self.df_case_id = self.op_params['df_case']
        self.set_df_case()

        self.csni_list = []
        self.list_csni()
        self.list_case()

    def list_csni_1(self):
        csni_list = [[r['case_name'], r['case_id']] for r in self.system.op_params['op_cases']]
        self.csni_list = np.transpose(csni_list)

    def list_csni(self):
        list = [[r['case_name'], r['case_id']] for r in self.system.op_params['op_cases']]
        # csni_list = list(set(csni_list))
        csni_list = []
        [csni_list.append(x) for x in list if x not in csni_list]
        self.csni_list = np.transpose(csni_list)

    def set_df_case(self):
        idx_dfc = [[n, c] for (n, c) in enumerate(self.op_params['op_cases']) if c['case_id'] == self.df_case_id]
        self.df_case = [dfc[1] for dfc in idx_dfc]
        self.idx_df = [dfc[0] for dfc in idx_dfc]
        # self.df_case = [c for (n, c) in enumerate(self.op_params['op_cases']) if c['case_id'] == self.df_case_id]
        # self.df_case = self.op_params['op_cases'][self.idx_df]
        list(self.df_case)

    def show_params(self):
        try:
            # for w in self.p_frm.winfo_children():
            #   w.destroy()
            # for psf in self.p_subfrm:
            #   psf.destroy()
            self.p_frm.destroy()

        except AttributeError:
            pass

        self.p_subfrm = []
        self.p_frm = Frame(self)
        self.p_frm.pack(side=TOP)

        sheet_c1 = [0, ['Case ID', 'case_id', 'int', 10], ['Case Name', 'case_name', 'str', 10]]
        self.p_subfrm.append(ParamsFrm(self.p_frm, self.df_case[0], [sheet_c1]))

        sheet_c2 = [0, ['Route ID', 'route_id', 'int', 10]]
        sheet_c3 = [31, 'Travel Direction', 'direction', ['Upward', '1', 'int', 10],
                    ['Downward', '2', 'int', 10], ['Cycling', '3', 'int', 10]]

        sheet_c4 = [0, ['Train Type', 'train_type', 'int', 10], ['Power Net ID', 'pwrnet_id', 'int', 10]]
        sheet_c5 = [0, ['Performance Level, %.', 'pl_df', 'num', 10],
                    ['Service Acc. Rate, %', 'serv_acc_df', 'num', 10],
                    ['Service Braking Rate, %', 'serv_brk_df', 'num', 10]]
        sheet_c6 = [20, 'Coasting Vector, ' + '\n' + '[km, kph]', 'coast_vec_df', ['', '', 'num', 7]]
        sheet_c7 = [0, ['Dwell Time, sec.', 'dwell_time', 'int', 10],
                    ['Start Time, ', 'start_time', 'str', 10]]
        sheet_c8 = [10, 'Time Table', 'time_tbl', ['Duration, min.', '', 'int', 10],
                    ['Headway, sec.', '', 'int', 10]]

        sheet_c9 = [50, 'Route 1', '', sheet_c4, sheet_c5, sheet_c6, sheet_c7,
                    sheet_c8]  # the sheets frame for placing sheets
        sheet_c10 = [51, 'Routes OP Mode', '', sheet_c9]  # the notebook to place the sheets frames

        # self.layout = [sheet_c1, sheet_c10]
        # self.layout = [sheet_c1, sheet_c2, sheet_c3, sheet_c4, sheet_c9]
        # self.layout = [sheet_c1, sheet_c2, sheet_c3, sheet_c4, sheet_c8]
        # self.layout = [sheet_c1, sheet_c2, sheet_c3, sheet_c4, sheet_c5, sheet_c6, sheet_c7]
        self.p_ntbk = ttk.Notebook(self.p_frm, padding=[5, 5, 5, 5])
        self.p_ntbk.pack(side=TOP, fill=X)
        self.p_ntbk.bind('<<NotebookTabChanged>>', self.tab_chg)

        for dc in self.df_case:
            layout = [sheet_c2, sheet_c3, sheet_c4, sheet_c5, sheet_c6, sheet_c7, sheet_c8]
            p_frm_rd = ParamsFrm(self.p_frm, dc, layout)
            if dc['direction'] == 1:
                strDir = '  Upward'
            elif dc['direction'] == 2:
                strDir = '  Downward'
            self.p_ntbk.add(p_frm_rd, text='Route ' + str(dc['route_id']) + strDir)
            self.p_subfrm.append(p_frm_rd)

    def tab_chg(self, event):
        tab_idx = self.p_ntbk.index(self.p_ntbk.select())
        print(tab_idx)
        # self.show_params()
        # self.p_ntbk.index(tab_idx)

    def clear_params(self):
        for f in self.p_subfrm:
            f._clear()
            # self.p_frm._clear()

    def close_frm(self):
        self.destroy()

    def add_new_params(self):
        for f in self.p_subfrm:
            f._save_temp()
        # self.p_frm._save_temp()
        # params_temp = self.p_frm.params_temp
        idx_dupcid = next((i for (i, op) in enumerate(self.op_params['op_cases'])
                           if op['case_id'] == self.p_subfrm[0].params_temp['case_id']), None)
        idx_duprd = []
        for psf in self.p_subfrm[1:len(self.p_subfrm)]:
            idx_duprd.extend([i for (i, op) in enumerate(self.op_params['op_cases'])
                              if op['route_id'] == psf.params_temp['route_id']
                              and op['direction'] == psf.params_temp['direction']])
        idx_duprd = list(set(idx_duprd))

        if idx_dupcid is not None and idx_duprd is not None:  # update the route operation mode
            msg_box = messagebox.askyesno('Route Operation Duplicate', 'Override the existing route operation?')
            if msg_box == True:
                for f, dfc, idx in zip(self.p_subfrm[1:len(self.p_subfrm)], self.df_case, self.idx_df):
                    dfc.update(self.p_subfrm[0].params_temp)
                    dfc.update(f.params_temp)
                    dfc['simulated'] = 0
                    dfc['p_filename'] = ''
                    self.op_params['op_cases'][idx].update(dfc)

                # self.df_case = params_temp
                # self.df_case['simulated'] = 0
                # self.df_case['p_filename'] = ''
                # self.op_params['op_cases'][idx_dupcid] = self.df_case
            else:
                return
        elif idx_dupcid is None:
            for f, c in zip(self.p_subfrm[1:len(self.p_subfrm)], self.df_case):
                dfc = copy.deepcopy(c)
                dfc.update(self.p_subfrm[0].params_temp)
                dfc.update(f.params_temp)
                dfc['simulated'] = 0
                dfc['p_filename'] = ''
                self.op_params['op_cases'].append(dfc)
        else:
            for f, c, idx in zip(self.p_subfrm[1:len(self.p_subfrm)], self.df_case, idx_duprd):
                if idx is None:
                    dfc = copy.deepcopy(c)
                    dfc.update(self.p_subfrm[0].params_temp)
                    dfc.update(f.params_temp)
                    dfc['simulated'] = 0
                    dfc['p_filename'] = ''
                    self.op_params['op_cases'].append(dfc)

            # self.df_case = params_temp
            # self.df_case['simulated'] = 0
            # self.df_case['p_filename'] = ''
            # self.op_params['op_cases'].append(self.df_case)

        self.op_params['df_case'] = self.p_subfrm[0].params_temp['case_id']
        # self.op_params['df_case'] = self.df_case['case_id']
        self.system.op_params = self.op_params
        save_system(self.system, self.system.filename)

        self.list_csni()
        self.list_case()

    def save_params_as(self, f_name):
        self.p_subfrm[0]._save_temp()
        for f, dfc, idx in zip(self.p_subfrm[1:len(self.p_subfrm)], self.df_case, self.idx_df):
            f._save_temp()
            dfc.update(self.p_subfrm[0].params_temp)
            dfc.update(f.params_temp)
            dfc['simulated'] = 0
            dfc['p_filename'] = ''
            self.op_params['op_cases'][idx].update(dfc)
        # self.p_frm._save_temp()
        # self.df_case = self.p_frm.params_temp
        # self.df_case['simulated'] = 0
        # self.df_case['p_filename'] = ''
        # self.op_params['op_cases'][self.idx_df] = self.df_case
        self.system.op_params = self.op_params
        save_system(self.system, f_name)

        self.list_csni()
        self.list_case()

    def save_params(self):
        self.p_subfrm[0]._save_temp()
        for f, dfc, idx in zip(self.p_subfrm[1:len(self.p_subfrm)], self.df_case, self.idx_df):
            f._save_temp()
            dfc.update(self.p_subfrm[0].params_temp)
            dfc.update(f.params_temp)
            dfc['simulated'] = 0
            dfc['p_filename'] = ''
            self.op_params['op_cases'][idx].update(dfc)
        # self.p_frm._save_temp()
        # self.df_case = self.p_frm.params_temp
        # self.df_case['simulated'] = 0
        # self.df_case['p_filename'] = ''
        # self.op_params['op_cases'][self.idx_df] = self.df_case
        self.system.op_params = self.op_params
        save_system(self.system, self.system.filename)

        self.list_csni()
        self.list_case()

    def sim_frm(self):
        def _c_sim():
            sys.exit()

        def _run_sim():
            c_idx = next(
                (i for (i, c) in enumerate(self.op_params['op_cases']) if c['case_name'] == self.var_clst.get()), None)
            self.system.op_params['df_case'] = self.system.op_params['op_cases'][c_idx]['case_id']
            self.p_frm._save_temp()
            self.op_params['op_cases'][c_idx] = self.p_frm.params_temp
            # self.system = System.System(self.system, 'New')       # 'New' for generate the system file for simulation
            self.system.sys_gen4sim()
            self.system.run_simulation()
            # self.system.run_simulation(self.msgtxt)
            # self.system.__run_simulation__(self.v_msgtxt)

        self.rs_frm = Frame(self.master)
        self.rs_frm.pack(side=TOP, padx=5, pady=20, fill=X)
        self.r_bt = Button(self.rs_frm, text='Run', width=15, command=_run_sim, bg='brown', fg='white')
        self.r_bt.pack(side=LEFT, padx=5, pady=5)
        self.c_bt = Button(self.rs_frm, text='Cancel', width=15, command=_c_sim, bg='brown', fg='white')
        self.c_bt.pack(side=LEFT, padx=5, pady=5)

        self.msg_frm = Frame(self.master)
        self.msg_frm.pack(side=BOTTOM, fill=X, padx=10, pady=15)
        self.msgtxt = scrolledtext.ScrolledText(master=self.msg_frm, wrap=None, font=('Times New Roman', 12))
        self.msgtxt.pack(side=TOP, fill=X, expand=True)
        self.p_subfrms.append(self.msg_frm)
        self.p_subfrms.append(self.rs_frm)
        # self.msg_frm.mainloop()
        # print()

    def list_case(self):
        try:
            self.p_selfrm.destroy()
        except AttributeError:
            pass

        def _list_case(event):
            # idx = next((c_idx for (c_idx, cni) in enumerate(self.csni_list[0])
            #            if cni == self.var_clst.get()), None)
            idx = self.c_list.current()
            self.df_case_id = int(self.csni_list[1][idx])
            self.set_df_case()
            self.show_params()

        self.p_selfrm = Frame(self)
        self.p_selfrm.pack(side=TOP, fill=X)
        # self.subfrms.append(self.p_selfrm)

        self.c_text2 = Label(self.p_selfrm, text='Case Name')
        self.c_text2.pack(side=LEFT, padx=5, pady=10)
        # self.r_text.grid(row=0, column=0, sticky=N + W)

        self.var_clst = StringVar(self.master)
        # self.var_clst.set(self.df_case['case_name'])
        idx = next((n for (n, lst) in enumerate(list(self.csni_list[1])) if int(lst) == self.df_case_id), None)
        self.c_list = ttk.Combobox(self.p_selfrm, textvariable=self.var_clst, values=list(self.csni_list[0]),
                                   state='readonly')
        self.c_list.current(idx)
        self.c_list.pack(side=LEFT, padx=5, pady=10)
        self.c_list.bind('<<ComboboxSelected>>', _list_case)

        # self.c_b5 = Button(self.fm_1, text='OK', command=self.show_case, width=15)
        # self.c_b5.pack(side=LEFT, padx=5, pady=10)


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
        self.ctlfrm = []
        self.params_tkent = {}
        self.params_temp = {}

        self._show()
        # if self.op_code == 'edit':
        #     self._edit_params()

    def _quit(self):
        for frm in self.subfrms:
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
                e0 = v.set('')

    def _show(self):
        try:
            for frm in self.subfrms:
                frm.destroy()
        except AttributeError:
            pass

        self.layout_up(self, self.layout)

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
        frm.pack(side=TOP, fill=X, padx=5, pady=2)
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
    # sys_sim()
    # plot_sim_data()
    # plot_train_resistance()
    go()
