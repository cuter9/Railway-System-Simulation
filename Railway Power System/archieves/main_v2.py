import numpy as np
import Network as net
import Train as tr
from numpy import array
import Utilities as ut
import UI_Main as ui


def sys_params():
    # Use a breakpoint in the code line below to debug your script.
    print(f'hello world, let we start and have nice trips!')  # Press Ctrl+F8 to toggle the breakpoint.
    route_1 = {'len': 6.3,  # km
               'no_station': 9,
               'loc_station': np.array([0.195, 1.078, 1.813, 2.334, 2.975, 3.907, 4.789, 5.665, 6.270, 6.45]),
               'name_station': ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B11', 'B12', 'YE'],  # km
               'speed_limit_c': np.array([[0.0, 0.195, 4.82, 5.62, 6.270, 6.45],
                                          [30.0, 70.0, 30.0, 70.0, 30.0, 30.0]]),  # km/hr
               'grad_c': np.array([[0.0, 0.08, 1.04, 1.12, 1.77, 2.38, 2.93, 3.95, 4.74, 5.10, 5.62, 5.70, 6.22, 6.45],
                                   [0.0, 0.97, 0.00, 0.52, 0.00, 0.63, 0.00, -.52, 0.00, 0.30, 0.00, -2.02, 0.0,
                                    0.00]]),  # gradient in %
               'cur_c': np.array(
                   [[0.000, 0.240, 1.030, 1.120, 1.770, 1.860, 2.290, 2.380, 2.930, 3.120, 4.10, 4.40, 4.740, 4.820,
                     5.620, 5.700, 6.230, 6.450],
                    [0.000, 1000.0, 0.00, 1000.0, 0.0, 1000.0, 0.00, 1000.0, 0.00, 1000.0, 350.0, 1000.0, 0.0, 40.0,
                     0.000, 1000.0, 0.000, 0.000]])  # curvature in radius in meter
               }

    route_2 = {'len': 6.8,  # km
               'no_station': 10,
               'loc_station': np.array([0.195, 1.078, 1.813, 2.334, 2.975, 3.907, 4.789, 5.481, 6.098, 6.703, 6.80]),
               'name_station': ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'YE'],  # km
               'speed_limit_c': np.array([[0.0, 0.195, 4.82, 5.62, 6.70, 6.80],
                                          [30.0, 70.0, 70.0, 70.0, 30.0, 30.0]]),  # km/hr
               'grad_c': np.array([[0.0, 0.08, 1.04, 1.12, 1.77, 2.38, 2.93, 3.95, 4.74, 5.10, 5.45, 6.13, 6.66, 6.80],
                                   [0.0, 0.97, 0.00, 0.52, 0.00, 0.63, 0.00, -.52, 0.00, -0.52, 0.00, -0.3, 0.0,
                                    0.00]]),
               # gradient in %
               'cur_c': np.array(
                   [[0.000, 0.240, 1.030, 1.120, 1.770, 1.860, 2.290, 2.380, 2.930, 3.120, 4.10, 4.40, 4.740, 4.820,
                     5.440, 5.520, 6.050, 6.130, 6.660, 6.80],
                    [0.000, 1000.0, 0.00, 1000.0, 0.00, 1000.0, 0.0, 1000.0, 0.0, 1000.0, 350.0, 1000.0, 0.0, 1000.0,
                     0.000, 1000.0, 0.000, 1000.0, 0.0, 0.000]])  # curvature in radius in meter
               }
    net_params = {'routes': [route_1, route_2]}
    for n in net_params['routes']:
        n['loc_station'] = n['loc_station'] * 1000
        n['speed_limit_c'][0] = n['speed_limit_c'][0] * 1000
        n['speed_limit_c'][1] = n['speed_limit_c'][1] / 3.6
        n['grad_c'][0] = n['grad_c'][0] * 1000
        n['grad_c'][1] = n['grad_c'][1] / 100
        n['cur_c'][0] = n['cur_c'][0] * 1000

    tr_params = {'len': 40,  # m
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
                 'acc_serve': 0.85,
                 'acc_rate_max': 1.0,  # m/s^2
                 'brake_rate_max': 1.0,  # m/s^2
                 'brake_serve': 0.85,  # m/s^2
                 'jerk': 0.8,  # m/s^3
                 'max_speed': 70,  # km/s
                 'max_speed_lv': 65,  # km/s
                 'p_load': array([0, 60, 150, 230]),  # person
                 'line_volt': array([550, 750, 900])  # volt
                 }
    w = np.ones([4]) * tr_params['w_t'] + tr_params['p_load'] * tr_params['w_person'] / 1000
    tr_params['w'] = w
    pwr_params = {'no_BSS': 2,
                  'loc_BSS': array([0, 5]),  # kp
                  'cap_BSS': array([20, 20]),
                  'volt_BSS': 22,  # kV
                  'no_TSS': 4,
                  'loc_TSS': array([1.078, 2.334, 3.907, 5.665]),  # km
                  'cap_TSS': array([2000, 2000, 2000, 2000]),  # kW
                  'volt_TSS': 750,  # Volt
                  'range_TSS': array([[0, 1.8], [1.8, 2.9], [2.9, 4.8], [4.7, net_params['routes'][0]['len']]]),
                  # [kp, kp]
                  'R_3rail': 0.007,  # Ohm/km
                  'R_TSS_line': 0.0369,  # Ohm/km
                  'R_rail': 0.0175,  # Ohm/km
                  'pwr_reg': 0
                  }
    # op_params = {'route_id': 1,  'dwell_time': [20],
    #              'headway': [120], 'duration': [120], 'start_time': [6, 0, 0]}    # [hour, min, sec]
    op_params = {'route_id': [1], 'dwell_time': [20], 'start_time': [6, 0, 0],  # [[hour], [min], [sec]]
                 'duration': [60, 30, 90, 120, 90, 300, 90, 90, 120],
                 'headway': [480, 120, 90, 180, 120, 360, 90, 180, 480]}
    op_params['start_time_sec'] = op_params['start_time'][0] * 3600 \
                                  + op_params['start_time'][1] * 60 \
                                  + op_params['start_time'][2]
    sim_params = {'ts': 0.1, 't_op': 0, 'disturbance': [1, 1]}  # disturb: add disturbance to [dwell time, acc]
    return net_params, tr_params, pwr_params, op_params, sim_params


def sys_sim(params):
    net_params, tr_params, pwr_params, op_params, sim_params = sys_params()
    if params['headway'][0] != -1:  # used default data for generate time table
        op_params = params
        op_params['start_time'] = [6, 0, 0]
        op_params['start_time_sec'] = op_params['start_time'][0] * 3600 \
                                      + op_params['start_time'][1] * 60 \
                                      + op_params['start_time'][2]

    r_id = op_params['route_id'][0] - 1
    system = net.Network(net_params['routes'][r_id], tr_params, pwr_params, op_params, sim_params)
    ts = sim_params['ts']  # sampling time for simulation
    # t_op = sim_params['t_op']  # operation time
    # t_op = ts
    # n_ts = int(op_params['duration'] * 60 / ts)
    # for n in range(n_ts):
    # list_active_trip = [trip['active'] for trip in system.active_trips]
    # while all(act != 0 for act in [trip['active'] for trip in system.active_trips]):
    while system.trips_info['no_active_trips'] > 0:
        system.__next_state__()
        system.sim_params['t_op'] = system.sim_params['t_op'] + ts
        # list_active_trip = [trip['active'] for trip in system.active_trips]sys_mata = 'achieve.sim_data_'
        # trips = system.active_trips

    if params['headway'][0] == -1:
        if sim_params['disturbance'][0] == 1 and sim_params['disturbance'][1] == 0:
            sys_mata = 'achieve.sim_data_' + str(op_params['route_id'][0]) + '_whole_day_time_table_1_dd'
        elif sim_params['disturbance'][0] == 0 and sim_params['disturbance'][1] == 1:
            sys_mata = 'achieve.sim_data_' + str(op_params['route_id'][0]) + '_whole_day_time_table_1_da'
        elif sim_params['disturbance'][0] == 1 and sim_params['disturbance'][1] == 1:
            sys_mata = 'achieve.sim_data_' + str(op_params['route_id'][0]) + '_whole_day_time_table_1_d'
        else:
            sys_mata = 'achieve.sim_data_' + str(op_params['route_id'][0]) + '_whole_day_time_table_1'
    else:
        if np.all((sim_params['disturbance'] == 0)):
            d = ''
        else:
            d = 'd'
        sys_mata = 'achieve.sim_data_' + \
                   'r' + str(op_params['route_id'][0]) + 'h' + str(op_params['headway'][0]) + \
                   'd' + str(op_params['dwell_time'][0]) + 'o' + str(op_params['duration'][0]) + d

    ut.__save_sim_data__(system, sys_mata)  # save simulation data
    print('System simulation is completed! ')

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


def plot_train_resistance(tr_params):
    tr.train_resistance(tr_params)


def plot_sim_data(pro_sel, pro_type, trip_no):
    # system = ut.__load_sim_data__(achieve_name)
    system = ut.__load_sim_data__(pro_sel)
    type_profile = pro_type
    # 1 : v to x; 2: x to t; 3: pwr to t; 4: a to t; 5: a to x; 6: p to x
    # 21 : net pwr to time
    idx = trip_no
    # idx = [-1]  # idx=0 for first trip or first substation
    # idx = [-1]      # idx=0 for first trip or first substation
    f = ut.plot_profiles(system, pro_type, idx)
    return f


def ui_start():
    ui.main_menu()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # sys_sim()
    # plot_sim_data()
    plot_train_resistance()
    # ui_start()
