import numpy as np
import time
import Utilities as ut


class Train:
    def __init__(self, **tr_params):
        self.model = tr_params
        self.state = {'acc_rate': 0, 'speed': 0, 'loc': 0, 'control': 1, 'dwell_left': 0, 'f_motor': 0,
                      'MAL': [0, self.model['max_speed']],  # MAL: movement authority
                      'weight': self.model['w'][3]}

    def __char_tract__(self):
        max_tract_pwr = self.model['motor_pwr'] * self.model['no_tract_motor'] * self.model['motor_eff']
        # W = np.ones([4]) * self.model['w_t'] + self.model['p_load'] * self.model['w_person'] / 1000
        W = self.model['w']
        tr_acc = self.model['acc_rate_max']
        x1 = max_tract_pwr / (tr_acc * W)  # max train speed (m/sec) for maximum power constraint
        y1 = tr_acc * W  # maximum traction effort (kN)
        x2 = (self.model['max_speed_lv'] / 3.6) * np.ones([4])  # maximum speed (m/sec) for max line voltage
        for a, b in zip(x1, x2):
            if a > b:
                print("the max. line volt speed is less than max. effort speed,", a * 3.6)
                quit()
        # x2 = 18 * np.ones([4])   # maximum speed (m/sec) for max line voltage
        y2 = max_tract_pwr * x1 / x2  # max traction effort (kN) at max speed for line voltage constraint

        no_speed_pt = 100  # no of points to setup the traction characteristics
        speed_pt = np.arange(no_speed_pt + 1) * (self.model['max_speed'] / no_speed_pt) / 3.6  # m/sec
        self.char_tract_w = np.empty([4, 2, no_speed_pt + 1])  # traction effort to speed characteristic in NT
        self.char_tract_current_w = np.empty([4, 2, no_speed_pt + 1])  # current to speed characteristic in NT
        for i in range(4):
            const_tract = np.array([y1[i] for s in speed_pt if 0 <= s <= x1[i]])  # gen constant effort region
            char_tract = const_tract

            const_pwr = np.array([(lambda x: max_tract_pwr / x)(s)  # gen constant pwr region
                                  for s in speed_pt if (x1[i] < s <= x2[i])])
            char_tract = np.append(char_tract, const_pwr)

            const_volt = np.array([(lambda x: max_tract_pwr * x2[i] / np.square(x))(s)  # gen constant volt region
                                   for s in speed_pt if (x2[i] < s <= self.model['max_speed'])])
            char_tract = np.append(char_tract, const_volt)
            char_tract_current = char_tract * speed_pt * self.model['line_volt'][1] / self.model['motor_eff']

            # char_tract_2D = np.reshape(char_tract, (-1, len(char_tract)))
            char_tract_2D = np.expand_dims(char_tract, axis=0)  # extend dim in 0 dim to include speed vector
            char_tract_current_2D = np.expand_dims(char_tract_current, axis=0)  # extend dim to include speed vector

            # speed_pt_2D = np.reshape(speed_pt, (-1, len(speed_pt)))
            speed_pt_2D = np.expand_dims(speed_pt, axis=0)
            char_tract_2D = np.concatenate((speed_pt_2D, char_tract_2D), axis=0)
            char_tract_current_2D = np.concatenate((speed_pt_2D, char_tract_current_2D), axis=0)

            self.char_tract_w[i] = char_tract_2D
            self.char_tract_current_w[i] = char_tract_current_2D
        self.model['char_tract_w'] = self.char_tract_w
        self.model['char_tract_current_w'] = self.char_tract_current_w
        # print(self.char_tract_w[2])
        ut.plot_data_tk(self.char_tract_w)
        ut.plot_data(self.char_tract_current_w)
        # ut.plot_data(np.expand_dims(self.char_tract_w[3], axis=0))
        # ut.plot_data(np.expand_dims(self.char_tract_current_w[3], axis=0))
        return self.char_tract_w, self.char_tract_current_w

    def __cal_tr_resistance__(self):
        v0 = self.state['speed'] * 3.6  # km/hr
        m0 = self.state['weight']
        rin = self.model['inertial']
        n_axle = self.model['no_axle']
        n_v = self.model['no_fleet']
        area = self.model['area_f']
        r_tr = (6.4 * m0 + 130 * n_axle + 0.14 * m0 * v0 + (0.046 + 0.0065 * (n_v - 1)) * area * np.square(v0)) / 1000
        a_tr = -r_tr / (m0 * (1 + rin))  # equivalent deceleration
        return r_tr, a_tr

    def __cal_grad_resistance__(self, net_params):
        x0 = self.state['loc']
        m0 = self.state['weight']
        rin = self.model['inertial']
        p_loc_grad = np.where(net_params['grad_c'][0] <= x0)[0][-1]  # index of section the train entering
        grad = net_params['grad_c'][1][p_loc_grad]
        r_grad = 9.8 * m0 * np.sin(np.arctan(grad))  # in kN
        a_grad = -r_grad / (m0 * (1 + rin))  # equivalent deceleration
        return r_grad, a_grad

    def __cal_cur_resistance__(self, net_params):
        x0 = self.state['loc']
        m0 = self.state['weight']
        rin = self.model['inertial']
        p_loc_cur = np.where(net_params['cur_c'][0] <= x0)[0][-1]  # index of section the train entering
        rad = net_params['cur_c'][1][p_loc_cur]  # radius of curvature
        if rad > 0:
            r_cur = (698.544 * m0 / rad) / 1000  # kN
        else:
            r_cur = 0
        a_cur = -r_cur / (m0 * (1 + rin))  # equivalent deceleration
        return r_cur, a_cur

    def __braking_profile__(self, ts):
        x0 = self.state['loc']
        # x0 = 100
        v0 = self.state['speed']
        # v0 = 10
        de_acc = self.model['brake_serve']
        n_ts = np.int(np.ceil((v0 / de_acc) / ts))
        x = np.array([(lambda s: x0 + v0 * s - 0.5 * de_acc * np.square(s))(k * ts) for k in range(n_ts)])
        v = np.array([(lambda s: v0 - de_acc * s)(k * ts) for k in range(n_ts)])
        br_prof = np.concatenate(([x], [v]), axis=0)
        return br_prof

    def __program_stop__(self, ts):
        mal = self.state['MAL']
        x0 = self.state['loc']
        v0 = self.state['speed']
        max_b_rate = self.model['brake_rate_max']
        if x0 < mal[0] - 0.05 and v0 > mal[1]:  # 0.05 : PSS accuracy
            a1 = - np.min([0.5 * np.square(v0) / (mal[0] - x0), max_b_rate])
        else:
            a1 = 0
            self.state['control'] = 0  # train in stop state
            self.state['MAL'] = mal
        return a1

    def __station_dwell__(self, ts):
        a1 = 0
        self.state['dwell_left'] = self.state['dwell_left'] - ts  # count down
        if self.state['dwell_left'] <= 0:
            self.state['dwell_left'] = 0
            self.state['control'] = 1
        return a1

    def __cruising__(self, ts):
        mal = self.state['MAL']
        # x0 = self.state['loc']
        v0 = self.state['speed']
        b_rate = self.model['brake_serve']
        a_rate = self.model['acc_serve']
        if v0 >= 1.05 * mal[1]:  # 1.05 and 0.95 : speed regulation tolerance, jitter if less tolerance
            a1 = - b_rate
        elif v0 <= 0.95 * mal[1]:
            a1 = a_rate
        else:
            a1 = 0
        return a1

    def __atp__(self, ts):
        mal = self.state['MAL']
        x0 = self.state['loc']
        v0 = self.state['speed']
        b_rate = self.model['brake_serve']
        a_rate = self.model['acc_serve']
        max_b_rate = self.model['brake_rate_max']
        max_a_rate = self.model['acc_rate_max']

        if x0 < mal[0] and v0 > mal[1]:  # brake if target not meet, gen a target brake rate
            a1 = - np.min([- 0.5 * (np.square(mal[1]) - np.square(v0)) / (mal[0] - x0), max_b_rate])
        elif x0 < mal[0] and v0 <= mal[1]:  # acc if brake early down to target speed
            a1 = np.min([0.5 * (np.square(mal[1]) - np.square(v0)) / (mal[0] - x0), max_a_rate])
        elif x0 >= mal[0] and v0 > 1.01 * mal[1]:  # brake if over atp speed
            a1 = - b_rate
        elif x0 >= mal[0] and v0 <= 0.99 * mal[1]:  # acc if brake early down to target speed
            a1 = a_rate
        else:
            a1 = 0

        return a1


def train_resistance(tr_params):
    train = Train(**tr_params)
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
