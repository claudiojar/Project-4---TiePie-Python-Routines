# -*- coding: utf-8 -*-
"""
Created on Wednesday 10.11.2021 at 09:35

Miraex - Plot a graph from CSV file

@author: Claudio Jaramillo
"""

import numpy as np
import MiraexLib.plot as miraex_plt
import MiraexLib.misc as miraex_misc
from MiraexLib.printinfo import*

import csv
import pandas
import matplotlib.pyplot as plt


# %% Settings
name = '12KferruleH70e'
selected_file = miraex_misc.OpenFileDialog()

# We have to specify the header list names, because in the CSV file generated the actual column names are commented out with the # character.
# Ideally we would create a CSV file where the header name line is NOT a comment, thus remove the initial # char
header_list = ['timestamp', 'rms ch1', 'std ch1',
               'rms ch2', 'std ch2', 'sled power', 'sled power std']

my_data = pandas.read_csv(selected_file, engine='python',
                          sep=',', encoding='utf-8', comment='#', names=header_list)

# %% Plotting

plot_titles = ['Channel 1', 'Channel 2']
my_xlabel = 'Time'
my_global_title = 'RMS Voltage per Channel'

yData = [[my_data['rms ch1'][i] for i in range(len(my_data))],
         [my_data['rms ch2'][i] for i in range(len(my_data))]]
xData = [my_data['timestamp'][i] for i in range(len(my_data))]

# Define plot elements
my_fig, ax = plt.subplots(nrows=2, ncols=1)

# define how many ticks in the x axis we want to show
nb_x_ticks = 5
nb_x_ticks += 1

for nn, ax in enumerate(ax):

    # actual lines plotted
    ax.plot(xData, yData[nn], '-')

    ax.set_title(f'{plot_titles[nn]}')
    ax.grid(which='major')
    # ax.legend()
    start, end = ax.get_xlim()
    ax.xaxis.set_ticks(np.arange(start, end, (end-start)/nb_x_ticks))
    ax.set_ylabel('RMS Voltage')

my_fig.set_size_inches(20, 9, forward=True)
ax.set_xlabel(my_xlabel)
my_fig.supxlabel(my_global_title, fontsize=20)
plt.show()
