# -*- coding: utf-8 -*-
"""
Created on Sunday 28.11.2021 at 14:09

Miraex - Fiber characterization routine

@author: Claudio Jaramillo
"""

from __future__ import print_function
import libtiepie
import time
import matplotlib.pyplot as plt
import os
import sys

import numpy as np
import MiraexLib.plot as miraex_plt
import MiraexLib.misc as miraex_misc
import MiraexLib.analysis as miraex_anls
from MiraexLib.printinfo import*

from cubini.KPZ101 import KPZ101

"""
IMPORTANT DOCUMENTATION :

This script depends on the [Cubini library](https://github.com/Schlabonski/cubini).

To install follow the steps in the READ ME of the repo.

If the line :

    python3 setup.py install

fails, try using :

    python setup.py install

For this script to work properly, the libraries :
 - PyUSB
 - LibUSB

Need to be installed.

Install them both first by using :

    conda install -c conda-forge pyusb
    conda install -c conda-forge libusb

from the anaconda cmd line after having activated the relevant environment.

> Environment Miraex_2021_12_01 is the earliest to have this dependency installed.

Then, go to : https://github.com/libusb/libusb/releases/tag/v1.0.24

Download the zip file, and open it.

Unzip using 7zip into a temp dir.

If on 64-bit Windows, copy

    MinGW64\dll\libusb-1.0.dll

into

    C:\windows\system32

If on 32-bit windows, copy

    MinGW32\dll\libusb-1.0.dll

into

    C:\windows\SysWOW64.

This should solve the ''No backend available'' exepction raised at init of the cuboids.

Warning : use the set_max_voltage method before the set_output_voltage method to avoid crashes.
"""

# %% Generic parameters

name = 'DM-0001-DC1_on_top '

# %% Cuboid parameters

V_max = 75  # 75 V maximum voltage
V_default = 20  # V default voltage

# %% Settings ref perfect mirror
refCh = [2.340, 1.123]  # Signal with perfect mirror in V [Ch1 Ch2], reference

# %% Settings for oscilloscope
Lrec = 10000  # Recording length
Fs = 1e6  # Sampling freq

ampRange = 4  # Oscilloscope amplitude in V

# make h a global variable so it can be used outside the main function. Useful when you do event handling and sequential move
global h

# %% Initialization

# list of serial numbers
cuboids = [29250837]

# connect to all modules
cubinis = []

print('here')

for sn in cuboids:
    # try:
    cubini = KPZ101(serial_number=sn)
    time.sleep(0.1)
    cubini.set_input_mode()
    cubinis.append(cubini)
    print('KPZ101 {} found.'.format(sn))

"""
    except Exception as e:
        print(e)
        print('KPZ101 {} not found.'.format(sn))
"""
"""
# sequentially run a test sequence for each cube
for kpz in cubinis:
    kpz.set_max_voltage(V_max)
    kpz.enable_output()
    kpz.set_output_voltage(0)
    time.sleep(0.5)
    for v in np.linspace(0, 50, 25):
        kpz.set_output_voltage(v)
        time.sleep(0.1)
    kpz.set_output_voltage(0)
    kpz.disable_output()
"""


# set initial parameters sequentially
for kpz in cubinis:
    kpz.set_max_voltage(V_max)
    kpz.enable_output()
    kpz.set_output_voltage(V_default)


# %% TiePie initialization

# Print library info:
print_library_info()

# Enable network search:
libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()

# %% Parameter set before code

Vvolt = []  # Volt vector

average_list = []
Vect_AmpRMS = []
data_no_offset = []

# Set acquire
samplerate = 1
bufferdelay = 0.1
df = (1.25*(10**6))

dt = 1/df

iitotal = 20

# %% Main loop

for ii in range(1, 1, 1):  # start, stop, step
    trigger = 0
    voltstop = 0
    hystTest = np.arange(3, 65, 1)

    for tt in hystTest:
        print('hello world')

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

        if scp and gen:
            try:
                # Oscilloscope settings:

                # Set measure mode:
                scp.measure_mode = libtiepie.MM_BLOCK

                # Set sample frequency:
                scp.sample_frequency = Fs  # Hz

                # Set record length:
                scp.record_length = Lrec  # nb of samples

                # Set pre sample ratio:
                scp.pre_sample_ratio = 0  # 0 %

                # For all channels:
                for ch in scp.channels:
                    # Enable channel to measure it:
                    ch.enabled = True

                    # Set range:
                    ch.range = ampRange  # V

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
                gen.frequency = 1e3  # 1 kHz

                # Set amplitude:
                gen.amplitude = 2  # 2 V

                # Set offset:
                gen.offset = 0  # 0 V

                # Enable output:
                gen.output_on = True

                # Print oscilloscope info:
                print_device_info(scp)

                # Print generator info:
                print_device_info(gen)

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
                np_data = np.array(data)  # numpy array
                #print(f'{np_data.shape = }')

                # average value of the data fetched during 1 loop per channel
                # The first index is the iteration index
                # The second index is the avg for channel index
                average_list.append([np.mean(np_data[i])
                                    for i in range(len(np_data))])

                # Substract the mean of np_data to each element of np_data during 1 loop
                '''
                Processed data will have n number of elements, each has nb_of_channels sub-dimensions that represent the nb of channels that we are working with in the oscilloscope.

                The number of elements n is the number of iterations of the loop. It increases as the test time increases.
                '''
                # By substracting the mean we remove the DC offset for each channel
                data_no_offset.append([np_data[i] - average_list[i]
                                      for i in range(len(np_data))])

                del np_data

                # Get all channel data value ranges (which are compensated for probe gain/offset)
                data_range_min_max = []
                for channel in scp.channels:
                    data_range_min_max.append(
                        [channel._get_data_value_min(), channel._get_data_value_max()])

                # Creation of lists to plot
                # RMS of the data fetched in 1 loop iteration, for each channel
                AmpRMS = [np.sqrt(np.mean((np.array(data_no_offset[i]))**2))
                          for i in range(len(data_no_offset))]

                # Create a vector with all the RMS values of all loops, updates each loop
                Vect_AmpRMS.append(AmpRMS)
                Vect_AmpRMS_np = np.array(Vect_AmpRMS)

                # Create a Channel first array of RMS values for plotting and better addressing of the data
                Channel_AmpRMS = np.transpose(Vect_AmpRMS_np)

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

            except Exception as e:
                print('Exception: ' + e.message)
                sys.exit(1)

            # Close oscilloscope:
            del scp

            # Close generator:
            del gen

        else:
            print('No oscilloscope available with block measurement support or generator available in the same unit!')

        for i in range(len(average_list)):
            miraex_plt.DynamicPlot2(Vvolt, average_list[i],
                                    'Duration [s]', 'RMS', 'Test')


# Reset cuboids to default parameters
for kpz in cubinis:
    kpz.set_max_voltage(V_max)
    kpz.enable_output()
    kpz.set_output_voltage(V_default)
