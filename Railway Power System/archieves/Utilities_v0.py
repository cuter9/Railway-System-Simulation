import numpy as np
import matplotlib.pyplot as plt


def plot_profiles(trips, type_profile, idx_profile):
    profiles = []
    for trip in trips:
        profiles = profiles + [trip['profile']]

    in_data = []
    if type_profile == 1:  # distance - speed
        for idx in idx_profile:
            x = profiles[idx][1]  # speed
            y = profiles[idx][2]  # distance
            in_data = in_data + [[x, y]]

    elif type_profile == 2:  # time - distance
        for idx in idx_profile:
            x = profiles[idx][0]  # time
            y = profiles[idx][1]  # distance
            in_data = in_data + [[x, y]]

    elif type_profile == 2:  # time - power
        for idx in idx_profile:
            x = profiles[idx][0]  # time
            y = profiles[idx][5]  # distance
            in_data = in_data + [[x, y]]

    plot_data(in_data)


def plot_data(in_data):  # in_data:  2 dim np array; x axis data : in_data[0]; y axis data:in_data[1]
    plt.figure(figsize=(16, 10))  # witdth:heigth = 16 : 10
    for d in in_data:
        plt.plot(d[0], d[1])
    # for i in range(np.shape(in_data)[0]):
    #    plt.plot(in_data[i][0], in_data[i][1])
    # plt.yscale(fig_perf['y_scale'])

    # font_title = {'fontsize': 18, 'fontweight': 'bold',
    #               'verticalalignment': 'baseline', 'horizontalalignment': 'center'}
    # plt.title(fig_perf['fig_title'], fontdict=font_title)
    font_title = {'fontsize': 18, 'fontweight': 'bold'}
    plt.title('data', loc='center', **font_title)

    font_axis = {'fontsize': 16, 'fontweight': 'bold'}
    plt.ylabel('y', loc='center', **font_axis)
    #        plt.yticks(fontdict = font_axis)
    plt.xlabel('x', loc='center', **font_axis)
    #        plt.xticks(fontdict = font_axis)
    plt.show()
    # plt.savefig('Training Convergence ' + self.train_method + '.pdf', format='pdf')
