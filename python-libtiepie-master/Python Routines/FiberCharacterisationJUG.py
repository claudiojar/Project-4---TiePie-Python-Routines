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

# %% TiePie initialization

# Print library info:
print_library_info()

# Enable network search:
libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()
