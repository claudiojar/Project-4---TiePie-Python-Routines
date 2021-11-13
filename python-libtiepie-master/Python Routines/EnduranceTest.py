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
name = 'Debugging'

freq = 2100
TestDuration = 30 # Duration of the test in secs
MeasFreq = 1 # time interval between measurements (approximative)

Lrec = 10000 # Recording length
Fs = 1e6 # Sampling freq

ampIn = 12 # input amplitude in V
ampRange = 2 # oscilloscope amplitude in V


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

    except :
        print('Exception at Signal Generation')


# %% Endurance Test

duration = 0

my_time = time.time()
print(my_time)
while duration < TestDuration :
    #time.sleep(1)
    duration = time.time() - my_time #secs

    print(f'{duration = }')

