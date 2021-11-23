# -*- coding: utf-8 -*-
"""
Created on Wednesday 10.11.2021 at 09:35

Miraex - Endurance Test for piezoelectric shaker

@author: Claudio Jaramillo
"""

from __future__ import print_function
import sys
import os
from typing import final
import libtiepie
import time
import datetime

import numpy as np
import MiraexLib.plot as miraex_plt
import MiraexLib.misc as miraex_misc
from MiraexLib.printinfo import*

# %% Magic numbers and setup
_seconds = 1
_minutes = _seconds*60
_hours = _minutes*60
_days = _hours*24

'''
myDays = input('Test duration : days ? ')
myHours = input('Test duration : hours ? ')
myMinutes = input('Test duration : minutes ? ')
mySeconds = input('Test duration : seconds ? ')
'''

nb_of_graphs_to_show = int(input(
    'For how many epochs would you like to show the dynamic plot ? '))

# %% Settings
freq = 2e3

TestLoopDuration = 10*_seconds  # Duration of the test loop
TestTotalDuration = 0*_days + 1*_minutes  # Duration of the entire test

if TestTotalDuration <= TestLoopDuration:
    print('ERROR')
    print('The total test duration MUST be larger than the loop duration.')
    sys.exit(1)

MeasFreq = 1  # time interval between measurements (approximative)

Lrec = 100  # Recording length : the number of samples that will be taken per loop, default = 10000
Fs = 200e3  # Sampling freq

ampOut = 1  # input amplitude in V
ampRange = 4  # oscilloscope amplitude in V

# %% Setting up result file
# Create file_name
name = 'EnduranceTest'
file_name = miraex_misc.CreateFileName(name, 'txt')
writeDir_func = miraex_misc.CreateWriteDir('raw')

# Open the text file to write the results
result_file = open(writeDir_func+file_name, "ab")
print(result_file)

result_file.truncate(0)

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
'''

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

# %% Perform test

# Setting starting counters
total_duration = 0
epoch_counter = 0

# Setting starting time
total_start_time = time.time()
print('Starting time : ', total_start_time)

# outer loop
while total_duration < TestTotalDuration:

    # Computing the number of epochs
    epoch_counter += 1
    print('Begin of epoch ', epoch_counter)

    # creation of empty lists and variables that will be modified in the inner loop and need to be reset at each outer loop
    loop_counter = 0
    loop_duration = 0
    loop_start_time = time.time()

    average_list = []
    data_no_offset = []
    Vect_AmpRMS = []
    Vect_Duration = []

    print(f'{loop_duration = }')
    print(f'{TestLoopDuration = }')
    # Inner loop
    while loop_duration < TestLoopDuration:

        # Counting the number of loops
        print('--------------------------')
        loop_counter += 1
        print('Begin of inner loop : ', loop_counter)

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
                '''

                # Locate trigger input:
                # or TIID_GENERATOR_START or TIID_GENERATOR_STOP
                trigger_input = scp.trigger_inputs.get_by_id(
                    libtiepie.TIID_GENERATOR_NEW_PERIOD)

                if trigger_input is None:
                    raise Exception('Unknown trigger input!')

                # Enable trigger input:
                trigger_input.enabled = True

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
        #print(f'{np_data.shape = }')

        # average value of the data fetched during 1 loop per channel
        # The first index is the iteration index
        # The second index is the avg for channel index
        average_list.append([np.mean(np_data[i]) for i in range(len(np_data))])

        # Substract the mean of np_data to each element of np_data during 1 loop
        '''
        Processed data will have n number of elements, each has nb_of_channels sub-dimensions that represent the nb of channels that we are working with in the oscilloscope.

        The number of elements n is the number of iterations of the loop. It increases as the test time increases.
        '''
        # By substracting the mean we remove the DC offset for each channel
        data_no_offset.append(
            [np_data[i] - average_list[loop_counter-1][i] for i in range(len(np_data))])

        del np_data

        '''
        print('data_no_offset')
        print(data_no_offset)
        print('processed data shape = ', np.array(data_no_offset).shape)
        '''

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

        # Creation of lists to plot
        '''
        Possible confusion over statistics here in the reference MATLAB code ?

        Here we diverge from the ref. MATLAB file. We will compute the RMS value of the channels 1 and 2 overone acquisition period and write it to a JSON file. We will also plot the RMS values of channels 1 and 2 over that acquisition in order to verify the intergrity of the data and then we simply dump the plot.
        '''
        # RMS of the data fetched in 1 loop iteration, for each channel
        AmpRMS = [np.sqrt(np.mean((np.array(data_no_offset[loop_counter-1][i]))**2))
                  for i in range(len(data_no_offset[loop_counter-1]))]

        # Create a vector with all the RMS values of all loops, updates each loop
        Vect_AmpRMS.append(AmpRMS)
        Vect_AmpRMS_np = np.array(Vect_AmpRMS)

        # Create a Channel first array of RMS values for plotting and better addressing of the data
        Channel_AmpRMS = np.transpose(Vect_AmpRMS_np)

        # Printing data for verification
        '''
        print('Iteration RMS values : ')
        print(Vect_AmpRMS_np)

        print('Channel RMS values : ')
        print(Channel_AmpRMS)
        '''

        # duration before plotting, might be inaccurate to IRL !!!
        loop_duration = time.time() - loop_start_time  # secs

        # creation of duration array for plotting
        Vect_Duration.append(loop_duration)

        # Plotting
        """Dynamic plotting every iteration of the while loop"""
        if nb_of_graphs_to_show >= epoch_counter:
            for i in range(len(Channel_AmpRMS)):
                miraex_plt.DynamicPlot2(Vect_Duration, (Channel_AmpRMS[i]),
                                        'Duration [s]', 'RMS', 'Dynamic Endurance Test')

        else:
            miraex_plt.CloseAllPlots()

        print('End of inner loop ', loop_counter)

    # Writing of RMS values at the end of each EPOCH, the data we write contains all the RMS values for all the loops contained within one epoch

    # f.write(b"\n")
    # In the resulting file each column represents one channel
    np.savetxt(result_file, Vect_AmpRMS_np)

    total_duration = time.time() - total_start_time
    print('END OF EPOCH', epoch_counter)
    print('--------------------------')

'''
REMOVE COMMENT FOR HS3
'''
# Stop generator:
gen.stop()

# Disable output:
gen.output_on = False


# print(VAmpRMS)
print(f'{total_duration = } seconds')

# Don't forget to close the file !
result_file.close()

# %% Post processing
# Required time to write the data !
time.sleep(1)

# Opening data file to plot final data
result_file = open(writeDir_func+file_name, "ab")
final_data = np.loadtxt(writeDir_func+file_name)

# Creating final data
final_data_tp = np.transpose(final_data)

# Plotting final data
x_data = np.arange(final_data_tp.shape[1])

for i in range(len(final_data_tp)):

    legend = 'Channel '+str(i+1)
    miraex_plt.GenericPlot(
        x_data, final_data_tp[i], 'Time', 'RMS', file_name, legend)

# Keep the ShowPlots command at the end of the script !!!!!!
miraex_plt.ShowPlots()
result_file.close()
