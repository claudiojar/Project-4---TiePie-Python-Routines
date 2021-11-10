# -*- coding: utf-8 -*-
"""
Created on Wednesday 10.11.2021 at 09:35

Miraex - TiePie Oscilloscope Control

@author: Claudio Jaramillo
"""

from __future__ import print_function
import time
import os
import sys
import libtiepie
from examples.printinfo import *


#%% Parameters
name = 'DM-0001_afterUV_drift' # Saving name
time = 1 # pause time to add between measurements (5.5 s min)  [s]
range = 4 # range in V (CAREFUL think about changing it !!!!)


#%%

MeanKulite=[]
DC2=[]
DC1=[]

timeline = []