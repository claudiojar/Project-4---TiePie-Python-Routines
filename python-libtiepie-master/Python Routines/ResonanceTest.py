# -*- coding: utf-8 -*-
"""
Created on Wednesday 20.11.2021 at 10:44

Miraex - Resonance Test for piezoelectric shaker

@author: Claudio Jaramillo
"""

from __future__ import print_function
import libtiepie
import time
import matplotlib.pyplot as plt

import numpy as np
import MiraexLib.plot as miraex_plt
import MiraexLib.misc as miraex_misc
import MiraexLib.analysis as miraex_anls
from MiraexLib.printinfo import*


# %% Settings
name = input('Name for the file : ')

# Parameters for the sweep over frequency
start = 5e3  # Sweep starting frequency in Hz
stop = 20e3  # Sweep stop frequency in Hz
points = 150  # Number of points for the sweep

ampIn = 2  # input amplitude in V
ampRange = 3  # oscillo amplitude in V

Lrec = 10000  # Recording length for a data point
Fs = 1e6  # Sampling freq

target = 12e3  # target resonance frequency in Hz
tolerance = 3e3  # tolerance for the past fail in Hz

# %% Setting up result file
# Create file_name
name += 'ResonanceTest'
file_name = miraex_misc.CreateFileName(name, 'txt')
writeDir_func = miraex_misc.CreateWriteDir('raw')

# Open the text file to write the results
result_file = open(writeDir_func+file_name, "ab")
print(result_file)

result_file.truncate(0)

nb_of_points_to_show = int(input(
    'For how many iterations would you like to show the dynamic plot ? '))

# %% Opening devices and setting up devices

# Print library info:
print_library_info()

# Enable network search:
libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()

# Parameters and lists that will be modified during the loop
# voltage amplitude RMS
v_amplitude_rms = []

# average signal value
average_signal = []

# Storage list
Data_Storage = []

# voltage at frequency
v_freq = []

# generator frequency
v_gen_freq = []

# Data with a removed DC component
data_no_offset = []

# Sweep loop
for incre in range(points):
    freq = start + (stop - start)/(points-1)*(incre-1)
    v_freq.append(freq)
    print('--------------')
    print('Current frequency : ', freq)

    # Try to open an oscilloscope with block measurement support and a generator in the same device:
    scp = None
    gen = None
    for item in libtiepie.device_list:
        if (item.can_open(libtiepie.DEVICETYPE_OSCILLOSCOPE)) and (item.can_open(libtiepie.DEVICETYPE_GENERATOR)):
            scp = item.open_oscilloscope()
            if scp.measure_modes & libtiepie.MM_BLOCK:
                gen = item.open_generator()
                break
            else:
                scp = None

    # Oscilloscope settings:
    # Set measure mode:
    scp.measure_mode = libtiepie.MM_BLOCK

    # Set sample frequency:
    scp.sample_frequency = Fs  # 1 MHz

    # Set record length:
    scp.record_length = Lrec  # 10000 samples

    # Set pre sample ratio:
    scp.pre_sample_ratio = 0  # 0 %

    # For all channels:
    for ch in scp.channels:
        # Enable channel to measure it:
        ch.enabled = True

        # Set range:
        ch.range = ampRange  # 8 V

        # Set coupling:
        ch.coupling = libtiepie.CK_DCV  # DC Volt

    # Set trigger timeout:
    scp.trigger_time_out = 1  # 1 s

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

    # Generator settings:

    # Set signal type:
    gen.signal_type = libtiepie.ST_SINE

    # Set frequency:
    gen.frequency = freq  # in Hz

    # Set amplitude:
    gen.amplitude = ampIn  # in V

    # Set offset:
    gen.offset = 0  # 0 V

    # Enable output:
    gen.output_on = True

    # Print oscilloscope info:
    # print_device_info(scp)

    # Print generator info:
    # print_device_info(gen)

    # Get information about the frequency
    v_gen_freq.append(gen.frequency)

    # Start measurement:
    scp.start()

    # Start signal generation:
    gen.start()

    # Wait for measurement to complete:
    while not scp.is_data_ready:
        time.sleep(0.01)  # 10 ms delay, to save CPU time

    # Stop generator:
    gen.stop()

    # Disable output:
    gen.output_on = False

    # Get data:
    data = scp.get_data()

    # Data processing

    # print(f'{data = }')
    # np_data will be rewritten at every loop iteration
    # np_data[nb of channels of the scope][nb of samples in channel]

    np_data = np.array(data)  # numpy array
    #print(f'{np_data.shape = }')

    # average value of the data fetched during 1 loop per channel
    # The first index is the iteration index
    # The second index is the avg for channel index
    average_signal.append([np.mean(np_data[i])
                           for i in range(len(np_data))])

    # Substract the mean of np_data to each element of np_data during 1 loop
    '''
    Processed data will have n number of elements, each has nb_of_channels sub-dimensions that represent the nb of channels that we are working with in the oscilloscope.

    The number of elements n is the number of iterations of the loop. It increases as the test time increases.
    '''
    # By substracting the mean we remove the DC offset for each channel
    data_no_offset.append(
        [np_data[i] - average_signal[incre-1][i] for i in range(len(np_data))])

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
    # Output CSV data:
    csv_file = open('OscilloscopeGeneratorTrigger.csv', 'w')
    try:
        csv_file.write('Sample')
        for i in range(len(data)):
            csv_file.write(';Ch' + str(i + 1))
        csv_file.write(os.linesep)
        for i in range(len(data[0])):
            csv_file.write(str(i))
            for j in range(len(data)):
                csv_file.write(';' + str(data[j][i]))
            csv_file.write(os.linesep)

        print()
        print('Data written to: ' + csv_file.name)

    finally:
        csv_file.close()
    '''

    # Close oscilloscope:
    del scp

    # Close generator:
    del gen

    # ---------------------------------------------------------------------------------------------
    # DATA POST PROCESSING
    # ---------------------------------------------------------------------------------------------

    Data_Storage.append(data)

    # RMS of the data fetched in 1 loop iteration, for each channel
    Amplitude_RMS = [np.sqrt(np.mean((np.array(data_no_offset[incre-1][i]))**2))
                     for i in range(len(data_no_offset[incre-1]))]

    v_amplitude_rms.append(Amplitude_RMS)
    v_amplitude_rms_np = np.array(v_amplitude_rms)

    # Create a Channel first array of RMS values for plotting and better addressing of the data
    channel_amp_rms = np.transpose(v_amplitude_rms_np)

    '''
    print('Amplitude RMS')
    print(Amplitude_RMS)

    print('v_amplitude_rms')
    print(v_amplitude_rms)
    '''

    x_data = v_gen_freq

    # y_data contains the RMS for iteration for each channel : y_data[iteration][channel]
    # In this case channel 0 is the measurement of amplitude of oscillation
    y_data = [v_amplitude_rms[i][0]*1000 for i in range(len(v_amplitude_rms))]
    print('Current RMS [mV] : ', v_amplitude_rms[incre][0]*1000)

    '''
    print('xdata')
    print(x_data)

    print('ydata')
    print(y_data)
    '''

    if incre < nb_of_points_to_show:
        # Dynamic plotting
        for i in range(len(channel_amp_rms)):
            miraex_plt.DynamicPlot2(v_gen_freq, (channel_amp_rms[i])*1000,
                                    'Frequency [Hz]', 'Oscillation Amplitude RMS [mV]', 'Dynamic Resonance Test', True)

    else:
        miraex_plt.CloseAllPlots()

# In the resulting file each column represents one channel
np.savetxt(result_file, v_amplitude_rms_np)
result_file.close()

time.sleep(1)

# Opening data file to plot final data
result_file = open(writeDir_func+file_name, "ab")
final_data = np.loadtxt(writeDir_func+file_name)

# Creating final data
final_data_tp = np.transpose(final_data)

# Plotting final data
x_data = np.array(v_gen_freq)
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
    # We have to do this in order to avoind the FWHM detecting function breaking when trying to compute the FWHM for a noise only signal.
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
