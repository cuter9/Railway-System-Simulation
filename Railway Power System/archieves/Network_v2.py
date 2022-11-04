import numpy as np
import Train as tr
import PwrSystem as ps
import Utilities as ut
import datetime


class Network_1:
    def __init__(self, system):
        self.net_params = system.net_params_4sim
        self.tr_params = system.tr_params_4sim
        self.pwr_params = system.pwr_params_4sim
        self.op_params = system.op_params_4sim
        self.sim_params = system.sim_params_4sim
        self.routes = []

        self.df_case_id = self.op_params['df_case']
        idx_c = next((i for (i, c) in enumerate(self.op_params['op_cases']) if c['case_id'] == self.df_case_id))
        self.df_case = self.op_params['op_cases'][idx_c]
        self.df_rdop_id = self.df_case['rd_ops']
        # df_rdop_id = [rdop_id1, rdop_id2, rdop_id3, ...]; rdop: route_id, direction, op_parameters

        idx_rd = []
        for rd in self.df_rdop_id:
            idx_rd = idx_rd.extend(
                [i for (i, rd) in enumerate(self.op_params['route_ops']) if rd['rdop_id'] == self.df_op_case])
        idx_rd = list(set(idx_rd))
        self.df_rd_ops = []
        self.df_rd_ops = self.df_rd_ops.extend(self.op_params['route_ops'][i] for i in idx_rd)

        self.trips_info = {'no_active_trips': 0}
        self.init_network()

    def init_network(self):
        self.sim_params['t_op'] = 0
        for rdop in self.df_rd_ops:
            self.op_params_rd = rdop
            idx_net = next((i for (i, n) in enumerate(self.net_params)
                            if n['route_id'] == rdop['route_ip'] and n['directiion'] == rdop['direction']), None)
            self.net_params_rd = self.net_params[idx_net]

            tr_type = rdop['train_type']
            idx_tr = next((idx for (idx, t) in enumerate(self.tr_params['trains']) if t['train_type'] == tr_type), None)
            self.tr_params_rd = self.tr_params['trains'][idx_tr]  # the train type for simulation

            pn_id = rdop['df_pwrnet_id']
            idx_pn = next((i for (i, pn) in enumerate(self.pwr_params['pwr_nets']) if pn['pwrnet_id'] == pn_id), None)
            self.pwr_params_rd = self.pwr_params['pwr_nets'][idx_pn]

            self.sim_params_rd = self.sim_params

            route = Network(self)
            self.trips_info['no_active_trips'] += route['no_active_trips']
            self.routes = self.routes.extend(route)

    def next_state(self):
        self.trips_info['current state'] = ''
        for r in self.routes:
            r.sim_params.update(self.sim_params)
            r.__next_state__()
            self.trips_info['current state'] = self.trips_info['current state'] \
                                               + 'Route ' + r['route_id'] + 'Direction' + r['direction'] + ': ' \
                                               + r.trips_info['current state'] + ' \n'
            self.trips_info['no_active_trips'] += r['no_active_trips']


class Network:

    def __init__(self, system):
        self.net_params = system.net_params_df
        self.tr_params = system.tr_params_df
        self.pwr_params = system.pwr_params_df
        self.op_params = system.op_params_df
        self.sim_params = system.sim_params

        self.sim_params['t_op'] = 0
        t_op = self.sim_params['t_op']

        self.headway = self.op_params['time_tbl'][1]
        # self.trips_info = {'first_trip_id': [1, 1], 'last_trip_id': [0, 0],
        #                   'no_trips': [0, 0], 'active_trips': [[0, 0], [0, 0]]}
        self.trips_info = {'no_active_trips': 0}
        self.active_trips = []

        self.train_m = tr.Train(**self.tr_params)  # create a model train
        self.train_m.state['acc_rate'] = self.train_m.model['acc_rate_max']
        self.train_m.__char_tract__()
        # print(self.train.state)

        self.pwr_net = ps.PwrNet(self.pwr_params, self.sim_params)  # initiate power system

        self.__gen_time_table__()

        self.op_params['next_depart_index'] = 0
        n = self.op_params['next_depart_index'] + 1
        self.__init_a_trip__(n, t_op)
        # print(len(self.active_trips), self.active_trips[0])

    def __gen_time_table__(self):
        self.op_params['depart_time'] = [0]
        ldt = 0  # last_depart_time
        for dt, ht in zip(self.op_params['time_tbl'][0], self.op_params['time_tbl'][1]):
            no_trip = int(np.ceil(dt * 60 / ht)) + 1
            self.op_params['depart_time'] = \
                np.append(self.op_params['depart_time'], [(lambda x: (x + 1) * ht + ldt)(t) for t in range(no_trip)])
            ldt = self.op_params['depart_time'][-1]

    def __init_a_trip__(self, n, t_op):
        train = tr.Train(**self.tr_params)
        train.state['pl'] = self.op_params['pl_df']
        train.state['ato_speed'] = train.state['pl'] * train.model['max_speed'] / 3.6  # covert to m/s
        train.state['serv_acc_max'] = train.model['acc_rate_max'] * self.op_params['serv_acc_df']
        train.state['acc_rate'] = train.state['serv_acc_max']
        train.state['serv_brk_max'] = train.model['brake_rate_max'] * self.op_params['serv_brk_df']
        train.state['brk_rate'] = train.state['serv_brk_max']
        train.state['coast_vect'] = np.multiply(self.op_params['coast_vec_df'], [1000, 1 / 3.6])  # covert to [m, m/s]
        # self.trips_info['no_trips'] = np.add(self.trips_info['no_trips'], [1, 1])
        # self.trips_info['last_trip_id'] = [n, n]
        # self.trips_info['active_trips'] = np.add(self.trips_info['active_trips'], [[1, 1], [1, 1]])
        self.active_trips = self.active_trips + \
                            [{'trip_id': n, 'train': train, 'depart_time': t_op, 'travel_time': 0, 'active': 1,
                              'profile': [[0], [0], [0], [0], [0], [0]]}]  # [t, x, v, a, traction, power]

        self.trips_info['no_active_trips'] = self.trips_info['no_active_trips'] + 1
        op_time = self.op_params['start_time_sec'] + t_op
        op_time_hms = datetime.timedelta(seconds=int(op_time))
        info = str(op_time_hms) + ': Trip ' + str(n) + ' enters service. No. of active trips in the line: ' \
               + str(self.trips_info['no_active_trips'])
        print(info)

        self.trips_info['current state'] = info
        # self.msg_txt.insert('insert', self.trips_info['current state'] + '\n')
        # self.msg_txt.update()

        if self.op_params['next_depart_index'] < len(self.op_params['depart_time']) - 1:
            self.op_params['next_depart_index'] = self.op_params['next_depart_index'] + 1
            self.op_params['next_depart_time'] = self.op_params['depart_time'][self.op_params['next_depart_index']]

    def __next_state__(self):
        ts = self.sim_params['ts']
        t_op = self.sim_params['t_op']
        if t_op >= self.op_params['next_depart_time'] and \
                self.op_params['next_depart_index'] < len(self.op_params['depart_time']) - 1:
            n = self.op_params['next_depart_index'] + 1
            self.__init_a_trip__(n, t_op)
            self.active_trips[n - 1]['profile'] = [[t_op], [0], [0], [0], [0], [0]]

        pwr_instant = 0
        for trip in self.active_trips:
            if trip['active'] == 1:
                if trip['train'].state['loc'] >= self.net_params['stations'][0][-1]:
                    trip['travel_time'] = self.sim_params['t_op'] - trip['depart_time']
                    trip['active'] = 0
                    self.trips_info['no_active_trips'] = self.trips_info['no_active_trips'] - 1
                    op_time = self.op_params['start_time_sec'] + t_op
                    op_time_hms = datetime.timedelta(seconds=int(op_time))
                    info = str(op_time_hms) + ': Trip ' + str(trip['trip_id']) \
                           + ' arrive at the terminal station and stops the service. No. of active trips  in the line: ' \
                           + str(self.trips_info['no_active_trips'])
                    print(info)
                    self.trips_info['current state'] = info
                    # self.msg_txt.insert('insert', self.trips_info['current state'] + '\n')
                    # self.msg_txt.update()

                    # break
                else:
                    self.__update_trip__(trip)

                if self.pwr_params['pwr_reg'] == 1 or \
                        (self.pwr_params['pwr_reg'] == 0 and trip['train'].state['power'] >= 0):
                    pwr_instant = pwr_instant + trip['train'].state['power']  # accumulate the power of each active trip

        self.pwr_net.__whole_pwr__(pwr_instant, t_op + ts)

        # self.sim_params['t_op'] = t_op + ts

    def __update_trip__(self, trip):  # update the nth active trip state for the next time step
        train = trip['train']
        ts = self.sim_params['ts']
        t_op = self.sim_params['t_op'] + ts

        a0 = train.state['acc_rate']  # current acc
        v0 = train.state['speed']  # current speed
        x0 = train.state['loc']  # current location of the train
        m0 = train.state['weight']  # current weight of the train in ton
        # train_profile = train.state['profile']
        train_profile = trip['profile']
        r_tr, a_tr = train.__cal_tr_resistance__()
        r_grad, a_grad = train.__cal_grad_resistance__(self.net_params)
        r_cur, a_cur = train.__cal_cur_resistance__(self.net_params)
        res = r_tr + r_grad + r_cur  # train and track resistance

        # tract_table = self.train_m.char_tract_w[3]  # simulate with W3 weight, for available tractive force
        tract_table = self.train_m.model['char_tract_w']['tract_effort'][3]
        brake_table = self.train_m.model['char_tract_w']['brake_effort'][3]
        # simulate with W3 weight, for available tractive force
        x_pt = np.where(tract_table[0] <= v0)
        tf_max = tract_table[1][x_pt[0][-1]]  # [1] tractive, [x_pt[0][-1]] : last element
        bf_max = brake_table[1][x_pt[0][-1]]  # assume same as tractive force

        if train.state['control'] == 0:  # not need to check constraint if train is in dwell state
            a1 = train.__station_dwell__(ts)
            x1 = train.state['MAL'][0]
            v1 = train.state['MAL'][1]
            tract = 0

        else:
            if train.state['control'] == 4:  # braking to station stop      # if in pps model lock to the mode
                a1 = train.__program_stop__(ts)
            else:
                brk_prof = self.check_constraint(train)
                if train.state['control'] == 1:  # acceleration
                    a1 = train.state['serv_acc_max']
                    # a1 = tf_max / m0
                elif train.state['control'] == 2:  # cruising
                    a1 = train.__cruising__(ts)

                elif train.state['control'] == 3:  # braking to speed limit point
                    a1 = train.__atp__(ts)

                elif train.state['control'] == 4:  # braking to station stop
                    a1 = train.__program_stop__(ts)

            if abs(a1 - a0) > train.model['jerk'] * ts:  # check jerk rate compliance
                if a1 - a0 >= 0:
                    a1 = a0 + train.model['jerk'] * ts
                else:
                    a1 = a0 - train.model['jerk'] * ts

            if self.sim_params['disturbance'][1] == 0:
                a1 = a1 * (0.95 + 0.05 * np.random.rand(1))
            else:
                a1 = a1

            i = 1  # count for the effect of traction system
            if i == 1:
                f_req = a1 * m0 * (1 + train.model['inertial']) + res
                if f_req >= 0:  # in power mode
                    if f_req > tf_max:
                        a1 = (tf_max - res) / \
                             (m0 * (1 + train.model['inertial']))  # the max available power  cane be used
                        tract = tf_max
                    else:
                        tract = f_req
                elif f_req < 0:  # in regen mode
                    if - f_req > bf_max:
                        tract = - bf_max  # the less of gen brake can be supplied by mach brake to maintain the req
                    else:
                        tract = f_req
            else:
                tract = 0

            # v1 = v0 + 0.5 * (a0 + a1) * ts
            # x1 = x0 + 0.5 * (v0 + v1) * ts + 0.5 * 0.5 * (a0 + a1) * np.square(ts)
            v1 = v0 + 0.5 * a1 * ts
            x1 = x0 + 0.5 * 0.5 * (v0 + v1) * ts + 0.5 * a1 * np.square(ts)

        if tract >= 0:
            power = tract * v1 / train.model['motor_eff'] + train.model['aux_power'] * train.model['no_fleet']
        else:
            power = tract * v1 * train.model['motor_eff'] + train.model['aux_power'] * train.model['no_fleet']

        train.state['traction'] = tract
        train.state['power'] = power
        train.state['loc'] = x1
        train.state['speed'] = v1
        train.state['acc_rate'] = a1
        train_profile = np.concatenate((train_profile, [[t_op], [x1], [v1], [a1], [tract], [power]]), axis=1)
        trip['profile'] = train_profile
        trip['train'] = train

        # print(train_profile)
        # return train_profile, train

    def check_constraint(self, train):  # check conflict with speed limit
        ts = self.sim_params['ts']
        t_op = self.sim_params['t_op']
        a0 = train.state['acc_rate']  # current acc
        v0 = train.state['speed']  # current speed
        x0 = train.state['loc']  # current location of the train
        m0 = train.state['weight']  # current weight of the train
        brk_prof = train.__braking_profile__(ts)  # gen the braking profile w/o speed constraint/limit
        # t_dw = self.op_params['dwell_time'][0]

        sl = self.net_params['speed_limit_c']
        p = np.where((sl[0] > x0))  # screen out the movement authorities before current train loc
        bound_pre = p[0][0] - 1  # the previous boundary of current track section
        bound_next = p[0][0]  # the next boundary of current track section
        train.state['atp_speed'] = sl[1][bound_pre]  # the speed limit of current track section
        train.state['ato_speed'] = train.state['pl'] * train.state['atp_speed']

        MALs = sl[0:np.shape(sl)[0], bound_next:np.shape(sl)[1]]  # the next movement authorities for conflict checking
        for x, v in zip(brk_prof[0], brk_prof[1]):  # check braking profile if in conflict with the speed limit (MAL)
            for xl, vl in zip(MALs[0], MALs[1]):
                if x >= xl and v >= vl:
                    train.state['control'] = 3  # control state  = braking
                    train.state['MAL'] = [xl, vl]  # the movement authority for train to brake down to
                    return brk_prof

        st = self.net_params['stations'][0]
        p_st = np.where((st > x0))  # screen out the station before current train loc
        p_next = p_st[0][0]  # next station
        if np.size(brk_prof[0]) != 0 and np.size(p_st) != 0:
            if brk_prof[0][-1] >= st[p_next]:
                train.state['control'] = 4  # control state  = station stopping
                train.state['MAL'] = [st[p_st[0][0]], 0]  # the movement authority for train to brake down to
                train.state['dwell_left'] = self.op_params['dwell_time']
                if self.sim_params['disturbance'][0] == 1:
                    train.state['dwell_left'] = self.op_params['dwell_time'] * (0.8 + 0.4 * np.random.rand(1))
                else:
                    train.state['dwell_left'] = self.op_params['dwell_time']
                return brk_prof

        # if v0 >= train.model['max_speed'] / 3.6:
        # if v0 >= train.state['atp_speed']:
        if v0 >= train.state['ato_speed']:
            train.state['control'] = 2  # control state  = cruise
            # train.state['MAL'] = [x0, train.state['atp_speed']]  # the movement authority for train to maintain
            train.state['MAL'] = [x0, train.state['ato_speed']]  # the movement authority for train to maintain
            return brk_prof

        train.state['control'] = 1  # control state  = accelerating
        train.state['MAL'] = [self.net_params['len'] + 1, train.model['max_speed']]  # no MAL
        return brk_prof  # train acc at it max effort

    # def __check_end_of_trip__(self):  # def __new_trip_entry__(self):         def __trip_exit__(self):
