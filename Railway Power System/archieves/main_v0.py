import numpy as np
import Network as net
import Train as tr
from numpy import array
import Utilities as ut


def main():
    # Use a breakpoint in the code line below to debug your script.
    print(f'hello world')  # Press Ctrl+F8 to toggle the breakpoint.
    net_params = {'len': 6.3,  # km
                  'no_station': 9,
                  'loc_station': array([0.195, 1.078, 1.813, 2.334, 2.975, 3.907, 4.789, 5.665, 6.270, 6.31]),  # km
                  'speed_limit_c': array([[0.0, 0.195, 4.82, 5.62, 6.270, 6.31],
                                          [30.0, 70.0, 30.0, 70.0, 70.0, 30.0]]),  # km/hr
                  'grad_c': array([[0.0, 0.08, 1.04, 1.12, 1.77, 2.38, 2.93, 3.95, 4.74, 4.83, 5.62, 5.70, 6.22, 6.31],
                                   [0.0, 0.97, 0.00, 0.52, 0.00, 0.63, 0.00, -.52, 0.00, 0.30, 0.00, -2.02, 0.0,
                                    0.00]]),  # gradient in %
                  'cur_c': array([[0.000, 0.240, 1.030, 1.120, 1.770, 1.860, 2.290, 2.380, 2.930, 3.120, 4.740, 4.820,
                                   5.620, 5.700, 6.230, 6.310],
                                  [0.000, 1000.0, 0.00, 1000.0, 0.00, 1000.0, 0.00, 1000.0, 0.00, 1000.0, 0.00, 40.0,
                                   0.000, 1000.0, 0.000, 0.000]])  # curvature in radius in meter
                  }
    net_params['loc_station'] = net_params['loc_station'] * 1000
    net_params['speed_limit_c'][0] = net_params['speed_limit_c'][0] * 1000
    net_params['speed_limit_c'][1] = net_params['speed_limit_c'][1] / 3.6
    net_params['grad_c'][0] = net_params['grad_c'][0] * 1000
    net_params['grad_c'][1] = net_params['grad_c'][1] / 100
    net_params['cur_c'][0] = net_params['cur_c'][0] * 1000

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
                 'motor_eff': 0.85,
                 'acc_serve': 0.85,
                 'acc_rate_max': 1.0,  # m/s^2
                 'brake_rate_max': 1.0,  # m/s^2
                 'brake_serve': 0.85,  # m/s^2
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
                  'no_TSS': 4,
                  'loc_TSS': array([1.078, 2.334, 3.907, 5.665]),  # km
                  'cap_TSS': array([1000, 1000, 1000, 1000]),  # kW
                  'range_TSS': array([[0, 1.8], [1.8, 2.9], [2.9, 4.8], [4.7, net_params['len']]]),  # [kp, kp]
                  'R_3rail': 0.007,  # Ohm/km
                  'R_TSS_line': 0.0369,  # Ohm/km
                  'R_rail': 0.0175  # Ohm/km
                  }
    op_params = {'headway': 120, 'dwell_time': 20, 'duration': 12}
    sim_params = {'ts': 0.1, 't_op': 0}
    sys = net.Network(net_params, tr_params, pwr_params, op_params, sim_params)
    ts = sim_params['ts']  # sampling time for simulation
    # t_op = sim_params['t_op']  # operation time
    t_op = ts
    n_ts = int(op_params['duration'] * 60 / ts)
    for n in range(n_ts):
        sys.__next_state__()
        sys.sim_params['t_op'] = sys.sim_params['t_op'] + ts
#        train = sys.active_trips[n]['trip_train']
#        if train.state['loc'] >= net_params['loc_station'][-1]:
#            print('trip ', n, 'is at the end of line')
#            break

    trips = sys.active_trips
    type_profile = 1
    idx = [4]
    ut.plot_profiles(trips, type_profile, idx)
    # xd = train_profile[0]
    # yd = train_profile[-1]
    # d_plot = np.concatenate(([xd], [yd]), axis=0)
    # ut.plot_data(np.expand_dims(d_plot, axis=0))

    # ut.plot_data(np.expand_dims(train_profile[1:3], axis=0))
    # ut.plot_data(np.expand_dims(train_profile[0:2], axis=0))
    # print(train_profile[1:3])

    # train_resistance(tr_params)
    # train_braking(tr_params, ts)


def train_resistance(tr_params):
    train = tr.Train(**tr_params)
    no_speed_pt = 100  # no of points to setup the traction characteristics
    speed_pt = np.arange(no_speed_pt + 1) * (train.model['max_speed'] / no_speed_pt) / 3.6  # m/sec
    tr_res = np.empty([4, 2, no_speed_pt + 1])  # train resistance to speed characteristic in NT

    for i in range(4):
        train.state['weight'] = train.model['w'][i]
        tr_res_temp = np.empty([no_speed_pt + 1])
        for j in range(no_speed_pt + 1):
            train.state['speed'] = speed_pt[j]
            tr_res_temp[j] = train.__cal_tr_resistance__()[0]
        tr_res_2D = np.expand_dims(tr_res_temp, axis=0)
        speed_pt_2D = np.expand_dims(speed_pt, axis=0)
        tr_res_2D = np.concatenate((speed_pt_2D, tr_res_2D), axis=0)
        tr_res[i] = tr_res_2D

    ut.plot_data(tr_res)


def train_braking(tr_params, ts):
    train = tr.Train(**tr_params)
    br_p = train.__braking_profile__(ts)
    ut.plot_data(np.expand_dims(br_p, axis=0))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
