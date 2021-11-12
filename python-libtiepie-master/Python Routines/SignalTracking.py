# -*- coding: utf-8 -*-
"""
Created on Wednesday 10.11.2021 at 09:35

Miraex - TiePie Oscilloscope Control

@author: Claudio Jaramillo
"""

from __future__ import print_function
import time
import os
import sys
import libtiepie
from numpy.core.fromnumeric import shape
from printinfo import*

import numpy as np
import MiraexLib.plot as miraex_plt


# %% Functions
def myFunc():
    print('Function')


# %% Parameters to be set by user
myName = 'DM-0001_afterUV_drift'  # Saving name
myTime = 1  # pause time to add between measurements (5.5 s min)  [s]
myRange = 4  # range in V (CAREFUL think about changing it !!!!)

nb_of_chunks = 5

# %%

MeanKulite = []
DC2 = []
DC1 = []

timeline = []

# %% Data acquisition

# Print library info:
print_library_info()

# Enable network search:
libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()

# Try to open an oscilloscope with stream measurement support:
scp = None
for item in libtiepie.device_list:
    if item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE):
        scp = item.open_oscilloscope()
        if scp.measure_modes & libtiepie.MM_STREAM:
            break
        else:
            scp = None

if scp:
    try:
        # Set measure mode:
        scp.measure_mode = libtiepie.MM_STREAM

        # Set sample frequency:
        scp.sample_frequency = 1e3  # in Hz

        # Set record length:
        scp.record_length = 1000  # in s

        # For all channels:
        for ch in scp.channels:
            # Enable channel to measure it:
            ch.enabled = True

            # Set range:
            ch.range = myRange  # in Volts

            # Set coupling:
            ch.coupling = libtiepie.CK_DCV  # DC Volt

        # Print oscilloscope info:
        print_device_info(scp)

        # Start measurement:
        scp.start()

        csv_file = open(myName+'.csv', 'w')

        try:

            print('try')

            # Write csv header:
            csv_file.write('Sample')
            for i in range(len(scp.channels)):
                csv_file.write(';Ch' + str(i + 1))
            csv_file.write(os.linesep)

            # Measure nb_of_chunks chunks:
            sample = 0
            for chunk in range(nb_of_chunks):
                # Print a message, to inform the user that we still do something:
                print('Data chunk ' + str(chunk + 1))

                # Wait for measurement to complete:
                while not (scp.is_data_ready or scp.is_data_overflow):
                    time.sleep(0.01)  # 10 ms delay, to save CPU time

                if scp.is_data_overflow:
                    print('Data overflow!')
                    break

                # Get data:
                data = scp.get_data()

                """
                BEGIN DYNAMIC PLOT
                """
                print('hello')
                x_data = np.linspace(0, 1, len(data[0]))
                y_data = data[0]
                miraex_plt.DynamicPlot2(x_data, y_data, 'xlabel', 'ylabel', 'title')
                """
                END DYNAMIC PLOT
                """

                # Output CSV data:
                for i in range(len(data[0])):
                    csv_file.write(str(sample + i))
                    for j in range(len(data)):
                        csv_file.write(';' + str(data[j][i]))
                    csv_file.write(os.linesep)

                sample += len(data[0])

            print()
            print('Data written to: ' + csv_file.name)
        finally:
            csv_file.close()

        # Stop stream:
        scp.stop()

    except Exception as e:
        print('Exception')
        sys.exit(1)

    # Close oscilloscope:
    del scp

else:
    print('No oscilloscope available with stream measurement support!')
    sys.exit(1)

# %% Data processing and plotting

data_np = np.array(data)

miraex_plt.GenericPlot(np.linspace(0, 1, len(data_np[0])), data_np[0],
                       'Time', 'Voltage', 'TITLE', 'myLegend')

miraex_plt.ShowPlots()


# sys.exit(0)
