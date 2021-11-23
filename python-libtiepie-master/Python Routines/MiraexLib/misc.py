# -*- coding: utf-8 -*-
"""
Created on Wednesday 16.11.2021 at 09:23

Miraex - Miscellaneous Routines

@author: Claudio Jaramillo
"""

import os
import datetime
import sys
import tkinter as tk
from tkinter import filedialog


def getParent(path, levels=1):
    """
    Fetches the parent(s) directory(ies) to the location passed in the path variable.

    param path : the path to which we want to find the parent directories.

    param levels (default = 1) : how many up levels we want to obtain parent directories from.
    """
    common = path

    # Using for loop for getting
    # starting point required for
    # os.path.relpath()
    for i in range(levels + 1):

        # Starting point
        common = os.path.dirname(common)

    # Parent directory upto specified
    # level
    return os.path.relpath(path, common)


def CreateFileName(ParentName: str, FileType='txt'):
    # File will be named with date in the name
    now = datetime.datetime.now()
    current_time_str = now.strftime("%m-%d-%Y_@_%H-%M-%S")

    # Complete file name
    file_name = ParentName+'__'+current_time_str+'.'+FileType

    return file_name


def CreateWriteDir(DataType: str):

    allowed_types = ['raw', 'figure']

    if DataType not in allowed_types:
        print('ERROR : DataType must be "raw" or "figure".')
        sys.exit(0)

    # Write directory within the repo
    if DataType == 'raw':
        writeDir_in_repo = '\\exports\\raw-data\\'
    elif DataType == 'figure':
        writeDir_in_repo = '\\exports\\figures\\'

    # Get repo path
    myPath = os.getcwd()
    print(myPath)
    writeDir = myPath + writeDir_in_repo
    print(f'{writeDir = } ')

    return writeDir


def OpenFileDialog():
    
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()

    return file_path
