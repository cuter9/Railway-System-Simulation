import numpy as np
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
        self.train.state['acc_rate'] = self.train.model['acc_rate_max']
        self.train.__char_tract__()

        # print(self.train.state)
        self.active_trips = [{'trip_id': 1, 'trip_train': self.train, 'depart_time': 0, 'travel_time': 0,
                              'profile': [[0], [0], [0], [0], [0], [0]]}]    # [t, x, v, a, traction, power]
        self.trips_archive = [{'trip_id': 1, 'trip_train': self.train, 'depart_time': 0, 'travel_time': 0,
                               'profile': [[0], [0], [0], [0], [0], [0]]}]
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

    def __update_trip__(self, n):  # update the nth active trip state for the next time step
        trip = self.active_trips[n]
        train = trip['trip_train']
        ts = self.sim_params['ts']
        t_op = self.sim_params['t_op'] + ts

        a0 = train.state['acc_rate']  # current acc
        v0 = train.state['speed']  # current speed
        x0 = train.state['loc']  # current location of the train
        m0 = train.state['weight']  # current weight of the train in ton
        # train_profile = train.state['profile']
        train_profile = self.active_trips[0]['profile']
        r_tr, a_tr = train.__cal_tr_resistance__()
        r_grad, a_grad = train.__cal_grad_resistance__(self.net_params)
        r_cur, a_cur = train.__cal_cur_resistance__(self.net_params)
        res = r_tr + r_grad + r_cur         # train and track resistance

        tract_table = self.train.char_tract_w[3]    # simulate with W3 weight, for available tractive force
        x_pt = np.where(tract_table[0] <= v0)
        tf_max = tract_table[1][x_pt[0][-1]]  # [1] tractive, [x_pt[0][-1]] : last element
        bf_max = tf_max     # assume same as tractive force

        if train.state['control'] == 0:  # not need to check constraint if train is in dwell state
            a1 = train.__station_dwell__(ts)
            x1 = train.state['MAL'][0]
            v1 = train.state['MAL'][1]
            tract = 0
        else:
            brk_prof = self.check_constraint(train)
            if train.state['control'] == 1:  # acceleration
                a1 = self.train.model['acc_rate_max']
                # a1 = tf_max / m0
            elif train.state['control'] == 2:  # cruising
                a1 = train.__cruising__(ts)

            elif train.state['control'] == 3:  # braking to speed limit point
                a1 = train.__atp__(ts)

            elif train.state['control'] == 4:  # braking to station stop
                a1 = train.__program_stop__(ts)

            i = 1   # count for the effect of traction system
            if i == 1:
                f_req = a1 * m0 * (1+train.model['inertial']) + res
                if f_req >= 0:      # in power mode
                    if f_req > tf_max:
                        a1 = (tf_max - res) / (m0*(1+train.model['inertial']))  # the max available power  cane be used
                        tract = tf_max
                    else:
                        tract = f_req
                elif f_req < 0:     # in regen mode
                    if - f_req > bf_max:
                        tract = - bf_max  # the less of gen brake can be supplied by mach brake to maintain the req
                        # brake
                    else:
                        tract = f_req
            else:
                tract = 0

            v1 = v0 + 0.5 * (a0 + a1) * ts
            x1 = x0 + 0.5 * (v0 + v1) * ts + 0.5 * 0.5 * (a0 + a1) * np.square(ts)

        power = tract * v1 / train.model['motor_eff'] + train.model['aux_power'] * train.model['no_fleet']
        train.state['traction'] = tract
        train.state['power'] = power
        train.state['loc'] = x1
        train.state['speed'] = v1
        train.state['acc_rate'] = a1
        train_profile = np.concatenate((train_profile, [[t_op], [x1], [v1], [a1], [tract], [power]]), axis=1)
        # train.state['profile'] = train_profile
        self.active_trips[n]['profile'] = train_profile

        self.active_trips[n]['train'] = train
        # print(train_profile)

    def check_constraint(self, train):  # check conflict with speed limit
        ts = self.sim_params['ts']
        t_op = self.sim_params['t_op']
        a0 = train.state['acc_rate']  # current acc
        v0 = train.state['speed']  # current speed
        x0 = train.state['loc']  # current location of the train
        m0 = train.state['weight']  # current weight of the train
        brk_prof = train.__braking_profile__(ts)  # gen the braking profile w/o speed constraint/limit
        # t_dw = self.op_params['dwell_time']

        sl = self.net_params['speed_limit_c']
        p = np.where((sl[0] > x0))  # screen out the movement authorities before current train loc
        bound_pre = p[0][0]-1       # the previous boundary of current track section
        bound_next = p[0][0]        # the next boundary of current track section
        train.state['atp_speed'] = sl[1][bound_pre]    # the speed limit of current track section

        MALs = sl[0:np.shape(sl)[0], bound_next:np.shape(sl)[1]]  # the next movement authorities for conflict checking
        for x, v in zip(brk_prof[0], brk_prof[1]):  # check braking profile if in conflict with the speed limit
            for xl, vl in zip(MALs[0], MALs[1]):
                if x >= xl and v >= vl:
                    train.state['control'] = 3  # control state  = braking
                    train.state['MAL'] = [xl, vl]  # the movement authority for train to brake down to
                    return brk_prof

        st = self.net_params['loc_station']
        p_st = np.where((st > x0))     # screen out the station before current train loc
        p_next = p_st[0][0]       # next station
        if np.size(brk_prof[0]) != 0 and np.size(p_st) != 0:
            if brk_prof[0][-1] >= st[p_next]:
                train.state['control'] = 4  # control state  = station stopping
                train.state['MAL'] = [st[p_st[0][0]], 0]  # the movement authority for train to brake down to
                train.state['dwell_left'] = self.op_params['dwell_time']
                return brk_prof

        # if v0 >= train.model['max_speed'] / 3.6:
        if v0 >= train.state['atp_speed']:
            train.state['control'] = 2  # control state  = cruise
            train.state['MAL'] = [x0, train.state['atp_speed']]  # the movement authority for train to maintain
            return brk_prof

        train.state['control'] = 1  # control state  = accelerating
        train.state['MAL'] = [self.net_params['len'] + 1, train.model['max_speed']]  # no MAL
        return brk_prof  # train acc at it max effort

    # def __check_end_of_trip__(self):  # def __new_trip_entry__(self):         def __trip_exit__(self):
