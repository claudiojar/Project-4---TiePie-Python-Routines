# -*- coding: utf-8 -*-
"""
Created on Wednesday 10.11.2021 at 09:35

Miraex - Plot a graph from CSV file

@author: Claudio Jaramillo
"""

import numpy as np
import MiraexLib.plot as miraex_plt
import MiraexLib.misc as miraex_misc
from MiraexLib.printinfo import*

import csv


# %% Settings
name = '12KferruleH70e'
file = miraex_misc.OpenFileDialog()
