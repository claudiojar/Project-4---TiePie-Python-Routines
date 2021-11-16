# -*- coding: utf-8 -*-
"""
Created on Wednesday 10.11.2021 at 09:35

Miraex - Endurance Test for piezoelectric shaker

@author: Claudio Jaramillo
"""

from __future__ import print_function
import sys
import libtiepie
import time

import numpy as np
from numpy.lib.function_base import average
import MiraexLib.plot as miraex_plt
from MiraexLib.printinfo import*
from MiraexLib.misc import fprint


# %% Settings
name = 'EnduranceTest'

freq = 2e3
TestDuration = 2  # Duration of the test in secs
MeasFreq = 1  # time interval between measurements (approximative)

Lrec = 5  # Recording length : the number of samples that will be taken per loop, default = 10000
Fs = 200e3  # Sampling freq

ampOut = 1  # input amplitude in V
ampRange = 4  # oscilloscope amplitude in V


# %% Opening devices and setting up devices

# Print library info:
print_library_info()

# Enable network search:
libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()

# Try to open a generator:
gen = None
for item in libtiepie.device_list:
    if item.can_open(libtiepie.DEVICETYPE_GENERATOR):
        gen = item.open_generator()
        if gen:
            break

'''
REMOVE COMMENTS FOR HS3

if gen:
    try:
        # Set signal type:
        gen.signal_type = libtiepie.ST_SINE

        # Set frequency:
        gen.frequency = freq  # in Hz

        # Set amplitude:
        gen.amplitude = ampOut  # in V

        # Set offset:
        gen.offset = 0  # in V

        # Enable output:
        gen.output_on = True

        # Print generator info:
        print_device_info(gen)

        # Start signal generation:
        gen.start()

    except:
        print('Exception at Signal Generation')
'''

# %% Open scope and perform test

duration = 0
counter = 0

# creation of empty lists that will be modified in the loop
average_list = []
data_storage = []
processed_data = []
Vect_AmpRMS = []
Vect_Duration = []

my_time = time.time()
print(my_time)
while duration < TestDuration:

    print('--------------------------')
    # Try to open an oscilloscope with block measurement support:
    scp = None
    for item in libtiepie.device_list:
        if item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE):
            scp = item.open_oscilloscope()
            if scp.measure_modes & libtiepie.MM_BLOCK:
                break
            else:
                scp = None

    if scp:
        try:
            # Set measure mode:
            scp.measure_mode = libtiepie.MM_BLOCK

            # Set sample frequency:
            scp.sample_frequency = Fs  # in Hz

            # Set record length:
            scp.record_length = Lrec  # nb of samples

            # Set pre sample ratio:
            scp.pre_sample_ratio = 0  # 0 %

            # For all channels:
            for ch in scp.channels:
                # Enable channel to measure it:
                ch.enabled = True

                # Set range:
                ch.range = ampRange  # in V

                # Set coupling:
                ch.coupling = libtiepie.CK_DCV  # DC Volt

            # Set trigger timeout:
            scp.trigger_time_out = 1  # in secs

            # Disable all channel trigger sources:
            for ch in scp.channels:
                ch.trigger.enabled = False

            '''
            REMOVE COMMENT FOR HS3

            # Locate trigger input:
            # or TIID_GENERATOR_START or TIID_GENERATOR_STOP
            trigger_input = scp.trigger_inputs.get_by_id(
                libtiepie.TIID_GENERATOR_NEW_PERIOD)

            if trigger_input is None:
                raise Exception('Unknown trigger input!')

            # Enable trigger input:
            trigger_input.enabled = True
            '''

            # Print oscilloscope info (optional):
            # print_device_info(scp)

            # Start measurement:
            scp.start()

            # Wait for measurement to complete:
            while not scp.is_data_ready:
                time.sleep(0.01)  # 10 ms delay, to save CPU time

            # Get data:
            data = scp.get_data()

        except:
            print('Error at Scope Generation')

    # Data processing

    # print(f'{data = }')
    # np_data will be rewritten at every loop iteration
    # np_data[nb of channels of the scope][nb of samples in channel]

    np_data = np.array(data)  # numpy array
    print(f'{np_data.shape = }')

    np_data = np.array([[1, 1, 3, 3, 3],
                        [2, 2, 2, 2, 2],
                        [3, 3, 3, 3, 3],
                        [4, 4, 4, 4, 4]])

    print(f'{np_data.shape = }')
    print(np_data[0])

    # average value of the data fetched during 1 loop per channel
    # The first index is the iteration index
    # The second index is the avg for channel index
    average_list.append([np.mean(np_data[0])])
    print(f'{average_list = }')

    # Substract the mean of np_data to each element of np_data during 1 loop
    '''
    Processed data will have n number of elements, each has nb_of_channels sub-dimensions that represent the nb of channels that we are working with in the oscilloscope.

    The number of elements n is the number of iterations of the loop. It increases as the test time increases.
    '''
    # By substracting the mean we remove the DC offset
    processed_data.append(np_data - np.mean(np_data))
    print('processed data shape = ', np.array(processed_data).shape)

    # Get all channel data value ranges (which are compensated for probe gain/offset)
    data_range_min_max = []
    for channel in scp.channels:
        data_range_min_max.append(
            [channel._get_data_value_min(), channel._get_data_value_max()])

    '''
    COMMENT DEPRECATED, BUT LEAVING IT HERE JUST IN CASE. SAFE TO IGNORE.

    Possible problem here because we are already computing the variance between the datapoints
    and the average of those datapoints. Yet we later take that data anc compute an RMS of it, which
    should yield the STD, but we are computing the STD of the STD ?

    MATLAB reference code lacks documentation, therefore we decide to use the STD of the data as a
    statistic metric and come back to it once the issue has been cleared.
    '''
    data_storage = (processed_data)

    # Creation of lists to plot
    '''
    Possible confusion over statistics here in the reference MATLAB code ?
    '''

    '''
    Here we diverge from the ref. MATLAB file. We will compute the RMS value of the channels 1 and 2 overone acquisition period and write it to a JSON file. We will also plot the RMS values of channels 1 and 2 over that acquisition in order to verify the intergrity of the data and then we simply dump the plot.
    '''
    # RMS of the data fetched in 1 loop iteration, for each channel
    AmpRMS = [np.sqrt(np.mean((np.array(processed_data[i]))**2))
              for i in range(len(processed_data))]

    print(f'{AmpRMS = }')

    # Create a vector with all the RMS values of all loops, updates each loop
    Vect_AmpRMS.append(AmpRMS)
    Vect_AmpRMS_np = np.array(Vect_AmpRMS)
    print(f'{Vect_AmpRMS_np.shape = }')

    # duration before plotting, might be inaccurate to IRL !!!
    duration = time.time() - my_time  # secs

    # creation of duration array for plotting
    Vect_Duration.append(duration)

    print(f'{(Vect_Duration) = }')
    print(f'{(Vect_AmpRMS_np) = }')

    counter += 1
    print(f'{counter = }')
    # Plotting
    """Dynamic plotting every iteration of the while loop"""
    # for i in range(len())

    miraex_plt.DynamicPlot2(Vect_Duration, (Vect_AmpRMS_np[0]*1000),
                            'Duration [s]', 'RMS (x1000)', 'Dynamic Endurance Test')

print('--------------------------')
'''
REMOVE COMMENT FOR HS3

# Stop generator:
gen.stop()

# Disable output:
gen.output_on = False
'''

# print(VAmpRMS)
print(len(data_storage))
print(f'{duration = } seconds')


# %% Post processing

vfour = []

for i in range(len(data_storage)):
    pass
# %%

# Keep the ShowPlots command at the end of the script !!!!!!

# miraex_plt.ShowPlots()
