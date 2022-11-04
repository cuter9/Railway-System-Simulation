import numpy as np
from numpy import array
import time
import Utilities as ut


class Train:
    def __init__(self, **tr_params):
        self.model = tr_params
        self.state = {'acc_rate': 0, 'speed': 0, 'loc': 0, 'control': 1, 'dwell_left': 0, 'f_motor': 0,
                      'MAL': [0, self.model['max_speed']],      # MAL: movement authority
                      'weight': self.model['w'][3]}

    def __char_tract__(self):
        max_tract_pwr = self.model['motor_pwr'] * self.model['no_tract_motor']
        W = self.model['w']  # train weight W0, W1, W2, W3
        tc = {}
        for nt in range(2):
            if nt == 0:  # generate tractive effort
                tr_acc = self.model['acc_rate_max']
                x1 = max_tract_pwr * self.model['motor_eff'] / (
                        tr_acc * W)  # max train speed (m/sec) w/o subject to maximum power constraint
                y1 = tr_acc * W  # maximum traction effort (kN)
                x2 = (self.model['max_speed_lv'] / 3.6) * np.ones([4])  # maximum speed (m/sec) for max line voltage
                for a, b in zip(x1, x2):  # check the consistent between constant per region and constant voltage region
                    if a > b:  # speed bounded by max. line volt should be less than that bounded by max. effort
                        print("the speed bounded by max. line volt is less than that bounded by max. effort", a * 3.6)
                        quit()
                y2 = max_tract_pwr * x1 / x2  # max traction effort (kN) at max speed before max line volt constraint
            elif nt == 1:  # generate braking effort
                tr_acc = self.model['brake_rate_max']
                x1 = max_tract_pwr / (tr_acc * W * self.model['motor_eff'])  # max train speed (m/sec) w/o subject to maximum power constraint
                y1 = tr_acc * W  # maximum braking effort (kN)
                # No maximum line voltage constraint in braking mode
                x2 = (self.model['max_speed'] / 3.6) * np.ones([4])  # maximum speed (m/sec) for max line voltage
                # for a, b in zip(x1, x2):  # check the consistent between constant per region and constant voltage region
                #     if a > b:  # speed bounded by max. line volt should be less than that bounded by max. effort
                #         print("the speed bounded by max. line volt is less than that bounded by max. effort", a * 3.6)
                #        quit()
                y2 = max_tract_pwr * x1 / x2  # max traction effort (kN) at max speed under max. power constraint

            no_speed_pt = 100       # no of points to setup the traction characteristics
            speed_pt = np.arange(no_speed_pt + 1) * (self.model['max_speed'] / no_speed_pt) / 3.6  # m/sec
            char_tract_w = np.empty([len(W), 2, no_speed_pt + 1])  # traction effort to speed characteristic in NT
            char_tract_current_w = np.empty([len(W), 2, no_speed_pt + 1])  # current to speed characteristic in NT
            for i in range(len(W)):
                # generate the tractive effort (kN) and current curve w. r. to speed for each train weight
                if nt == 0:
                    const_tract = np.array([y1[i] for s in speed_pt if 0 <= s <= x1[i]])  # gen constant effort region curve
                    char_tract = const_tract
                else:
                    sbr = 3.6 * y1[i]/self.model['min_speed_rb']
                    blending_tract = np.array([sbr*s for s in speed_pt if 0 <= s < self.model['min_speed_rb']/3.6])  # gen constant effort region curve
                    char_tract = blending_tract
                    const_tract = np.array([y1[i] for s in speed_pt if self.model['min_speed_rb']/3.6 <= s <= x1[i]])  # gen constant effort region curve
                    char_tract = np.append(char_tract, const_tract)

                if nt == 0:
                    const_pwr = np.array([(lambda x: max_tract_pwr * self.model['motor_eff'] / x)(s) for s in speed_pt if (x1[i] < s <= x2[i])])   # gen constant pwr region curve
                elif nt == 1:   # braking effort
                    const_pwr = np.array([(lambda x: (max_tract_pwr / self.model['motor_eff']) / x)(s) for s in speed_pt if (x1[i] < s <= x2[i])])   # gen constant pwr region curve

                char_tract = np.append(char_tract, const_pwr)

                if nt == 0:  # only needed when gen tractive effort
                    const_volt = np.array([(lambda x: max_tract_pwr * self.model['motor_eff'] * x2[i] / np.square(x))(s) for s in speed_pt if
                                           (x2[i] < s <= self.model['max_speed'])])  # gen constant volt region curve
                    char_tract = np.append(char_tract, const_volt)

                char_tract_current = char_tract * speed_pt / (self.model['motor_eff'] * self.model['line_volt'][0][1])  # 750 v
                char_tract_2D = np.expand_dims(char_tract, axis=0)  # extend dim in 0 dim to include speed points vector
                char_tract_current_2D = np.expand_dims(char_tract_current, axis=0)  # to include speed points vector

                speed_pt_2D = np.expand_dims(speed_pt, axis=0)
                char_tract_2D = np.concatenate((speed_pt_2D, char_tract_2D), axis=0)
                char_tract_current_2D = np.concatenate((speed_pt_2D, char_tract_current_2D), axis=0)

                char_tract_w[i] = char_tract_2D
                char_tract_current_w[i] = char_tract_current_2D
            if nt == 0:
                tc['tract_effort'] = char_tract_w
                tc['tract_current'] = char_tract_current_w
                # self.model['char_tract_w'] = tc['trac_effort']
                # self.model['char_tract_w'] = tc['trac_effort']
            else:
                tc['brake_effort'] = char_tract_w
                tc['brake_current'] = char_tract_current_w
                # self.model['char_tract_w'] = tc['trac_effort']
        self.model['char_tract_w'] = tc

        # print(self.char_tract_w[2])
        # ut.plot_data(self.char_tract_w)
        # ut.plot_data_tk(self.model['char_tract_w']['brake_effort'])
        # ut.plot_data_tk(self.model['char_tract_w']['brake_current'])
        # ut.plot_data_tk(self.model['char_tract_w']['tract_effort'])
        # ut.plot_data_tk(self.model['char_tract_w']['tract_current'])

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
        grad_ratio = (x0 - net_params['grad_c'][0][p_loc_grad])/self.model['len']
        r_grad = r_grad * grad_ratio if grad_ratio < 1 else r_grad
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
            cur_ratio = (x0 - net_params['cur_c'][0][p_loc_cur]) / self.model['len']
            r_cur = r_cur * cur_ratio if cur_ratio < 1 else r_cur
        else:
            r_cur = 0
        a_cur = -r_cur / (m0 * (1 + rin))  # equivalent deceleration
        return r_cur, a_cur

    def __braking_profile__(self, ts):
        x0 = self.state['loc']
        v0 = self.state['speed']
        de_acc = self.state['serv_brk_max']             # the max service brake rate for predict the time to stop
        n_ts = np.int(np.ceil((v0 / de_acc) / ts))      # predict the time to complete stop
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
        b_rate = self.state['serv_brk_max']
        a_rate = self.state['serv_acc_max']
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
        b_rate = self.state['serv_brk_max']
        a_rate = self.state['serv_acc_max']
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

    def train_resistance(self):
        # train = Train(**tr_params)
        no_speed_pt = 100  # no of points to setup the traction characteristics
        speed_pt = np.arange(no_speed_pt + 1) * (self.model['max_speed'] / no_speed_pt) / 3.6  # m/sec
        tr_res = np.empty([4, 2, no_speed_pt + 1])  # train resistance to speed characteristic in NT

        for i in range(4):
            self.state['weight'] = self.model['w'][i]
            tr_res_temp = np.empty([no_speed_pt + 1])
            for j in range(no_speed_pt + 1):
                self.state['speed'] = speed_pt[j]
                tr_res_temp[j] = self.__cal_tr_resistance__()[0]
            tr_res_2D = np.expand_dims(tr_res_temp, axis=0)
            speed_pt_2D = np.expand_dims(speed_pt, axis=0)
            tr_res_2D = np.concatenate((speed_pt_2D, tr_res_2D), axis=0)
            tr_res[i] = tr_res_2D

        return tr_res

        # ut.plot_data(tr_res)

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

    return tr_res
    # ut.plot_data(tr_res)
