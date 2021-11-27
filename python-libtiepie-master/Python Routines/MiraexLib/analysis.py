# -*- coding: utf-8 -*-
"""
Created on 27.11.2021 at 10:24

Miraex - Data analysis Routines

@author: Claudio Jaramillo
"""

import numpy as np
from matplotlib import pyplot as mp
from numpy.core.fromnumeric import amax, argmax


def generate_peak(x, c):
    """[Generate a peak in some range of data x at point c]

    Args:
        x ([numpy array]): [range of data]
        c ([float]): [position of peak]

    Returns:
        [numpy array]: [generated data]
    """
    return np.exp(-np.power(x - c, 2) / 16.0)


def lin_interp(x, y, i, half):
    return x[i] + (x[i+1] - x[i]) * ((half - y[i]) / (y[i+1] - y[i]))


def half_max_x(x, y):
    half = max(y)/2.0
    print('half', half)
    signs = np.sign(np.add(y, -half))
    zero_crossings = (signs[0:-2] != signs[1:-1])
    zero_crossings_i = np.where(zero_crossings)[0]

    print('zero_crossings_i = ', zero_crossings_i)

    return [lin_interp(x, y, zero_crossings_i[0], half),
            lin_interp(x, y, zero_crossings_i[1], half)]


def find_max_peak(x):
    """Find maximum peak in a 1 dimensional x array

    Args:
        x (numpy array): array to find peak in

    Returns:
        tuple: maximum, index of maximum
    """

    np_x = x

    x_max = np.amax(np_x)
    index_max = np.argmax(np_x)

    return (x_max, index_max)


def find_min_peak(x):
    """Find minimum peak in a 1 dimensional x array

    Args:
        x (numpy array): array to find peak in

    Returns:
        tuple: minimum, index of minimum
    """

    np_x = x

    x_max = np.amin(np_x)
    index_max = np.argmin(np_x)

    return (x_max, index_max)


"""
# make some fake data
x = np.linspace(0, 20, 21)
y = generate_peak(x, 10)


# find the two crossing points
hmx = half_max_x(x, y)

# print the answer
fwhm = hmx[1] - hmx[0]
print("FWHM:{:.3f}".format(fwhm))

# a convincing plot
half = max(y)/2.0
"""
"""
mp.plot(x, y)
mp.plot(hmx, [half, half])
mp.show()
"""
