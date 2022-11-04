import numpy as np
import Network as net
import datetime
import time
import Utilities as ut
import matplotlib
import Profiles as prof

matplotlib.use("TkAgg")
import UI_Main_v6 as ui
import copy


class SysTemplate:
    def __init__(self):
        self.net_params = {}
        self.tr_params = {}
        self.pwr_params = {}
        self.op_params = {}
        self.sim_params = {}

        self.__net_params_temp__()
        self.__tr_params_temp__()
        self.__op_params_temp__()
        self.__pwr_params_temp__()
        self.__sim_params_temp__()

    def __net_params_temp__(self):
        route_1 = {'route_id': 1,
                   'route_name': 'main forward',
                   'direction': 0,  # 0: Upward; 1: Downward
                   'len': 6.3,  # km
                   'no_station': 9,
                   'stations': [[0.0, 0.195, 1.078, 1.813, 2.334, 2.975, 3.907, 4.789, 5.665, 6.270, 6.45],
                                ['SB', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B11', 'B12', 'SE']],  # km
                   'speed_limit_c': [[0.0, 0.195, 4.82, 5.62, 6.270, 6.45],
                                     [30.0, 70.0, 30.0, 70.0, 30.0, 30.0]],  # km/hr
                   'grad_c': [[0.0, 0.08, 1.04, 1.12, 1.77, 2.38, 2.93, 3.95, 4.74, 5.10, 5.62, 5.70, 6.22, 6.45],
                              [0.0, 0.97, 0.00, 0.52, 0.00, 0.63, 0.00, -.52, 0.00, 0.30, 0.00, -2.02, 0.0,
                               0.00]],  # gradient in %
                   'cur_c': [
                       [0.000, 0.240, 1.030, 1.120, 1.770, 1.860, 2.290, 2.380, 2.930, 3.120, 4.10, 4.40, 4.740, 4.820,
                        5.620, 5.700, 6.230, 6.450],
                       [0.000, 1000.0, 0.00, 1000.0, 0.0, 1000.0, 0.00, 1000.0, 0.00, 1000.0, 350.0, 1000.0, 0.0, 40.0,
                        0.000, 1000.0, 0.000, 0.000]]  # curvature in radius in meter
                   }

        route_2 = {'route_id': 2,
                   'route_name': 'branch forward',
                   'direction': 0,  # 0: Upward; 1: Downward
                   'len': 6.8,  # km
                   'no_station': 10,
                   'stations': [[0.0, 0.195, 1.078, 1.813, 2.334, 2.975, 3.907, 4.789, 5.481, 6.098, 6.703, 6.80],
                                ['SB', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'SE']],  # km
                   'speed_limit_c': [[0.0, 0.195, 4.82, 5.62, 6.70, 6.80],
                                     [30.0, 70.0, 70.0, 70.0, 30.0, 30.0]],  # km/hr
                   'grad_c': [[0.0, 0.08, 1.04, 1.12, 1.77, 2.38, 2.93, 3.95, 4.74, 5.10, 5.45, 6.13, 6.66, 6.80],
                              [0.0, 0.97, 0.00, 0.52, 0.00, 0.63, 0.00, -.52, 0.00, -0.52, 0.00, -0.3, 0.0,
                               0.00]],
                   # gradient in %
                   'cur_c': [
                       [0.000, 0.240, 1.030, 1.120, 1.770, 1.860, 2.290, 2.380, 2.930, 3.120, 4.10, 4.40, 4.740, 4.820,
                        5.440, 5.520, 6.050, 6.130, 6.660, 6.80],
                       [0.000, 1000.0, 0.00, 1000.0, 0.00, 1000.0, 0.0, 1000.0, 0.0, 1000.0, 350.0, 1000.0, 0.0,
                        1000.0,
                        0.000, 1000.0, 0.000, 1000.0, 0.0, 0.000]]  # curvature in radius in meter
                   }
        self.net_params = {'routes': [route_1, route_2], 'df_route': 1}

    def __tr_params_temp__(self):
        train_1 = {'train_type': 1,
                   'train_name': 'Siemens XXX',
                   'len': 40,  # m
                   'area_f': 10.3,  # front area, m^2
                   'no_fleet': 4,  # train consist
                   'w_t': 50,  # ton
                   'inertial': 0.089,  # rotation inertial factor
                   'w_person': 60,  # kg
                   'no_axle': 8,
                   'no_tract_motor': 6,
                   'motor_pwr': 150,  # kW/motor
                   'aux_power': 20,
                   'motor_eff': 0.9,
                   # 'acc_serve': 0.85,
                   'acc_rate_max': 1.0,  # m/s^2
                   'brake_rate_max': 1.0,  # m/s^2
                   # 'brake_serve': 0.85,  # m/s^2
                   'jerk': 0.8,  # m/s^3
                   'max_speed': 70,  # km/s
                   'max_speed_lv': 60,  # km/s
                   'min_speed_rb': 4,  # km/s, min speed for regeneration braking
                   'p_load': [[0, 60, 150, 230]],  # person
                   'line_volt': [[550, 750, 900]]  # volt
                   }
        self.tr_params = {'trains': [train_1], 'df_train_type': 1}

    def __pwr_params_temp__(self):
        pwr_net_1 = {'pwrnet_id': 1, 'pwrnet_name': 'power net config 1',
                     'no_BSS': 2,
                     'BSS': [[0, 5],  # kp
                             # [3.5],   # boundary, kp
                             [20, 20]], # capacity
                     'volt_BSS': 22,  # kV
                     'no_TSS': 4,
                     'TSS': [[1.078, 2.334, 3.907, 5.665],  # km
                             # [1.5, 3.1, 4.7],    # boundary, kp
                             [2000, 2000, 2000, 2000]],  # kW
                     'volt_TSS': 750,  # Volt
                     'range_TSS': [[0, 1.8], [1.8, 2.9], [2.9, 4.8],
                                   [4.7, self.net_params['routes'][0]['len']]],
                     # [kp, kp]
                     'R_3rail': 0.007,  # Ohm/km
                     'R_TSS_line': 0.0369,  # Ohm/km
                     'R_rail': 0.0175,  # Ohm/km
                     'pwr_reg': 0
                     }
        self.pwr_params = {'pwr_nets': [pwr_net_1], 'df_pwrnet_id': 1}

    def __op_params_temp__(self):
        op_case_1 = {'case_id': 1, 'case_name': 'case 1',
                     'route_id': [1, 2], 'train_type': 1, 'pwrnet_id': 1,
                     'op_mode': 2,  # 0: Upward; 1: Backward; 2: Cycling
                     'rd_ops': [[1, 2], [9, 10]],
                     'simulated': 0, 'p_filename': ''
                     }

        op_case_2 = {'case_id': 2, 'case_name': 'case 2',
                     'route_id': [1], 'train_type': 1, 'pwrnet_id': 1,
                     'op_mode': 2,  # 0: Upward; 1: Backward; 2: Cycling
                     'rd_ops': [[3, 4]],
                     'simulated': 0, 'p_filename': ''}

        op_case_3 = {'case_id': 3, 'case_name': 'case 3',
                     'route_id': [1, 2], 'train_type': 1, 'pwrnet_id': 1,
                     'op_mode': 2,  # 0: Upward; 1: Backward; 2: Cycling
                     'rd_ops': [[5, 6], [7, 8]],
                     'simulated': 0, 'p_filename': ''}

        rdop_111 = {'rdop_id': 1,
                    'route_id': 1,
                    'direction': 0,  # 0: forward, 1 :backward, 2: loop
                    'pl_df': 1,  # default performance level
                    'serv_acc_df': 0.85,  # default service acceleration rate in % of maximum train acc rate
                    'serv_brk_df': 0.85,  # default service braking rate in % of maximum train brake rate
                    'coast_vec_df': [[-1, -1]],  # [distant, speed], default coasting vector [-1, -1]: no coasting
                    'dwell_time': 20, 'start_time': '06:00:00',  # [[hour], [min], [sec]]
                    'depart_offset': 0,  # the departure time offset to the start time
                    'time_tbl': [[60, 30, 90, 120, 90, 300, 90, 90, 120],  # duration
                                 [480, 120, 90, 180, 120, 360, 90, 180, 480]]  # headway
                    }

        rdop_112 = {'rdop_id': 2,
                    'route_id': 1,
                    'direction': 1,  # 0: forward, 1 :backward, 2: loop
                    'pl_df': 1,  # default performance level
                    'serv_acc_df': 0.85,  # default service acceleration rate in % of maximum train acc rate
                    'serv_brk_df': 0.85,  # default service braking rate in % of maximum train brake rate
                    'coast_vec_df': [[-1, -1]],  # [distant, speed], default coasting vector [-1, -1]: no coasting
                    'dwell_time': 20, 'start_time': '06:00:00',  # [[hour], [min], [sec]]
                    'depart_offset': 0,  # the departure time offset to the start time
                    'time_tbl': [[60, 30, 90, 120, 90, 300, 90, 90, 120],  # duration
                                 [480, 120, 90, 180, 120, 360, 90, 180, 480]]  # headway
                    }

        rdop_121 = {'rdop_id': 9,
                    'route_id': 2,
                    'direction': 0,  # 0: forward, 1 :backward, 2: loop
                    'pl_df': 1,  # default performance level
                    'serv_acc_df': 0.85,  # default service acceleration rate in % of maximum train acc rate
                    'serv_brk_df': 0.85,  # default service braking rate in % of maximum train brake rate
                    'coast_vec_df': [[-1, -1]],  # [distant, speed], default coasting vector [-1, -1]: no coasting
                    'dwell_time': 20, 'start_time': '06:00:00',  # [[hour], [min], [sec]]
                    'depart_offset': 0,  # the departure time offset to the start time
                    'time_tbl': [[60, 30, 90, 120, 90, 300, 90, 90, 120],  # duration
                                 [480, 120, 90, 180, 120, 360, 90, 180, 480]]  # headway
                    }

        rdop_122 = {'rdop_id': 10,
                    'route_id': 2,
                    'direction': 1,  # 0: forward, 1 :backward, 2: loop
                    'pl_df': 1,  # default performance level
                    'serv_acc_df': 0.85,  # default service acceleration rate in % of maximum train acc rate
                    'serv_brk_df': 0.85,  # default service braking rate in % of maximum train brake rate
                    'coast_vec_df': [[-1, -1]],  # [distant, speed], default coasting vector [-1, -1]: no coasting
                    'dwell_time': 20, 'start_time': '06:00:00',  # [[hour], [min], [sec]]
                    'depart_offset': 0,  # the departure time offset to the start time
                    'time_tbl': [[60, 30, 90, 120, 90, 300, 90, 90, 120],  # duration
                                 [480, 120, 90, 180, 120, 360, 90, 180, 480]]  # headway
                    }

        rdop_212 = {'rdop_id': 3,
                    'route_id': 1,
                    'direction': 0,  # 0: forward, 1 :backward, 2: loop
                    'pl_df': 1,  # default performance level
                    'serv_acc_df': 0.85,  # default service acceleration rate in % of maximum train acc rate
                    'serv_brk_df': 0.85,  # default service braking rate in % of maximum train brake rate
                    'coast_vec_df': [[-1, -1]],  # [distant, speed], default coasting vector [-1, -1]: no coasting
                    'dwell_time': 20, 'start_time': '06:00:00',  # [[hour], [min], [sec]]
                    'depart_offset': 0,  # the departure time offset to the start time
                    'time_tbl': [[60],  # duration
                                 [120]]  # headway
                    }
        rdop_222 = {'rdop_id': 4,
                    'route_id': 1,
                    'direction': 1,  # 0: forward, 1 :backward, 2: loop
                    'pl_df': 1,  # default performance level
                    'serv_acc_df': 0.85,  # default service acceleration rate in % of maximum train acc rate
                    'serv_brk_df': 0.85,  # default service braking rate in % of maximum train brake rate
                    'coast_vec_df': [[-1, -1]],  # [distant, speed], default coasting vector [-1, -1]: no coasting
                    'dwell_time': 20, 'start_time': '06:00:00',  # [[hour], [min], [sec]]
                    'depart_offset': 0,  # the departure time offset to the start time
                    'time_tbl': [[60],  # duration
                                 [120]]  # headway
                    }

        rdop_311 = {'rdop_id': 5,
                    'route_id': 1,
                    'direction': 0,  # 0: forward, 1 :backward, 2: loop
                    'pl_df': 1,  # default performance level
                    'serv_acc_df': 0.85,  # default service acceleration rate in % of maximum train acc rate
                    'serv_brk_df': 0.85,  # default service braking rate in % of maximum train brake rate
                    'coast_vec_df': [[-1, -1]],  # [distant, speed], default coasting vector [-1, -1]: no coasting
                    'dwell_time': 20, 'start_time': '06:00:00',  # [[hour], [min], [sec]]
                    'depart_offset': 0,  # the departure time offset to the start time
                    'time_tbl': [[60],  # duration
                                 [180]]  # headway
                    }
        rdop_312 = {'rdop_id': 6,
                    'route_id': 1,
                    'direction': 1,  # 0: forward, 1 :backward, 2: loop
                    'pl_df': 1,  # default performance level
                    'serv_acc_df': 0.85,  # default service acceleration rate in % of maximum train acc rate
                    'serv_brk_df': 0.85,  # default service braking rate in % of maximum train brake rate
                    'coast_vec_df': [[-1, -1]],  # [distant, speed], default coasting vector [-1, -1]: no coasting
                    'dwell_time': 20, 'start_time': '06:00:00',  # [[hour], [min], [sec]]
                    'depart_offset': 0,  # the departure time offset to the start time
                    'time_tbl': [[60],  # duration
                                 [180]]  # headway
                    }

        rdop_321 = {'rdop_id': 7,
                    'route_id': 2,
                    'direction': 0,  # 0: forward, 1 :backward, 2: loop
                    'pl_df': 1,  # default performance level
                    'serv_acc_df': 0.85,  # default service acceleration rate in % of maximum train acc rate
                    'serv_brk_df': 0.85,  # default service braking rate in % of maximum train brake rate
                    'coast_vec_df': [[-1, -1]],  # [distant, speed], default coasting vector [-1, -1]: no coasting
                    'dwell_time': 20, 'start_time': '06:00:00',  # [[hour], [min], [sec]]
                    'depart_offset': 90,  # the departure time offset to the start time
                    'time_tbl': [[60],  # duration
                                 [360]]  # headway
                    }
        rdop_322 = {'rdop_id': 8,
                    'route_id': 2,
                    'direction': 1,  # 0: forward, 1 :backward, 2: loop
                    'pl_df': 1,  # default performance level
                    'serv_acc_df': 0.85,  # default service acceleration rate in % of maximum train acc rate
                    'serv_brk_df': 0.85,  # default service braking rate in % of maximum train brake rate
                    'coast_vec_df': [[-1, -1]],  # [distant, speed], default coasting vector [-1, -1]: no coasting
                    'dwell_time': 20, 'start_time': '06:00:00',  # [[hour], [min], [sec]]
                    'depart_offset': 90,  # the departure time offset to the start time
                    'time_tbl': [[60],  # duration
                                 [360]]  # headway
                    }

        self.op_params = {'op_cases': [op_case_1, op_case_2, op_case_3],
                          'route_ops': [rdop_111, rdop_112, rdop_121, rdop_122, rdop_212, rdop_222, rdop_311, rdop_312,
                                        rdop_321, rdop_322], 'df_case_id': 1}

    def __sim_params_temp__(self):
        self.sim_params = {'ts': 0.1, 't_op': 0, 'dwell_disturb': 1, 'acc_disturb': 1}  # disturb: add disturbance to [dwell time, acc]
        # self.sim_params = sim_params


class System:
    def __init__(self, sys_temp):  # sys_temp : system template; sys_type: system type
        self.system_temp = sys_temp
        self.net_params = copy.deepcopy(sys_temp.net_params)
        self.tr_params = copy.deepcopy(sys_temp.tr_params)
        self.pwr_params = copy.deepcopy(sys_temp.pwr_params)
        self.op_params = copy.deepcopy(sys_temp.op_params)
        self.sim_params = copy.deepcopy(sys_temp.sim_params)
        self.profiles = []

    def gen4sim(self):  # generate and convert parameters for simulation purpose
        self.network_gen4sim()
        self.train_gen4sim()
        self.pwr_system_gen4sim()
        self.operation_gen4sim()
        self.simulation_gen4sim()

    # Use a breakpoint in the code line below to debug your script.

    def network_gen4sim(self):
        self.net_params_4sim = copy.deepcopy(self.net_params)
        for r in self.net_params_4sim['routes']:
            r['stations'][0] = np.array(r['stations'][0]) * 1000
            r['speed_limit_c'] = np.array(r['speed_limit_c'])
            r['speed_limit_c'][0] = r['speed_limit_c'][0] * 1000
            r['speed_limit_c'][1] = r['speed_limit_c'][1] / 3.6
            r['grad_c'] = np.array(r['grad_c'])
            r['grad_c'][0] = r['grad_c'][0] * 1000
            r['grad_c'][1] = r['grad_c'][1] / 100
            r['cur_c'] = np.array(r['cur_c'])
            r['cur_c'][0] = r['cur_c'][0] * 1000

    def train_gen4sim(self):
        self.tr_params_4sim = copy.deepcopy(self.tr_params)

        for tp in self.tr_params_4sim['trains']:
            # train_m = tr.Train(tp['train_type'])
            # train_m.__char_tract__()
            # tp['char_tract_w'] = train_m.model['char_tract_w']
            w = np.ones([4]) * np.array(tp['w_t']) + np.array(tp['p_load'][0]) \
                * np.array(tp['w_person']) / 1000
            tp['w'] = w

    def pwr_system_gen4sim(self):
        self.pwr_params_4sim = copy.deepcopy(self.pwr_params)

    def operation_gen4sim(self):
        self.op_params_4sim = copy.deepcopy(self.op_params)
        for rdop in self.op_params_4sim['route_ops']:
            t = datetime.datetime.strptime(rdop['start_time'], '%H:%M:%S')
            rdop['start_time_sec'] = datetime.timedelta(hours=t.hour, minutes=t.minute,
                                                        seconds=t.second).total_seconds()
            rdop['start_time_sec'] = int(rdop['start_time_sec'])

            # print(oc['start_time'])

    def simulation_gen4sim(self):
        self.sim_params_4sim = copy.deepcopy(self.sim_params)

    def run_simulation(self, msg_txt):

        # start system simulation
        msg_txt.insert('insert', "hello world, let's go and have nice trips!" + '\n')
        msg_txt.update()
        print(f"hello world, let's go and have nice trips!")  # Press Ctrl+F8 to toggle the breakpoint.

        self.net4sim = net.Network(self)

        ts = self.net4sim.sim_params['ts']  # sampling time for simulation
        msg_txt.insert('insert', self.net4sim.trips_info['current state'])
        msg_txt.update()
        # msg_txt.config(state=DISABLED)

        while self.net4sim.trips_info['no_active_trips'] > 0 or self.net4sim.sim_params['t_op'] == 0:
            # pre_state = self.net4sim.trips_info['current state']
            self.net4sim.next_state()
            self.net4sim.sim_params['t_op'] = self.net4sim.sim_params['t_op'] + ts
            # now_state = self.net4sim.trips_info['current state']

            if self.net4sim.trips_info['trips_changed'] == 1:
                msg_txt.configure(state='normal')
                msg_txt.insert('insert', self.net4sim.trips_info['current state'])
                msg_txt.update()
                msg_txt.see('end')
                msg_txt.configure(state='disable')

        if self.net4sim.sim_params['dwell_disturb'] == 1 and self.net4sim.sim_params['acc_disturb'] == 0:
            prof_name = 'c' + str(self.net4sim.df_case['case_id']) \
                        + 'rd' + str(self.net4sim.df_case['rd_ops']) \
                        + '_dd'
        elif self.net4sim.sim_params['dwell_disturb'] == 0 and self.net4sim.sim_params['acc_disturb'] == 1:
            prof_name = 'c' + str(self.net4sim.df_case['case_id']) \
                        + 'rd' + str(self.net4sim.df_case['rd_ops']) \
                        + '_da'
        elif self.net4sim.sim_params['dwell_disturb'] == 1 and self.net4sim.sim_params['acc_disturb'] == 1:
            prof_name = 'c' + str(self.net4sim.df_case['case_id']) \
                        + 'rd' + str(self.net4sim.df_case['rd_ops']) \
                        + '_d'
        else:
            prof_name = 'c' + str(self.net4sim.df_case['case_id']) \
                        + 'r' + str(self.net4sim.df_case['rd_ops'])

        sys_mata = 'results/achieve_' + prof_name + '.sim_data'
        ut.save_sim_data(self.net4sim, sys_mata)  # save simulation data
        self.net4sim.df_case['p_filename'] = sys_mata
        self.net4sim.df_case['simulated'] = 1  # default op case for simulation simulated
        idx_c = next((i for (i, c) in enumerate(self.op_params['op_cases'])
                      if c['case_id'] == self.net4sim.df_case['case_id']), None)
        self.op_params['op_cases'][idx_c]['simulated'] = self.net4sim.df_case[
            'simulated']  # set default op case simulated
        self.op_params['op_cases'][idx_c]['p_filename'] = self.net4sim.df_case[
            'p_filename']  # set default op case simulated

        ui.save_system(self, self.filename)
        # msg_txt.config(state=NORMAL)
        msg_txt.insert('insert', 'System simulation is completed! ' + '\n')
        msg_txt.update()
        msg_txt.see('end')
        # msg_txt.config(state=DISABLED)

        print('System simulation is completed! ')

        return 'Completed'

        # type_profile = 1
        # 1 : v to x; 2: x to t; 3: pwr to t; 4: a to t; 5: a to x; 6: p to x
        # 21 : net pwr to time
        # idx = [1]         # idx=0 for first trip or first substation
        # idx = [-1]        # idx=0 for first trip or first substation
        # ut.plot_profiles(trips, type_profile, idx)
        # f = ut.plot_profiles(system, type_profile, idx)

        # print(train_profile[1:3])
        # train_resistance(tr_params)
        # train_braking(tr_params, ts)
