import numpy as np


def quadreg(x, y, t, day):
    """ Function for performing quadratic regression on LiDAR data. """
    if len(x) > 0:
        try:
            xnum = (x - (t - day).total_seconds()) / 3600
        except TypeError:
            xnum = (x - t).total_seconds() / 3600
        p = np.polyfit(xnum, y, 2)
        b_0, b_1, b_2 = p[2], p[1], p[0]
        return b_0
    else:
        return float('nan')


def linreg(x, y, t, day):
    """ Function for performing linear regression on LiDAR data. """
    if len(x) > 0:
        try:
            xnum = (x - (t - day).total_seconds()) / 3600
        except TypeError:
            xnum = (x - t).total_seconds() / 3600
        p = np.polyfit(xnum, y, 1)
        b_0, b_1 = p[1], p[0]
        return b_0
    else:
        return float('nan')
