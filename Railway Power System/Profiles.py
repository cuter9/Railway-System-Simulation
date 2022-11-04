import numpy as np
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import *
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import pickle
import datetime
import Utilities as ut


class Profile:
    def __init__(self, system, main_frm):
        self.main_frm = main_frm
        # self.system = system.routes[0]
        self.system = system
        self.df_case_id = self.system.op_params['df_case_id']
        self.set_df_case()
        # self.df_case = self.system.df_case
        # self.df_case_id = self.system.df_case_id
        # self.df_rd_ops = self.system.df_rd_ops
        # self.df_rdop_id = self.system.df_rdop_id
        self.p_filename = ''
        self.prof_list = []
        self.prof_list_idx = 0
        self.list_prof()
        # self.prof_list_frm()
        # self.plot_frm()

    def set_df_case(self):
        self.idx_dfc = next(
            (i for (i, c) in enumerate(self.system.op_params['op_cases']) if c['case_id'] == self.df_case_id),
            None)
        self.df_case = self.system.op_params['op_cases'][self.idx_dfc]
        self.df_rdop_id = self.df_case['rd_ops']
        # df_rdop_id = [rdop_id1, rdop_id2, rdop_id3, ...]; rdop: route_id, direction, op_parameters

        self.idx_rd = []
        for r in self.df_rdop_id:
            for rd in r:
                self.idx_rd.append(
                    next((i for (i, rop) in enumerate(self.system.op_params['route_ops']) if rop['rdop_id'] == rd), None))

        self.idx_rd = list(set(self.idx_rd))
        self.df_rd_ops = []
        for i in self.idx_rd:
            self.df_rd_ops.append(self.system.op_params['route_ops'][i])

    def list_prof(self):
        # op_cases = self.system.op_params['op_cases']
        op_cases = self.system.op_params['op_cases']
        self.prof_list = [[c['case_id'], c['p_filename']] for c in op_cases if c['simulated'] == 1]

        if self.prof_list == []:
            messagebox.showinfo('Profile Error', 'There is no profiles')
            return print('There is no profiles')
        else:
            self.prof_list_idx = next((i for (i, c) in enumerate(self.prof_list) if c[0] == self.df_case_id), None)
            if self.prof_list_idx is None:
                self.prof_list_idx = 0
            self.prof_list = [[lst[0] for lst in self.prof_list],  # case id list
                              [lst[1] for lst in self.prof_list]]  # profile file name list

            self.df_case_id = self.prof_list[0][self.prof_list_idx]
            self.net4sim = ut.load_sim_data(self.prof_list[1][self.prof_list_idx])
            self.prof_list_frm()
            self.plot_frm()

        # self.prof_list[0] = [lst[0] for lst in self.prof_list]  # case id list
        # self.prof_list[1] = [lst[1] for lst in self.prof_list]  # profile file name list

    def prof_list_frm(self):
        self.plist_frm = Frame(self.main_frm, width=200, height=200)
        self.plist_frm.pack(side=TOP, fill=X, expand=1)

        def chg_pf_idx(event):
            self.prof_list_idx = self.lst.current()
            self.df_case_id = self.prof_list[0][self.prof_list_idx]
            self.var_lab_c.set('Case ID : ' + str(self.prof_list[0][self.prof_list_idx]))
            self.net4sim = ut.load_sim_data(self.prof_list[1][self.prof_list_idx])

            self.plot()
            # print(lst.current())

        self.var_lab_c = StringVar()
        self.var_lab_c.set('Case ID : ' + str(self.df_case_id))
        self.lab_id_c = Label(self.plist_frm, textvariable=self.var_lab_c, width=10)
        self.lab_id_c.pack(side=LEFT, padx=5)

#        self.lab_rd = Label(self.plist_frm, textvariable=self.var_lab_rt, width=10)
#        self.lab_rd.pack(side=LEFT, padx=5)

        self.lab_pfn = Label(self.plist_frm, text='Profile File Name:', width=15)
        self.lab_pfn.pack(side=LEFT, padx=5)

        self.lst = ttk.Combobox(self.plist_frm, values=self.prof_list[1], state='readonly', width=80)
        self.lst.current(self.prof_list_idx)
        self.lst.pack(side=LEFT, padx=5)
        self.lst.bind('<<ComboboxSelected>>', chg_pf_idx)

    def plot_frm(self):
        def _set_rt(event):
            rt = self.var_comb_rt.get()
            self.var_lab_rt.set('Route ID : ' + str(rt))
            # self.plot()

        # container frame for setting the trip no to plot
        self.tripno_frm = LabelFrame(self.main_frm,
                                     text='Select the route and set the trip no to plot (-1 for all trips) and ',
                                     width=200, height=200)
        self.tripno_frm.pack(side=TOP, fill=X, expand=1, padx=10, pady=5, anchor='w')
        self.var_lab_rt = StringVar()
        # self.var_lab_rd.set('Route ID : ' + str(self.df_rd_ops[0]['route_id']))
        self.lab_rt = Label(self.tripno_frm, textvariable=self.var_lab_rt, width=15)
        self.lab_rt.pack(side=LEFT, padx=5)

        self.var_comb_rt = IntVar()         # route ID selection
        self.comb_rt = ttk.Combobox(self.tripno_frm, textvariable=self.var_comb_rt, values=list(self.df_case['route_id']), width=5)
        self.comb_rt.pack(side=LEFT, padx=5)
        self.comb_rt.bind('<<ComboboxSelected>>', _set_rt)
        self.comb_rt.current(0)
        self.var_lab_rt.set('Route ID : ' + str(self.var_comb_rt.get()))

        self.rb_frm = Frame(self.tripno_frm)
        self.rb_frm.pack(side=LEFT, padx=5)
        self.var_rdir = IntVar()
        self.var_rdir.set(0)
        self.rb_updir = Radiobutton(self.rb_frm, text='Upward', variable=self.var_rdir, value=0)
        self.rb_updir.pack(side=LEFT, padx=5, pady=10)
        self.rb_dndir = Radiobutton(self.rb_frm, text='Downward', variable=self.var_rdir, value=1)
        self.rb_dndir.pack(side=LEFT, padx=5, pady=10)
        if self.df_case['op_mode'] != 2:
            self.rb_frm.forget()

        lab1 = Label(self.tripno_frm, width=10, text='Trip no', anchor='w')
        lab1.pack(side=LEFT, padx=10, pady=5)
        self.ent = Entry(self.tripno_frm, width=10)
        self.ent.pack(side=LEFT, padx=10, pady=5)
        self.ent.insert(1, '1')

        bp = Button(self.tripno_frm, text='Plot', command=self.plot, width=10, bg='brown', fg='white')
        bp.pack(side=LEFT, padx=10, pady=5)
        be = Button(self.tripno_frm, text='Exit', command=self._exit, width=10, bg='brown', fg='white')
        be.pack(side=LEFT, padx=10, pady=5)
        # container frame for profile type selection
        self.type_frm = LabelFrame(self.main_frm, text='Choose the type of profile', width=200, height=200)
        self.type_frm.pack(side=TOP, fill=X, padx=10, pady=5)
        p_type = ['speed - distance', 'distance - time', 'power - time', 'acc - time', 'acc - distance',
                  'power - distance',
                  'whole system power consumption']
        p_value = [1, 2, 3, 4, 5, 6, 21]
        self.v_type = IntVar()  # need to set root
        for t, v in zip(p_type, p_value):
            Radiobutton(self.type_frm, variable=self.v_type, text=t, value=v).pack(side=LEFT, padx=10, pady=10)
        self.v_type.set(1)

        # the frame container for figure canvas
        self.canvas_frm = Frame(self.main_frm, width=1000, height=800)
        self.canvas_frm.pack(side=BOTTOM, fill=BOTH, padx=5, pady=5, expand=1)

    def plot(self):
        try:
            for w in self.canvas_frm.winfo_children():
                w.destroy()

        except AttributeError:
            pass

        proType = self.v_type.get()  # the type of profile to plot
        trip_no = [int(self.ent.get())]  # the trip no to plot
        r = self.var_comb_rt.get()
        d = self.var_rdir.get()
        # print(proType, r, d, trip_no)
        rd = next((i for (i, rd) in enumerate(self.net4sim.routes)
                   if rd.op_params['route_id'] == r and rd.op_params['direction'] == d), None)

        self.fig = plot_profiles(self.net4sim, rd, proType, trip_no)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frm)
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.canvas_frm)
        self.toolbar.update()
        self.toolbar.pack(side=BOTTOM, fill=BOTH, expand=1)
        self.canvas.get_tk_widget().config(width=1200, height=450)
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

    def _exit(self):
        for w in self.main_frm.winfo_children():
            w.destroy()

def plot_profiles(system, rd, type_profile, idx_profile):  # system : net4sim
    def gen_time_tick(to):
        td = to[-1] - to[0]
        # ts = system.op_params['start_time_sec']
        ts = system.routes[rd].op_params['start_time_sec']
        if td <= 3600:
            interval = 300
        elif 3600 < td <= 36000:
            interval = 1800
        elif 36000 < td:
            interval = 7200
        no_tick = int(np.ceil(td / interval))
        time_tick = [(lambda t: to[0] + t * interval)(n) for n in range(no_tick)]
        lable_tick = [str(datetime.timedelta(seconds=int(t + ts))) for t in time_tick]
        return time_tick, lable_tick

    if type_profile < 20:
        # trips = system.active_trips
        trips = system.routes[rd].active_trips

        va = []
        # loc_station = system.routes[rd].net_params['stations'][0]
        # len_route = loc_station[-2] - loc_station[1]
        len_route = system.routes[rd].net_params['len']
        for t in trips:
            va.append(len_route / t['travel_time'])
        v_avg = np.round(np.mean(np.array(va)) * 3600, 2)

        t_trip = []
        for t in trips:
            t_trip.append(t['travel_time'])
        t_avg = np.round(np.mean(np.array(t_trip))/60, 2)


        profiles = []
        for trip in trips:
            profiles = profiles + [trip['profile']]

        in_data = []
        if idx_profile[0] == -1:
            idx_p = [i for i in range(len(profiles))]
        else:
            idx_p = idx_profile

        if type_profile == 1:  # speed - distance
            for idx in idx_p:
                x = profiles[idx][1]  # distance
                y = profiles[idx][2] * 3.6  # speed
                in_data = in_data + [[x, y]]
            # r_id = system.op_params['route_id']
            xtick_label = system.routes[rd].net_params['stations'][1]
            xtick_loc = system.routes[rd].net_params['stations'][0]
            ytick_loc = []
            ytick_label = []
            frame_data = {'title': 'speed to distance profile; average train speed :  ' + str(v_avg) + ' kph',
                          'x_label': 'distance, m',
                          'y_label': 'speed, kph',
                          'xtick_label': xtick_label, 'xtick_loc': xtick_loc,
                          'ytick_label': ytick_label, 'ytick_loc': ytick_loc}

        elif type_profile == 2:  # distance - time
            for idx in idx_p:
                y = profiles[idx][0]  # time
                x = profiles[idx][1]  # distance
                in_data = in_data + [[x, y]]
            # r_id = system.op_params['route_id']
            xtick_label = system.routes[rd].net_params['stations'][1]
            xtick_loc = system.routes[rd].net_params['stations'][0]
            period = [in_data[0][1][0], in_data[-1][1][-1]]
            ytick_loc, ytick_label = gen_time_tick(period)
            frame_data = {'title': 'time to distance profile; average traval time : ' + str(t_avg) + ' min.',
                          'x_label': 'distance, m',
                          'y_label': 'time, sec.',
                          'xtick_label': xtick_label, 'xtick_loc': xtick_loc,
                          'ytick_label': ytick_label, 'ytick_loc': ytick_loc}

        elif type_profile == 3:  # power - time
            for idx in idx_p:
                x = profiles[idx][0]  # time
                y = profiles[idx][5]  # power
                in_data = in_data + [[x, y]]
            period = [in_data[0][0][0], in_data[-1][0][-1]]
            xtick_loc, xtick_label = gen_time_tick(period)
            ytick_label = []
            ytick_loc = []
            frame_data = {'title': 'power to time profile',
                          'x_label': 'time, sec',
                          'y_label': 'power, kW.',
                          'xtick_label': xtick_label, 'xtick_loc': xtick_loc,
                          'ytick_label': ytick_label, 'ytick_loc': ytick_loc}

        elif type_profile == 4:  # acc - time
            for idx in idx_p:
                x = profiles[idx][0]  # time
                y = profiles[idx][3]  # acc
                in_data = in_data + [[x, y]]
            period = [in_data[0][0][0], in_data[-1][0][-1]]
            xtick_loc, xtick_label = gen_time_tick(period)
            ytick_label = []
            ytick_loc = []
            frame_data = {'title': 'acc to time profile',
                          'x_label': 'time, sec',
                          'y_label': 'acc, m/s^2',
                          'xtick_label': xtick_label, 'xtick_loc': xtick_loc,
                          'ytick_label': ytick_label, 'ytick_loc': ytick_loc}

        elif type_profile == 5:  # acc - distance
            for idx in idx_p:
                x = profiles[idx][1]  # distance
                y = profiles[idx][3]  # acc
                in_data = in_data + [[x, y]]
            # r_id = system.op_params['route_id']
            xtick_label = system.routes[rd].net_params['stations'][1]
            xtick_loc = system.routes[rd].net_params['stations'][0]
            ytick_label = []
            ytick_loc = []
            frame_data = {'title': 'acc to distance profile',
                          'x_label': 'distance, m',
                          'y_label': 'acc, m/s^2',
                          'xtick_label': xtick_label, 'xtick_loc': xtick_loc,
                          'ytick_label': ytick_label, 'ytick_loc': ytick_loc}

        elif type_profile == 6:  # power - distance
            for idx in idx_p:
                x = profiles[idx][1]  # distance
                y = profiles[idx][5]  # power
                in_data = in_data + [[x, y]]
            # r_id = system.op_params['route_id']
            xtick_label = system.routes[rd].net_params['stations'][1]
            xtick_loc = system.routes[rd].net_params['stations'][0]
            ytick_label = []
            ytick_loc = []
            frame_data = {'title': 'power to distance profile',
                          'x_label': 'distance, m',
                          'y_label': 'power, kW',
                          'xtick_label': xtick_label, 'xtick_loc': xtick_loc,
                          'ytick_label': ytick_label, 'ytick_loc': ytick_loc}

    else:
        # pwr_net = system.pwr_net
        in_data = []
        if type_profile == 21:  # overall system power consumption to time
            # x = pwr_net.pwr_profile[0]
            # y = pwr_net.pwr_profile[1]  # power
            x = system.pwr_profile[0]
            y = system.pwr_profile[1]  # power
            in_data = in_data + [[x, y]]
        period = [in_data[0][0][0], in_data[-1][0][-1]]
        xtick_loc, xtick_label = gen_time_tick(period)
        ytick_label = []
        ytick_loc = []
        frame_data = {'title': 'whole network power consumption to time profile',
                      'x_label': 'time, sec',
                      'y_label': 'power, kW',
                      'xtick_label': xtick_label, 'xtick_loc': xtick_loc,
                      'ytick_label': ytick_label, 'ytick_loc': ytick_loc}

    f = ut.plot_data(in_data, frame_data)
    return f


def plot_sim_data(p_filename, pro_type, trip_no):  # p_filename: profile file name
    # system = ut.load_sim_data(achieve_name)
    system = ut.load_sim_data(p_filename)
    # type_profile = pro_type
    # 1 : v to x; 2: x to t; 3: pwr to t; 4: a to t; 5: a to x; 6: p to x
    # 21 : net pwr to time
    idx = trip_no
    # idx = [-1]  # idx=0 for first trip or first substation
    # idx = [-1]      # idx=0 for first trip or first substation
    f = ut.plot_profiles(system, pro_type, idx)
    return f
