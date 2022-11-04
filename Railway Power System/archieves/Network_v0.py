import numpy as np
from numpy import array
import Train as tr
import Utilities as ut


class Network:
    # def __init__(self, **net_params):
    def __init__(self, *system_params):
        # for param in system_params:
        # print(system_params)
        self.net_params = system_params[0]
        self.tr_params = system_params[1]
        self.pwr_params = system_params[2]
        self.op_params = system_params[3]
        self.sim_params = system_params[4]
        # print(self.net_params);         print(self.tr_params)

        self.headway = self.op_params['headway']
        self.trips_info = {'first_trip_id': 1, 'last_trip_id': 1, 'no_trips': 1, 'active_trips': [1, 1]}
        self.train = tr.Train(**self.tr_params)
        self.train.state['acc_rate'] = 1
        self.train.__char_tract__()

        # print(self.train.state)
        self.active_trips = [{'trip_id': 1, 'trip_train': self.train, 'depart_time': 0, 'travel_time': 0}]
        # print(len(self.active_trips), self.active_trips[0])

    def __next_state__(self):
        # active_trips = self.active_trips()
        ts = self.sim_params['ts']
        t_op = self.sim_params['t_op']
        N = len(self.active_trips)
        for n in range(N):
            self.__update_trip__(n)

    #            self.new_trip_entry()
        self.sim_params['t_op'] = t_op + ts

    def __update_trip__(self, n):  # update the trip state for the next time step
        trip = self.active_trips[n]
        train = trip['trip_train']
        ts = self.sim_params['ts']
        t_op = self.sim_params['t_op'] + ts
        brk_prof = self.check_constraint(train)
        a0 = train.state['acc_rate']  # current acc
        v0 = train.state['speed']  # current speed
        x0 = train.state['loc']  # current location of the train
        m0 = train.state['weight']  # current weight of the train in ton
        train_profile = train.state['profile']

        if train.state['control'] == 1:     # acceleration
            x_pt = np.where(self.train.char_tract_w[3][0] <= v0)  # simulate with W3 weight
            F = self.train.char_tract_w[3][1][x_pt[0]][-1]  # [3] W3, [1] tractive, [x_pt[0]][-1] : last element
            a1 = F / m0
            v1 = v0 + 0.5 * (a1 + a0) * ts
            x1 = x0 + 0.5 * (v1 + v0) * ts
            tp = [[t_op], [x1], [v1], [a1]]

        elif train.state['control'] == 2:       # cruising
            r_tr, a_tr = train.__cal_tr_resistance__()
            r_grad, a_grad = train.__cal_grad_resistance__(self.net_params)
            r_cur, a_cur = train.__cal_cur_resistance__(self.net_params)
            F = r_tr + r_grad + r_cur
            a1 = 0
            v1 = v0 + 0.5 * (a1 + a0) * ts
            x1 = x0 + 0.5 * (v1 + v0) * ts
            tp = [[t_op], [x1], [v1], [a1]]

        elif train.state['control'] == 3:       # braking to speed limit point
            MAL = train.state['MAL']
            x1 = brk_prof[1][-1]
            v1 = brk_prof[2][-1]
            a1 = brk_prof[3][-1]
            tp = brk_prof

        elif train.state['control'] == 4:       # braking to station stop

            x1 = brk_prof[1][-1]
            v1 = brk_prof[2][-1]
            a1 = brk_prof[3][-1]
            t_dw = self.op_params['dwell_time']
            no_t_dw = t_dw/ts
            brk_prof[0] = brk_prof[0]
            tp = brk_prof

        train.state['loc'] = x1
        train.state['speed'] = v1
        train.state['acc_rate'] = a1
        train_profile = np.concatenate((train_profile, tp), axis=1)
        train.state['profile'] = train_profile
        self.active_trips[n]['train'] = train
        # print(train_profile)

    def check_constraint(self, train):  # check conflict with speed limit
        ts = self.sim_params['ts']
        t_op = self.sim_params['t_op']
        a0 = train.state['acc_rate']  # current acc
        v0 = train.state['speed']  # current speed
        x0 = train.state['loc']  # current location of the train
        m0 = train.state['weight']  # current weight of the train
        sl = self.net_params['speed_limit_c']
        p = np.where((sl[0] >= x0))[0][0]       # screen out the movement authorities before current train loc
        MALs = sl[0:np.shape(sl)[0], p:np.shape(sl)[1]]     # the movement authorities for conflict checking
        brk_prof = train.__braking_profile__(ts, t_op)    # gen the braking profile w/o speed constraint/limit
        for x, v in zip(brk_prof[1], brk_prof[2]):  # check braking profile if in conflict with the speed limit
            for xl, vl in zip(MALs[0], MALs[1]):
                if x >= xl and v >= vl:
                    train.state['control'] = 3      # control state  = braking
                    train.state['MAL'] = [xl, vl]     # the movement authority for train to brake down to
                    p_brk = np.where((brk_prof[1] < xl))[0][-1]
                    return brk_prof[0:np.shape(brk_prof)[0], p_brk:np.shape(brk_prof)[1]]

        st = self.net_params['loc_station']
        p_st = np.where((st[0] >= x0))      # screen out the station before current train loc
        if np.size(brk_prof[1]) != 0 and np.size(p_st) != 0:
            if brk_prof[1][-1] >= st[p_st[0][0]]:
                train.state['control'] = 4  # control state  = station stopping
                return brk_prof

        if v0 >= train.model['max_speed']/3.6:
            train.state['control'] = 2          # control state  = cruise
            train.state['MAL'] = [x0, train.model['max_speed']]       # the movement authority for train to maintain
            return brk_prof

        train.state['control'] = 1          # control state  = accelerating
        return brk_prof                     # train acc at it max effort

    # def __check_end_of_trip__(self):  # def __new_trip_entry__(self):         def __trip_exit__(self):
