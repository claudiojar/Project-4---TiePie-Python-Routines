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

# %% Parameters

name = 'DM-0001-DC1_on_top '

# %% Settings ref perfect mirror
refCh = [2.340, 1.123]  # Signal with perfect mirror in V [Ch1 Ch2]

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
    kpz.set_max_voltage(150)
    kpz.enable_output()
    kpz.set_output_voltage(0)
    time.sleep(0.5)
    for v in np.linspace(0, 50, 50):
        kpz.set_output_voltage(v)
        time.sleep(0.1)
    kpz.set_output_voltage(0)
    kpz.disable_output()
"""

# set initial parameters sequentially
for kpz in cubinis:
    kpz.set_max_voltage(150)
    kpz.enable_output()
    kpz.set_output_voltage(20)


# %% TiePie initialization

# Print library info:
print_library_info()

# Enable network search:
libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()
