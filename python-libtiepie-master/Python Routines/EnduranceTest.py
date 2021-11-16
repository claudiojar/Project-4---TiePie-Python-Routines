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
import MiraexLib.plot as miraex_plt
from MiraexLib.printinfo import*


# %% Settings
name = 'EnduranceTest'

freq = 2100
TestDuration = 5  # Duration of the test in secs
MeasFreq = 1  # time interval between measurements (approximative)

Lrec = 10000  # Recording length
Fs = 1e6  # Sampling freq

ampIn = 12  # input amplitude in V
ampRange = 2  # oscilloscope amplitude in V


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

if gen:
    try:
        # Set signal type:
        gen.signal_type = libtiepie.ST_SINE

        # Set frequency:
        gen.frequency = freq  # in Hz

        # Set amplitude:
        gen.amplitude = ampIn  # in V

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


# %% Open scope and perform test

duration = 0

# creation of empty lists that will be modified in the loop
average_list = []
data_storage = []
processed_data = []
VAmpRMS = []
vDuration = []

my_time = time.time()
print(my_time)
while duration < TestDuration:

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

    np_data = np.array(data)  # numpy array
    average_list.append(np.mean(np_data))

    for data_point in np_data:
        processed_data.append((data_point - np.mean(data)))

    # print(processed_data)  # ??????

    '''
    Possible problem here because we are already computing the variance between the datapoints
    and the average of those datapoints. Yet we later take that data anc compute an RMS of it, which
    should yield the STD, but we are computing the STD of the STD ?

    MATLAB reference code lacks documentation, therefore we decide to use the STD of the data as a
    statistic metric and come back to it once the issue has been cleared.
    '''

    data_storage.append(processed_data)

    # Creation of lists to plot
    '''
    Possible confusion over statistics here in the reference MATLAB code ?
    '''
    AmpRMS = np.sqrt(np.mean((np.array(processed_data))**2))
    VAmpRMS.append(AmpRMS)
    VAmpRMS_np = np.array(VAmpRMS)

    # print(AmpRMS)
    # print(VAmpRMS)

    # duration before plotting, might be inaccurate to IRL !!!
    duration = time.time() - my_time  # secs

    # creation of duration array for plotting
    vDuration.append(duration)

    print(f'{len(vDuration) = }')
    print(f'{len(VAmpRMS) = }')

    # Plotting
    """Dynamic plotting every iteration of the while loop"""
    miraex_plt.DynamicPlot2(vDuration, (VAmpRMS_np*1000),
                            'xlabel', 'ylabel', 'title')

# Stop generator:
gen.stop()

# Disable output:
gen.output_on = False

# print(VAmpRMS)
print(len(data_storage))
print(f'{duration = } seconds')


# %% Post processing

vfour = []

for i in range(len(data_storage)):
    AmpRMS = np.sqrt(np.mean((np.array(processed_data))**2))
    VAmpRMS.append(AmpRMS)
    VAmpRMS_np = np.array(VAmpRMS)


# %%


# Keep the ShowPlots command at the end of the script !!!!!!
miraex_plt.ShowPlots()
