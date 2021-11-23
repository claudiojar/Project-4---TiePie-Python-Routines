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


# %% Settings
name = 'wf9148x12KxXXXX'

# Parameters for the sweep over frequency
start = 5e3  # Sweep starting frequency in Hz
stop = 20e3  # Sweep stop frequency in Hz
points = 150  # Number of points for the sweep

ampIn = 2  # input amplitude in V
ampRange = 3  # oscillo amplitude in V

Lrec = 10000  # Recording length
Fs = 1e6  # Sampling freq

target = 12e3  # target resonance frequency in Hz
tolerance = 3e3  # tolerance for the past fail in Hz

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

# Sweep loop
for incre in range(points):
    freq = start + (stop - start)/(points-1)*(incre-1)
    v_freq.append(freq)

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
            print_device_info(scp)

            # Print generator info:
            print_device_info(gen)

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
        sys.exit(1)
