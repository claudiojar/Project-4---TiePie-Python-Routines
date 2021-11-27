# -*- coding: utf-8 -*-
"""
Created on Wednesday 10.11.2021 at 09:35

Miraex - Endurance Test for piezoelectric shaker

@author: Claudio Jaramillo
"""
from __future__ import print_function

import numpy as np
import MiraexLib.plot as miraex_plt
import MiraexLib.analysis as miraex_anls
import matplotlib.pyplot as plt

my_dir = "H:\\My Drive\\EPFL\\2. Master\\MA3 - 2021\\Semester Project - Miraex\\Project 4 - TiePie Python Routines\\exports\\raw-data\\"
name = "FrequencySweepTest1__ResonanceTest__11-24-2021_@_09-42-15.txt"
my_file = my_dir+name

# Opening data file to plot final data
result_file = open(my_file, "ab")
final_data = np.loadtxt(my_file)

print(final_data)

# Creating final data
final_data_tp = np.transpose(final_data)

# Plotting final data
start = 5e3  # Sweep starting frequency in Hz
stop = 20e3  # Sweep stop frequency in Hz
step = (stop-start)/len(final_data)

x_data = np.arange(start, stop, step)

# For each channel...
for i in range(len(final_data_tp)):

    # Create y data to plot per channel
    y_data = final_data_tp[i]

    # Find data maximum and minimum and index
    (my_max, my_max_index) = miraex_anls.find_max_peak(y_data)
    (my_min, my_min_index) = miraex_anls.find_min_peak(y_data)

    # Find and print the frequency at which the maximum appears
    resonance_frequency = x_data[my_max_index]
    print('Resonance Frequency : ', resonance_frequency)

    # We arbitrarily detect a noise only signal
    # We have to do this in order to avoind the FWHM function breaking when trying to compute the FWHM for a noise only signal.
    # This is kind of a hack
    if my_max-my_min < 1e-3:
        continue

    # find the two crossing points
    hmx = miraex_anls.half_max_x(x_data, y_data)

    # print the FWHM
    fwhm = hmx[1] - hmx[0]
    print("FWHM:{:.3f}".format(fwhm))

    # Find the Q-Factor
    q_factor = resonance_frequency/fwhm
    print('Q Factor : ', q_factor)

    # a convincing plot
    half = max(y_data)/2.0

    legend = 'Channel '+str(i+1)
    caption = f'Resonance frequency : {resonance_frequency/1000:.2f} kHz | Q Factor : {q_factor:.2f}'

    miraex_plt.GenericPlot(
        x_data, y_data, 'Frequency', 'RMS', name, legend, x_log=True, is_caption=True, my_caption=caption)
    plt.plot(hmx, [half, half])


# Keep the ShowPlots command at the end of the script !!!!!!
miraex_plt.ShowPlots()
result_file.close()
