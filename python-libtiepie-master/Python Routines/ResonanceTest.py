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

start = 5e3  # Sweep starting frequency in Hz
stop = 20e3  # Sweep stop frequency in Hz
points = 150  # Number of points for the sweep

ampIn = 2  # input amplitude in V
ampRange = 3  # oscillo amplitude in V

Lrec = 10000  # Recording length
Fs = 1e6  # Sampling freq

target = 12e3  # target resonance frequency in Hz
tolerance = 3e3  # tolerance for the past fail in Hz
