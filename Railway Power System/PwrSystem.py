import numpy as np


class PwrNet:
    def __init__(self, *pwr_params):
        self.pwr_config = pwr_params[0]
        self.sim_params = pwr_params[1]
        self.__net_init__()

    def __net_init__(self):
        t_op = self.sim_params['t_op']
        #        self.bss_state = []
        self.bss = []
        no_bss = self.pwr_config['no_BSS']
        for i in range(no_bss):
            bss_config = {'volt_BSS': self.pwr_config['volt_BSS'],
                          'loc': self.pwr_config['BSS'][0][i],
                          'cap': self.pwr_config['BSS'][1][i]}
            self.bss = self.bss + [BSS(bss_config, self.sim_params)]

        self.tss = []
        no_tss = self.pwr_config['no_TSS']
        for i in range(no_tss):
            tss_config = {'volt_TSS': self.pwr_config['volt_TSS'],
                          'loc': self.pwr_config['TSS'][0][i],
                          'cap': self.pwr_config['TSS'][1][i]}
            self.tss = self.tss + [TSS(tss_config, self.sim_params)]

        self.state = {'power': [t_op, 0]}
        self.pwr_profile = [[t_op], [0]]  # [t, p]

    def __whole_pwr__(self, pwr_now, t_op):
        self.state['power'] = np.array([t_op, pwr_now])
        self.pwr_profile = np.concatenate((self.pwr_profile, [[t_op], [pwr_now]]), axis=1)


class BSS:
    def __init__(self, *bss_params):
        self.bss_params = bss_params[0]
        self.sim_params = bss_params[1]
        self.state = [{'power': 0, 'volt': self.bss_params['volt_BSS'], 'current': 0}]
        self.pwr_profile = [[], [], [], []]  # [t, v, i, p]
        self.__bss_init__()

    def __bss_init__(self):
        t_op = self.sim_params['t_op']
        self.pwr_profile = [[t_op], [], [], []]  # [t, v, i, p]


class TSS:
    def __init__(self, *tss_params):
        self.tss_params = tss_params[0]
        self.sim_params = tss_params[1]
        self.state = [{'power': 0, 'volt': self.tss_params['volt_TSS'], 'current': 0}]
        self.pwr_profile = [[], [], [], []]     # [t, v, i, p]
        self.__tss_init__()

    def __tss_init__(self):
        t_op = self.sim_params['t_op']
        self.pwr_profile = [[t_op], [], [], []]     # [t, v, i, p]

